import json
import os.path
import re
import time

from bs4 import BeautifulSoup

from pacelinemonitor.dataloader import load_thread, load_forum, full_url
from pacelinemonitor.pacelinethread import PacelineThread

DB_FNAME = 'database.json'
if os.path.exists(DB_FNAME):
    with open(DB_FNAME) as db_reader:
        database = json.load(db_reader)
else:
    database = {}


def scrape_first_page_forum(forum_id='6'):
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
                thread_ids.add((thread_id, href))
    return thread_ids


def scrape_thread(thread_id, href):
    pagecontent = load_thread(thread_id, href)
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


def search_classifieds(patterns):
    thread_ids = scrape_first_page_forum()
    new_results = []
    for thread_id, href in thread_ids:
        if thread_id in database:
            continue
        title, full_text = scrape_thread(thread_id, href)
        matches = [(p, p.search(full_text)) for p in patterns]
        for p, match in matches:
            if match:
                database[thread_id] = href
                print(f"MATCHED {thread_id}:", href, p, match)

                new_results.append(PacelineThread(thread_id, title, full_url(href)))

    with open(DB_FNAME, 'w') as writer:
        json.dump(database, writer)

    return new_results
