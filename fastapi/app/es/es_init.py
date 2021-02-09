import boto3
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from ..core.config import settings
import logging


def get_awsauth_es():

    credentials = boto3.Session().get_credentials()

    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        settings.AWS_REGION,
        "es",
        session_token=credentials.token,
    )

    return awsauth


def get_es():
    # init elasticsearch
    awsauth = get_awsauth_es()
    if settings.ENV != "local":
        logging.info("prod ES")
        # ES for AWS needs these credentials,
        return Elasticsearch(
            hosts=[{"host": settings.ES_HOST, "port": 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30,
            max_retries=10,
            retry_on_timeout=True,
        )
    elif settings.ENV == "local":
        logging.info("local ES")
        # still the AWS elasticsearch, just running through SSH tunnel.
        return Elasticsearch(
            hosts=[{"host": "dockerhost"}], use_ssl=True, verify_certs=False
        )