import logging
import json
from pprint import pprint
import boto3
from core.settings import settings


# Start firehose client
def create_firehose():
    return boto3.client("firehose", region_name=settings.AWS_REGION)


# Firehose worker
def FirehosePutter(tweetQueue):

    tweetBatch = []

    firehose_client = create_firehose()

    while True:
        try:
            rawTweet = tweetQueue.get()
            jsonTweet = json.loads(rawTweet)["data"]
            newTweet = json.dumps(jsonTweet)
            tweetBatch.append({"Data": newTweet})
            tweetQueue.task_done()
        except Exception as ex:
            logging.exception(f"exception getting tweets from Queue \n {ex}")
            continue

        # Maximum per batch is 500 on aws
        if len(tweetBatch) >= 500:
            if settings.ENV == "prod":
                try:
                    logging.info("putting tweets to firehose")
                    logging.info(f"tweets in batch: {len(tweetBatch)}")
                    logging.info(f"tweets in queue: {tweetQueue.qsize()}")
                    # Put tweetBatch, then clear list
                    firehose_client.put_record_batch(
                        DeliveryStreamName="tweets", Records=tweetBatch
                    )
                    tweetBatch.clear()
                    logging.info("putting tweets success")
                except Exception as ex:
                    # Exception handling
                    logging.exception(f"exception pushing tweet to firehose: {ex}")
                    continue

            if settings.ENV == "local":
                logging.info("dumping tweets from batch")
                logging.info(f"tweets in batch: {len(tweetBatch)}")
                logging.info(f"tweets in queue: {tweetQueue.qsize()}")
                logging.info(f"Tweet 1: {pprint(tweetBatch[0])}")

                tweetBatch.clear()
