from time import time
from datetime import datetime, timedelta
import os
import re

from random import choice

from dateutil.parser import parse as dateparse
from pytz import utc
import requests


class Anilist(object):
    base = u'https://anilist.co/api/{}'

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def _renew_token(self):
        self.access_token = requests.post(
            self.base.format('auth/access_token'),
            params={'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret}).json()

    def _req(self, method, path, **params):
        if (
            not hasattr(self, 'access_token')
            or self.access_token['expires'] <= (time() - 60)
        ):
            # we either don't have a token or the one we have will be expiring
            # soon, so:
            self._renew_token()

        return requests.request(
            method, self.base.format(path), params=params,
            headers={'Authorization': 'Bearer {}'.format(
                self.access_token['access_token'])}).json()

    def _post(self, path, **params):
        return self._req('post', path, **params)

    def _get(self, path, **params):
        return self._req('get', path, **params)

    def browse(self, **params):
        return self._get('browse/anime', **params)

    def get_anime(self, anime_id):
        return self._get('anime/{}'.format(anime_id))


from secrets import client_id, client_secret
anilist = Anilist(client_id, client_secret)


with open(os.path.join(os.path.dirname(__file__), 'tweet.txt')) as tf:
    TWEETS = [
        t.strip()
        for t in tf.readlines()
    ]


def get_airing():
    airing = anilist.browse(status='Currently Airing', full_page=True)
    threshold = datetime.utcnow().replace(tzinfo=utc) - timedelta(days=365)
    anime = None
    while (anime is None or (
        airing and dateparse(anime['start_date']) < threshold)
    ):
        small_anime = choice(airing)
        airing.remove(small_anime)
        anime = anilist.get_anime(small_anime['id'])

    return anime


def get_popular():
    target = 1000
    page_len = 40
    page = 1
    choices = []
    while len(choices) < target and page_len != 0:
        res = anilist.browse(sort='popularity-desc', page=page)
        page_len = len(res)
        choices.extend(res)
        page += 1
    return choice(choices)


def get_title():
    func = choice([get_airing, get_popular])
    return func()['title_english']


def add_the(title):
    flags = re.IGNORECASE
    if re.match(
        r'.*\s+(ONA|OVA|Movie)$',
        title,
        flags=flags
    ) and not re.match(
        r'The.*',
        title,
        flags=flags
    ):
        return u'the {}'.format(title)

    return title


def remove_year(title):
    return re.sub(r'\s+\(\d{4}\)$', '', title)


def process_title(title):
    for func in [
        remove_year,
        add_the,
    ]:
        title = func(title)

    return title


def get_tweet():
    return choice(TWEETS).replace(
        '<anime>', process_title(get_title())
    ).lower()


if __name__ == '__main__':
    print get_tweet()
