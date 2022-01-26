import os
import json
import time
import datetime

from Twitter_Frontend_API import Client
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
    return Client()


def saveTweet(tweet):
    fname = 'tweets/f_' + min(tweet.items())[0] + '-' + \
        max(tweet.items())[0] + '.json'

    with open(fname, 'w') as f:
        json.dump(list(tweet.values()), f)


def getTweets(client, query, since_time=None, until_time=None):
    print('[INFO] Download Queued ({} -> {})'.format(since_time, until_time))

    q = query

    if (since_time != None):
        q += ' since:' + str(since_time)

    if (until_time != None):
        q += ' until:' + str(until_time)

    return client.latest_search(q)['globalObjects']['tweets']


def getAllNewTweets(client, query, stime=None):
    until_time = None
    max_time = None

    while True:
        res = getTweets(client, query, since_time=stime, until_time=until_time)

        print('[INFO] Downloaded {} tweets'.format(
            len(res)))

        # if no tweets retrived, return
        if (len(res) == 0):
            if (max_time is None):
                return None
            else:
                return max_time

        for tweet in res.values():
            tweet['created_at_unixtime'] = time.mktime(
                datetime.datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S %z %Y").timetuple())

        # Save latest id as since id to return (for next polling)
        if (max_time == None):
            max_time = min(res.items())[1]['created_at_unixtime']

        saveTweet(res)

        for tweet in res.values():
            notify_tweet.notifyHandler(tweet)

        # if tweets are smaller than 20 (fully polled in this round), return
        if (len(res) < 20):
            return max_time

        # if no tweet polling limit is set, return
        if (stime == None):
            return max_time

        # if couldn't poll all tweets,
        # set until_id to oldest tweet id
        # (poll tweets between last polled and polled now)
        until_time = min(res.items())[1]['created_at_unixtime']


query = os.getenv("QUERY")

client = getClient()

lastsidpath = './last_sid.json'
stime = None

if (os.path.exists(lastsidpath)):
    with open(lastsidpath, 'r') as f:
        j = json.load(f)
        if ('stime' in j):
            stime = j['stime']

print('[INFO] Query: "{}" Last STIME: {}'.format(query, stime))

while True:
    tstime = stime
    stime = getAllNewTweets(client, query, stime=stime)
    if (stime != None):
        with open(lastsidpath, 'w') as f:
            json.dump({'stime': stime}, f)
    else:
        stime = tstime
    time.sleep(POLL_INTERVAL)
