from es.es_init import get_es
import logging
from time import sleep
import sentry_sdk
from core.config import settings
from es.es_funcs import get_newest_doc, put_to_elasticsearch
from tweet_decode.tweet_decode import read_tweet_gzip
from s3.s3_init import get_s3_client


logging.getLogger("backoff").addHandler(logging.StreamHandler())

if settings.LOGGING_LEVEL == "INFO":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("backoff").setLevel(logging.INFO)
if settings.LOGGING_LEVEL == "WARNING":
    logging.basicConfig(level=logging.WARNING)

sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENV)


s3 = get_s3_client()


# freezing indexes
# es = get_es()

# indicesClient = es.indices

# indices = indicesClient.get(index="tweets-*-*", expand_wildcards="open")

# if len(indices) > 1:
#     newestDate = 0
#     newestIndexKey = ""
#     for key, index in indices.items():
#         creation_date = int(index["settings"]["index"]["creation_date"])
#         if creation_date > newestDate:
#             newestIndexKey = key
#             newestDate = creation_date

#     newestIndexObject = indices.pop(newestIndexKey)
#     logging.info(f"current index: f{newestIndexKey}")

#     for key, index in indices.items():
#         logging.info(f"freezing index: f{key}")
#         indices.freeze(key)


# reliable solution, newest tweet will always have the last key
# all tweets get sent together so any one key in ES means
# that all of the tweets from that key are in ES
try:
    newest_doc = get_newest_doc()
    last_key = newest_doc["s3_file_path"]

    logging.info(f"last_key: {last_key}")

except IndexError:
    # index error means there are no documents in ES. go from oldest AWS key
    # No StartAfter -> starts at oldest key
    last_key = s3.list_objects_v2(
        Bucket=settings.S3_BUCKET, EncodingType="url", MaxKeys=10, Prefix="tweets"
    )["Contents"][0]["Key"]


while True:
    s3_object_list = s3.list_objects_v2(
        Bucket=settings.S3_BUCKET,
        EncodingType="url",
        MaxKeys=1000,
        Prefix="tweets",
        StartAfter=last_key,
    )

    # kinda janky solution, should be a better way to do this
    # events would make a lot more sense but need to look into how to set those up
    if s3_object_list["KeyCount"] <= 0:
        logging.info("waiting 1 hour for new tweets")
        sleep(3600)
        continue

    # for each item in response, get the s3 file, decode, send to ES
    for s3_object in s3_object_list["Contents"]:
        if s3_object["Size"] <= 0:
            continue

        # considered using S3 Select here but got some weird errors
        tweet_file = s3.get_object(Bucket=settings.S3_BUCKET, Key=s3_object["Key"])[
            "Body"
        ]

        # read_tweet_gzip reformats tweets into ES schema
        tweets = read_tweet_gzip(tweet_file, s3_object["Key"])

        # needed to set the index to store the tweet
        year_month = (
            str(s3_object["LastModified"].year)
            + "-"
            + str(s3_object["LastModified"].month)
        )
        es_index = "tweets-" + year_month

        put_to_elasticsearch(tweets, es_index)

        last_key = s3_object["Key"]
