import os
import re

from urlparse import urlparse
from random import choice

import requests


with open(os.path.join(os.path.dirname(__file__), 'tweet.txt')) as tf:
    TWEETS = [
        t.strip()
        for t in tf.readlines()
    ]


def remove_year(title):
    return re.sub(r'\s+\(\d{4}\)$', '', title)


def get_title():
    redir = requests.get('https://hummingbird.me/random/anime',
                         allow_redirects=False).headers['Location']
    api_resp = requests.get(
        'http://hummingbird.me/api/v1' + urlparse(redir).path
    ).json()

    return remove_year(api_resp['title'])


def get_tweet():
    return choice(TWEETS).replace('<anime>', get_title())


if __name__ == '__main__':
    print get_tweet()
