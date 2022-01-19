import os
import json
import csv


tweet_objs = []


w_csv = []


for de in os.scandir('./tweets/'):
    if de.is_file() and de.name.endswith('.json'):
        with open(de.path, 'r') as f:
            tweet_objs.append([de.name, json.load(f)])


for tweet_obj in tweet_objs:
    for tweet in tweet_obj[1]['data']:
        w_csv.append([tweet['id'], tweet['created_at'],
                      tweet['author_id'], tweet['text']])


w_csv.sort(key=lambda x: x[0])
w_csv.insert(0, ['id', 'created_at', 'author', 'text'])


with open('tweets.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(w_csv)
