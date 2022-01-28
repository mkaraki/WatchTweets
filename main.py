import os
import json
import time
import calendar
from datetime import datetime

from Twitter_Frontend_API import Client
from dotenv import load_dotenv

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
        dt = datetime.utcfromtimestamp(since_time + 1)
        q += ' since:' + dt.strftime('%Y-%m-%d_%H:%M:%S_UTC')

    if (until_time != None):
        dt = datetime.utcfromtimestamp(until_time)
        q += ' until:' + dt.strftime('%Y-%m-%d_%H:%M:%S_UTC')

    print(q)

    d = client.latest_search(q)
    if ('globalObjects' in d and 'tweets' in d['globalObjects']):
        return d['globalObjects']['tweets']


def getAllNewTweets(client, query, stime=None):
    until_time = None
    max_time = None

    while True:
        res = getTweets(client, query, since_time=stime, until_time=until_time)

        if (res == None):
            return None, []

        print('[INFO] Downloaded {} tweets'.format(
            len(res)))

        # if no tweets retrived, return
        if (len(res) == 0):
            if (max_time is None):
                return None, []
            else:
                return max_time, []

        for tweet in res.values():
            tweet['created_at_unixtime'] = int(calendar.timegm(
                datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S %z %Y").timetuple()))

        # Save latest id as since id to return (for next polling)
        if (max_time == None):
            max_time = max(list(res.values()), key=lambda x: x['created_at_unixtime']).get(
                'created_at_unixtime')

        # if tweets are smaller than 20 (fully polled in this round)
        # or, if no tweet polling limit is set, return
        if (stime == None or len(res) < 20):
            return max_time, res

        # if couldn't poll all tweets,
        # set until_id to oldest tweet id
        # (poll tweets between last polled and polled now)
        until_time = min(list(res.values()), key=lambda x: x['created_at_unixtime']).get(
            'created_at_unixtime')


if __name__ == '__main__':
    import notify_tweet

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
        stime, res = getAllNewTweets(client, query, stime=stime)

        if (len(res) > 0):
            # Save Tweets to file
            saveTweet(res)

            # Invoke notify handler
            for tweet in res.values():
                notify_tweet.notifyHandler(tweet)

        # Save last id
        if (stime != None):
            with open(lastsidpath, 'w') as f:
                json.dump({'stime': stime}, f)
        else:
            # If cannot got any last id information,
            # Re-use last id information from last polling.
            stime = tstime

        # Wait for next polling
        time.sleep(POLL_INTERVAL)
