import os
import json
import time

import tweepy
from dotenv import load_dotenv

import notify_tweet

###############################################################################
# Configurations
###############################################################################

POLL_INTERVAL = 30

###############################################################################
# Program
###############################################################################


load_dotenv(override=True)


def getClient():
    # Twitter API credentials
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
    bearer_token = os.getenv("BEARER_TOKEN")

    client = tweepy.Client(bearer_token, consumer_key, consumer_secret,
                           access_token, access_token_secret, return_type=dict, wait_on_rate_limit=True)

    return client


def saveTweet(tweet):
    fname = 'tweets/' + tweet['meta']['oldest_id'] + '-' + \
        tweet['meta']['newest_id'] + '.json'

    with open(fname, 'w') as f:
        json.dump(tweet, f)


def getTweets(client, query, since_id=None, until_id=None, limit=10):
    print('[INFO] Download Queued ({} -> {}: {})'.format(since_id, until_id, limit))
    return client.search_recent_tweets(
        tweet_fields=['attachments', 'author_id', 'context_annotations', 'created_at', 'entities', 'geo', 'id', 'in_reply_to_user_id', 'lang',
                      'possibly_sensitive', 'public_metrics', 'referenced_tweets', 'source', 'text', 'withheld'],
        media_fields=['duration_ms', 'height', 'media_key', 'preview_image_url',
                      'public_metrics', 'type', 'url', 'width'],
        place_fields=['contained_within', 'country', 'country_code',
                      'full_name', 'geo', 'id', 'name', 'place_type'],
        poll_fields=['duration_minutes', 'end_datetime',
                     'id', 'options', 'voting_status'],
        user_fields=['created_at', 'description', 'entities', 'id', 'location', 'name', 'pinned_tweet_id',
                     'profile_image_url', 'protected', 'public_metrics', 'url', 'username', 'verified', 'withheld'],
        query=query,
        max_results=limit,
        since_id=since_id,
        until_id=until_id)


def getAllNewTweets(client, query, sid=None):
    until_id = None
    max_sid = None

    while True:
        res = getTweets(client, query, since_id=sid, until_id=until_id)

        print('[INFO] Downloaded {} tweets'.format(
            res['meta']['result_count']))

        # if no tweets retrived, return
        if (res['meta']['result_count'] == 0):
            if (max_sid is None):
                return None
            else:
                return max_sid

        # Save latest id as since id to return (for next polling)
        if (max_sid == None):
            max_sid = res['meta']['newest_id']

        saveTweet(res)

        for tweet in res['data']:
            notify_tweet.notifyHandler(tweet)

        # if tweets are smaller than 10 (fully polled in this round), return
        if (res['meta']['result_count'] < 10):
            return max_sid

        # if no tweet polling limit is set, return
        if (sid == None):
            return max_sid

        # if couldn't poll all tweets,
        # set until_id to oldest tweet id
        # (poll tweets between last polled and polled now)
        until_id = res['meta']['oldest_id']


query = os.getenv("QUERY")

client = getClient()

lastsidpath = './last_sid.json'
sid = None

if (os.path.exists(lastsidpath)):
    with open(lastsidpath, 'r') as f:
        sid = json.load(f)['sid']

print('[INFO] Query: "{}" Last SID: {}'.format(query, sid))

while True:
    tsid = sid
    sid = getAllNewTweets(client, query, sid=sid)
    if (sid != None):
        with open(lastsidpath, 'w') as f:
            json.dump({'sid': sid}, f)
    else:
        sid = tsid
    time.sleep(POLL_INTERVAL)
