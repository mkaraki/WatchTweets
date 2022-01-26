import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

# You have to configure in this file to notify other services


def notifyHandler(tweet):
    notifyDiscord(tweet)
    return


def notifyDiscord(tweet, find_user_info=False):
    msg = tweet['text']

    if ('entities' in tweet and 'urls' in tweet['entities']):
        for (i, url) in enumerate(tweet['entities']['urls']):
            msg = msg.replace(url['url'], url['expanded_url'])

    time = datetime.fromtimestamp(
        tweet['created_at_unixtime']).isoformat()

    c = {
        'embeds': [{
            'description': msg,
            'author': {
                'name': tweet['user_id_str'],
                'url': 'https://twitter.com/intent/user?user_id=' + tweet['user_id_str'],
            },
            'title': 'Tweet',
            'url': 'https://twitter.com/intent/like?tweet_id=' + tweet['id_str'],
            'footer': {
                'text': 'Twitter',
                'icon_url': 'http://github.com/twitter.png',
            },
            'timestamp': time,
        }]
    }
    requests.post(os.getenv('DISCORD_WEBHOOK_URL'), json.dumps(
        c), headers={'Content-Type': 'application/json'})
    return


load_dotenv(override=True)
