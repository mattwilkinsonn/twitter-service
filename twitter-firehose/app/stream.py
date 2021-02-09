import logging
import sentry_sdk
from queue import Queue
import threading
from core.settings import settings
from firehose.firehosePutter import FirehosePutter
from twitter.twitterStreamer import TweetStreamer


# Log info messages for debugging
logging.basicConfig(level=logging.INFO)

# Start sentry
sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENV)

# if settings.ENV == "local":
#     exit()

# Set up Queue, handles moving Tweets from Stream thread to Firehose thread
tweetQueue = Queue()


# Start Firehose Putter thread
threading.Thread(
    name="Firehose Putter", target=FirehosePutter, args=(tweetQueue,)
).start()
# Start Twitter Streamer thread
threading.Thread(
    name="Twitter Streamer", target=TweetStreamer, args=(tweetQueue,)
).start()

# Blocks main thread until the tweetQueue is empty
tweetQueue.join()
