import requests
from requests.models import ChunkedEncodingError
from core.settings import settings
import logging
import backoff


def auth():
    return settings.TWITTER_BEARER_TOKEN


def create_url():
    tweetfields = (
        "tweet.fields=created_at,lang,entities,public_metrics,geo&expansions=author_id"
    )
    return "https://api.twitter.com/2/tweets/sample/stream?" + tweetfields


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


class StreamFailedError(Exception):
    pass


def twitter_backoff_handler(details):

    logging.info("Twitter backoff handler")
    logging.info(f"Tries: {details['tries']} Waiting for {details['wait']}")


@backoff.on_exception(
    backoff.expo,
    (ChunkedEncodingError, StreamFailedError),
    max_tries=30,
    on_backoff=twitter_backoff_handler,
)
def connect_to_endpoint(url, headers, tweetQueue):
    response = requests.request("GET", url, headers=headers, stream=True)
    # print(response.status_code)
    if response.status_code != 200:
        raise StreamFailedError(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            tweetQueue.put(response_line)


def TweetStreamer(tweetQueue):
    bearer_token = auth()
    url = create_url()
    headers = create_headers(bearer_token)
    connect_to_endpoint(url, headers, tweetQueue)
