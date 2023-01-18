import functools
import json
import os
import time
from datetime import timedelta
from typing import Optional, Dict, NamedTuple

from pacelinemonitor.pacelinethread import PacelineThread

DB_FNAME = 'database.json'
TTL = timedelta(days=1).total_seconds()


class CacheEntry(NamedTuple):
    thread: PacelineThread
    load_time: float
    cached_file: str
    is_match: bool


class PacelineCache:
    data: Dict[PacelineThread, CacheEntry]

    def __init__(self, data: Optional[Dict] = None):
        if data is None:
            data = {}
        self.data = data

    @classmethod
    def from_file(cls, fname=DB_FNAME):
        if os.path.exists(fname):
            with open(DB_FNAME) as db_reader:
                database = json.load(db_reader)
        else:
            database = None
        return PacelineCache(data=database)

    def _prune(self):
        for thread_id, entry in self.data.items():
            if entry.load_time + TTL < time.time():
                os.remove(entry.cached_file)
                del self.data[thread_id]

    def save(self, fname=DB_FNAME):
        with open(fname, 'w') as fp:
            json.dump(self.data, fp)

    def __contains__(self, thread: PacelineThread):
        return thread in self.data

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, item) -> CacheEntry:
        return self.data[item]


CACHE = PacelineCache.from_file()


def get_cache() -> PacelineCache:
    return CACHE
