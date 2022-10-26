import base64
import os
from typing import Optional

import requests

CACHE_DIR = './cache/'


def load_forum(forum_id='6') -> Optional[str]:
    with open('sample.html') as reader:
        return reader.read()
    # url = f'https://forums.thepaceline.net/forumdisplay.php?f={forum_id}'
    # return _load(url)


def load_thread(href: str) -> Optional[str]:
    # with open('sample_thread.html') as reader:
    #     return reader.read()
    url = f'https://forums.thepaceline.net/{href}'
    encodedurl = base64.b64encode(url.encode()).decode()
    fname = f'{encodedurl}.html'
    fpath = os.path.join(CACHE_DIR, fname)
    if not os.path.exists(fpath):
        contents = _load(url)
        with open(fpath, 'w') as writer:
            writer.write(contents)
        return contents
    with open(fpath) as reader:
        return reader.read()


def _load(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        return None
