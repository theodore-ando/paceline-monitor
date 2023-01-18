import base64
import os
import time
from typing import Optional

import requests
from requests import PreparedRequest

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
CACHE_DIR = os.path.join(THIS_DIR, 'cache')


def load_forum(forum_id='6', page=1) -> Optional[str]:
    params = {
        'f': forum_id,
        'page': page,
        'order': 'desc'
    }
    req = PreparedRequest()
    req.prepare_url('https://forums.thepaceline.net/forumdisplay.php', params)

    # url = f'https://forums.thepaceline.net/forumdisplay.php?f={forum_id}'
    return _load(req.url)


def full_url(href):
    """href from internal paceline links aren't full url"""
    return f'https://forums.thepaceline.net/{href}'


def load_thread(thread_id: str, href: str) -> Optional[str]:
    # with open('sample_thread.html') as reader:
    #     return reader.read()
    url = full_url(href)
    encodedurl = base64.b64encode(url.encode()).decode()
    fname = f'{encodedurl}.html'
    fpath = os.path.join(CACHE_DIR, fname)
    if not os.path.exists(fpath):
        print(f'new thread: {thread_id}')
        time.sleep(1)  # don't wanna be too mean and overload paceline
        contents = _load(url)
        with open(fpath, 'w') as writer:
            writer.write(contents)
        return contents
    else:
        print(f'reading thread {thread_id} from cache')
    with open(fpath) as reader:
        return reader.read()


def _load(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        return None
