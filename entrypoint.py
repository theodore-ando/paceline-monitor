#!/usr/bin/env python3
import re
from typing import List

import click
from crontab import CronTab

from pacelinemonitor.notification import notify
from pacelinemonitor.pacelinespider import search_classifieds

import pathlib


def load_patterns(patternfile) -> List[re.Pattern]:
    with open(patternfile) as reader:
        return [
            re.compile(line[:-1])
            for line in reader if line.strip()
        ]


@click.group()
def cli():
    pass


@cli.command()
@click.option('--patternfile', '-p', default='patterns.txt')
@click.option('--email/--no-email', default=False)
def scrape(patternfile, email):
    patterns = load_patterns(patternfile)
    new_results = search_classifieds(patterns)
    if new_results:
        for res in new_results:
            print(res)
        notify(new_results, no_email=not email)


@cli.command()
def init():
    cwd = pathlib.Path().resolve()
    cron = CronTab()
    cron.remove_all(comment='pacelinemonitor')

    job = cron.new(
        command=f'cd {cwd} && pipenv run entrypoint.py scrape --email',
        comment='pacelinemonitor'
    )
    job.hour.every(1)
    cron.write()


if __name__ == '__main__':
    cli()
