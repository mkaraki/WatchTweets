import json
import os

import requests
from dotenv import load_dotenv

# You have to configure in this file to notify other services


def notifyHandler(tweet):
    notifyDiscord(tweet)
    return


def notifyDiscord(tweet, find_user_info=False):
    c = {
        'embeds': [{
            'description': tweet['text'],
            'author': {
                'name': tweet['author_id'],
                'url': 'https://twitter.com/intent/user?user_id=' + tweet['author_id'],
            },
            'title': 'Tweet',
            'url': 'https://twitter.com/intent/like?tweet_id=' + tweet['id'],
            'footer': {
                'text': 'Twitter',
                'icon_url': 'http://github.com/twitter.png',
            },
            'timestamp': tweet['created_at'],
        }]
    }
    requests.post(os.getenv('DISCORD_WEBHOOK_URL'), json.dumps(
        c), headers={'Content-Type': 'application/json'})
    return


load_dotenv(override=True)
