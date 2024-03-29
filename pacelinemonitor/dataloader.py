import base64
import os
import time
from typing import Optional
from urllib.parse import urlparse, parse_qs, urlencode

import requests
from requests import PreparedRequest

from pacelinemonitor.conf import NEW_THREAD_DELAY_SECS
from pacelinemonitor.datacacher import get_cache, CacheEntry
from pacelinemonitor.pacelinethread import PacelineThread

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


def desearch_thread_href(href: str):
    """
    Often the href to threads from the main page have unnecessary params that work only temporarily
    and contain data about the search itself.  This normalizes the href to just be the relative
    site path for the thread.  E.g.
      'showthread.php?s=7b3f0b7ebe9ddd8a9c17cff04a255929&t=291638' -> 'showthread.php?t=291638
    :param href:
    :return:
    """
    parse_res = urlparse(href)
    query = parse_qs(parse_res.query)
    new_query = urlencode({'t': query['t'][0]})
    return parse_res._replace(query=new_query).geturl()



def load_thread(thread: PacelineThread) -> Optional[str]:
    cache = get_cache()
    if thread in cache:
        print(f'reading thread {thread.thread_id} from cache')
        thread_data = cache[thread]
        with open(thread_data.cached_file) as reader:
            return reader.read()

    url = full_url(thread.link)
    encoded_url = base64.b64encode(url.encode()).decode()
    fname = f'{encoded_url}.html'
    fpath = os.path.join(CACHE_DIR, fname)

    cache[thread] = CacheEntry(
        thread=thread,
        load_time=time.time(),
        cached_file=fpath,
        is_match=False
    )

    print(f'new thread: {thread.thread_id}')
    time.sleep(NEW_THREAD_DELAY_SECS)  # don't wanna be too mean and overload paceline
    contents = _load(url)
    with open(fpath, 'w') as writer:
        writer.write(contents)
    return contents


def _load(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        return None
