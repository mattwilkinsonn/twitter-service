# read_s3.py
import boto3
from pydantic import BaseSettings
import logging
import sentry_sdk
from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
from requests_aws4auth import AWS4Auth
from io import BytesIO
import gzip
import json
import dateutil.parser
from time import sleep
from elasticsearch_dsl import Search
from pprint import pprint


class Settings(BaseSettings):

    AWS_REGION: str
    STORAGE_BUCKET: str
    ENV: str
    ES_HOST: str
    SENTRY_DSN: str
    LOGGING_LEVEL: str

    class Config:
        env_file = ".env"
        env_prefix = ""
        allow_mutation = False
        case_sensitive: True


settings = Settings()

if settings.LOGGING_LEVEL == "INFO":
    logging.basicConfig(level=logging.INFO)
if settings.LOGGING_LEVEL == "WARNING":
    logging.basicConfig(level=logging.WARNING)

# Start sentry
sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENV)

credentials = boto3.Session().get_credentials()


BUCKET = "protag-au-twitter"
s3 = boto3.client("s3")
s3_resource = boto3.resource("s3")

awsauth = AWS4Auth(
    credentials.access_key, credentials.secret_key, settings.AWS_REGION, "es"
)


def get_es():
    # init elasticsearch
    if settings.ENV != "local":
        # ES for AWS needs these credentials,
        return Elasticsearch(
            hosts=[{"host": settings.ES_HOST, "port": 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
        )
    elif settings.ENV == "local":
        # this is designed to run locally within docker container
        return Elasticsearch(hosts="http://elasticsearch:9200")


es = get_es()

# reliable solution, newest tweet will always have the last key
# all tweets get sent together so any one key in ES means
# that all of the tweets from that key are in ES
newestDoc = (
    Search(using=es, index="tweets-*")
    .sort({"created_at": {"order": "desc"}})
    .execute()[0]
)
lastKey = newestDoc["s3_file_path"]


while True:
    s3ObjectList = s3.list_objects_v2(
        Bucket=BUCKET,
        EncodingType="url",
        MaxKeys=1000,
        Prefix="tweets",
        StartAfter=lastKey,
    )

    # kinda janky solution, should be a better way to do this
    # events would make a lot more sense but need to look into how to set those up
    if s3ObjectList["KeyCount"] <= 0:
        sleep(3600)
        continue

    # for each item in response, get the s3 file, decode, send to ES
    for s3Object in s3ObjectList["Contents"]:
        if s3Object["Size"] <= 0:
            continue
        # clear tweets list to take next file
        tweets = []

        # considered using S3 Select here but got some weird errors
        # buf = s3.get_object(Bucket=BUCKET, Key=s3Object["Key"])["Body"].read()
        obj = s3_resource.Object(BUCKET, s3Object["Key"])
        for line in gzip.GzipFile(fileobj=obj.get()["Body"]):
            line = line.decode("utf-8")

            jsonObj = json.loads(line)
            if (
                jsonObj["quote_count"] != 0
                or jsonObj["reply_count"] != 0
                or jsonObj["retweet_count"] != 0
                or jsonObj["favorite_count"] != 0
            ):
                pprint(jsonObj)
                print(0)

        for line in gzip.read(obj):
            line = line.decode("utf-8")
            tweet = json.loads(line)

            if "delete" in tweet or "status_withheld" in tweet:
                continue

            print(tweet["favorite_count"])

            # this gets rid of a lot of tweets, most don't have external links
            urlLength = len(tweet["entities"]["urls"])
            if (
                urlLength == 0
                or urlLength == 1
                and "twitter.com" in tweet["entities"]["urls"][0]["expanded_url"]
            ):
                continue

            # makes url more easily queryable, regular url is shortened
            expandedUrls = []
            for url in tweet["entities"]["urls"]:
                if "twitter.com" in url["expanded_url"]:
                    continue
                expandedUrls.append(url["expanded_url"])

            # extended (longer) tweets have a different text location for some reason
            if "extended_tweet" in tweet:
                text = tweet["extended_tweet"]["full_text"]
            else:
                text = tweet["text"]

            # outputs epoch seconds, ES can read without any weird configs
            created_at_epoch = int(
                dateutil.parser.parse(tweet["created_at"]).timestamp()
            )

            # tweet schema
            esTweet = {
                "created_at": created_at_epoch,
                "urls": expandedUrls,
                "text": text,
                "favorite_count": tweet["favorite_count"],
                "_id": tweet["id_str"],
                "user-screen_name": tweet["user"]["screen_name"],
                "quote_count": tweet["quote_count"],
                "reply_count": tweet["reply_count"],
                "retweet_count": tweet["retweet_count"],
                "lang": tweet["lang"],
                "s3_file_path": s3Object["Key"],
            }

            # append tweet to list to be stored
            tweets.append(esTweet)

        # needed to set the index to store the tweet
        year_month = (
            str(s3Object["LastModified"].year)
            + "-"
            + str(s3Object["LastModified"].month)
        )
        es_index = "tweets-" + year_month

        # stores all tweets in list to Elasticsearch
        helpers.bulk(es, tweets, index=es_index)
        lastKey = s3Object["Key"]
