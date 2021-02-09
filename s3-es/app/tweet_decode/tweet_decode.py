import gzip
from os import EX_OK
import dateutil.parser
import re
from json import JSONDecoder, JSONDecodeError
import logging


def decode_stacked(document, pos=0, decoder=JSONDecoder()):
    NOT_WHITESPACE = re.compile(r"[^\s]")
    while True:
        match = NOT_WHITESPACE.search(document, pos)
        if not match:
            return
        pos = match.start()

        try:
            obj, pos = decoder.raw_decode(document, pos)
        except JSONDecodeError:
            logging.error("JSON Decode Error")
            raise Exception("JSON Decode Error")
        yield obj


def read_tweet_gzip(tweetFile, s3Key):
    tweets = []

    unzipped_file = gzip.GzipFile(fileobj=tweetFile).read().decode("utf-8")

    for tweet in decode_stacked(unzipped_file):
        if "entities" not in tweet:
            continue

        # this gets rid of a lot of tweets, most don't have external links
        if "urls" not in tweet["entities"]:
            continue

        url_length = len(tweet["entities"]["urls"])
        if (
            url_length == 1
            and "twitter.com" in tweet["entities"]["urls"][0]["expanded_url"]
        ):
            continue

        # makes url more easily queryable, regular url is shortened
        expanded_url = ''
        for url in tweet["entities"]["urls"]:
            if "twitter.com" in url["expanded_url"]:
                continue
            expanded_url = url["expanded_url"]
            break

        # outputs epoch seconds, ES can read without any weird configs
        created_at_epoch = int(dateutil.parser.parse(tweet["created_at"]).timestamp())

        # tweets from 10-20 to 10-28 did not have author_id attached
        if "author_id" not in tweet:
            tweet["author_id"] = None

        # tweet schema
        es_tweet = {
            "created_at": created_at_epoch,
            "url": expanded_url,
            "text": tweet["text"],
            "like_count": tweet["public_metrics"]["like_count"],
            "_id": tweet["id"],
            "author_id": tweet["author_id"],
            "quote_count": tweet["public_metrics"]["quote_count"],
            "reply_count": tweet["public_metrics"]["reply_count"],
            "retweet_count": tweet["public_metrics"]["retweet_count"],
            "lang": tweet["lang"],
            "s3_file_path": s3Key,
        }

        # append tweet to list to be stored
        tweets.append(es_tweet)
    return tweets
