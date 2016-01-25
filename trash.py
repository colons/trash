import re
from urlparse import urlparse

import requests


def remove_year(title):
    return re.sub(r'\s+\(\d{4}\)$', '', title)


if __name__ == '__main__':
    redir = requests.get('https://hummingbird.me/random/anime',
                         allow_redirects=False).headers['Location']
    api_resp = requests.get(
        'http://hummingbird.me/api/v1' + urlparse(redir).path
    ).json()

    print remove_year(api_resp['title'])
