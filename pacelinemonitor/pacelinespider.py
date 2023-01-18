import json
import os.path
import re
import time
from typing import List, Set, NamedTuple

from bs4 import BeautifulSoup

from pacelinemonitor.datacacher import PacelineCache, CacheEntry, get_cache
from pacelinemonitor.dataloader import load_thread, load_forum, full_url
from pacelinemonitor.pacelinethread import PacelineThread

CLASSIFIED_FORUM_ID = '6'

class PacelineResult(NamedTuple):
    thread: PacelineThread
    url: str
    pattern: str
def scrape_first_page_forum(forum_id=CLASSIFIED_FORUM_ID) -> Set[PacelineThread]:
    pagecontent = load_forum(forum_id=forum_id)
    soup = BeautifulSoup(pagecontent, features='lxml')
    threadtable = soup.find(id="threadslist")
    posts_tbody = threadtable.find(id=f"threadbits_forum_{forum_id}")
    thread_ids = set()
    for row in posts_tbody.find_all("tr"):
        main_td = row.find_all_next('td', limit=3)[2]
        td_text = ''.join(main_td.strings)
        if 'Sticky: ' in td_text:
            continue
        for link in main_td.find_all('a'):
            if link.get('id', '').startswith('thread_title_'):
                thread_id = link.get('id').split('_')[2]
                href = link.get('href')
                thread_ids.add(PacelineThread(thread_id, href))
    return thread_ids


def scrape_thread(thread: PacelineThread) -> (str, str):
    """
    Extract the title, and initial post text content from the thread
    :param thread_id: id of the thread to scrape
    :param href: link to the thread
    :return: (thread title, thread title + initial post text)
    """
    pagecontent = load_thread(thread)
    soup = BeautifulSoup(pagecontent, features='lxml')
    main_div = soup.find(id='posts')
    main_thread = main_div.find('table')

    # get the thread title
    initial_row = main_thread.find_all('tr')[3]  # first rows are metadata about thread
    title_div = initial_row.find_next('div')
    title_text = title_div.text.strip()
    print(title_text)

    # get the body of the initial post
    post_id = main_thread['id'][4:]
    initial_post = main_thread.find(id=f'post_message_{post_id}')
    initial_post_text = initial_post.text.strip()
    initial_post_text = re.sub('\s+', ' ', initial_post_text)
    return title_text, title_text + '\n\n' + initial_post_text


def search_classifieds(patterns: List[re.Pattern]):
    """
    Search classified forum for any listings matching any pattern in patterns
    :param patterns:
    :return:
    """
    cache = get_cache()
    threads = scrape_first_page_forum()
    new_results = []

    for thread in threads:
        title, full_text = scrape_thread(thread)
        matches = [(p, p.search(full_text)) for p in patterns]

        for p, match in matches:
            if match:
                cache[thread].is_match = True
                print(f"MATCHED {thread.thread_id}:", p, match)
                new_results.append(
                    PacelineResult(thread, full_url(thread.link), p.pattern)
                )

    cache.save()

    return new_results
