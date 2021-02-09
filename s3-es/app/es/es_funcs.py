import backoff
from elasticsearch.exceptions import AuthorizationException
from elasticsearch import helpers
from .es_init import get_es
from elasticsearch_dsl import Search
import logging

es = get_es()


def es_backoff_handler(details):

    logging.info("Backoff, attempting to refresh AWS credentials")

    global es
    es = get_es()


@backoff.on_exception(
    backoff.expo, AuthorizationException, max_tries=20, on_backoff=es_backoff_handler
)
def put_to_elasticsearch(tweets, es_index):
    return helpers.bulk(es, tweets, index=es_index)


def get_newest_doc():
    newest_doc = (
        Search(using=es, index="tweets-*")
        .sort({"created_at": {"order": "desc"}})[0:2]
        .execute()[0]
    )

    return newest_doc
