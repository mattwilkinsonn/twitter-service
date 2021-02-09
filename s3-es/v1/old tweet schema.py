for line in gzip.GzipFile(fileobj=tweetFile):

        # print(line)

        tweet = json.loads(line)

        if (
            "delete" in tweet
            or "status_withheld" in tweet
            or "retweeted_status" in tweet
        ):
            continue

        if tweet["id_str"] == "1309658165844283392":
            print(0)

        # this gets rid of a lot of tweets, most don't have external links
        urlLength = len(tweet["entities"]["urls"])
        if (
            urlLength == 0
            or urlLength == 1
            and "twitter.com" in tweet["entities"]["urls"][0]["expanded_url"]
        ):
            continue

        if (
            tweet["quote_count"] != 0
            or tweet["reply_count"] != 0
            or tweet["retweet_count"] != 0
            or tweet["favorite_count"] != 0
        ):
            pprint(tweet)
            print(0)

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
        created_at_epoch = int(dateutil.parser.parse(tweet["created_at"]).timestamp())

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
            "s3_file_path": s3Key,
        }

        # append tweet to list to be stored
        tweets.append(esTweet)
    return tweets