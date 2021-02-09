import requests
from ..core.config import settings
import os
import json
import logging

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'


def auth():
    return settings.TWITTER_BEARER_TOKEN


def create_url(ids):
    tweet_fields = "tweet.fields=lang,author_id,public_metrics,entities,created_at,text"
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    idsField = "ids=" + ids

    # ids = "ids=1278747501642657792,1255542774432063488"
    # You can adjust ids to include a single Tweets.
    # Or you can add to up to 100 comma-separated IDs
    url = "https://api.twitter.com/2/tweets?{}&{}".format(idsField, tweet_fields)
    return url


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def tweet_update(tweets, ids):
    bearer_token = auth()
    url = create_url(ids)
    headers = create_headers(bearer_token)
    twitter_response = connect_to_endpoint(url, headers)

    total_like_count = 0
    total_retweet_count = 0

    for tweet in twitter_response["data"]:
        tweets[tweet["id"]]["_source"]["like_count"] = tweet["public_metrics"][
            "like_count"
        ]
        tweets[tweet["id"]]["_source"]["retweet_count"] = tweet["public_metrics"][
            "retweet_count"
        ]

        total_like_count += tweet["public_metrics"]["like_count"]

        total_retweet_count += tweet["public_metrics"]["retweet_count"]

    return {
        "tweets": tweets,
        "total_like_count": total_like_count,
        "total_retweet_count": total_retweet_count,
    }
