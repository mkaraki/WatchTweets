import os
import json
import time

import tweepy
from dotenv import load_dotenv


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


def getTweets(client, query, since_id=None, limit=10):
    print('[INFO] Download Queued ({} -> {}: {})'.format(since_id, None, limit))
    return client.search_recent_tweets(
        tweet_fields=['attachments', 'author_id', 'context_annotations', 'created_at', 'entities', 'geo', 'id', 'in_reply_to_user_id', 'lang',
                      'possibly_sensitive', 'public_metrics', 'referenced_tweets', 'source', 'text', 'withheld'],
        media_fields=['duration_ms,height', 'media_key', 'preview_image_url',
                      'public_metrics', 'type', 'url', 'width'],
        place_fields=['contained_within', 'country', 'country_code',
                      'full_name', 'geo', 'id', 'name', 'place_type'],
        poll_fields=['duration_minutes', 'end_datetime',
                     'id', 'options', 'voting_status'],
        user_fields=['created_at', 'description', 'entities', 'id', 'location,name', 'pinned_tweet_id',
                     'profile_image_url', 'protected', 'public_metrics', 'url', 'username', 'verified', 'withheld'],
        query=query,
        max_results=limit,
        since_id=since_id)


def getAllNewTweets(client, query, sid=None):
    for limit in range(10, 100, 10):
        res = getTweets(client, query, since_id=sid, limit=limit)
        if (res['meta']['result_count'] == 0):
            return None
        elif (res['meta']['result_count'] < limit):
            return res

        if sid is None:
            return res


def main(sid=None):
    query = os.getenv("QUERY")

    client = getClient()

    s_res = getAllNewTweets(
        client, query, sid=sid)

    if (s_res == None):
        return None

    fname = s_res['meta']['oldest_id'] + '-' + \
        s_res['meta']['newest_id'] + '.json'

    with open(fname, 'w') as f:
        json.dump(s_res, f)

    return s_res['meta']['newest_id']


lastsidpath = './last_sid.json'
sid = None

if (os.path.exists(lastsidpath)):
    with open(lastsidpath, 'r') as f:
        sid = json.load(f)['sid']

while True:
    tsid = sid
    sid = main(sid)
    if (sid != None):
        with open(lastsidpath, 'w') as f:
            json.dump({'sid': sid}, f)
    else:
        sid = tsid
    time.sleep(30)
