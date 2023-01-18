import json
import smtplib
from email.mime.text import MIMEText
from typing import List

from pacelinemonitor.conf import SECRETS_FNAME
from pacelinemonitor.pacelinespider import PacelineResult

with open(SECRETS_FNAME) as secretsfp:
    secrets = json.load(secretsfp)
    user = secrets['user']
    pwd = secrets['pwd']
    from_addr = secrets['from']
    to_addr = secrets['to']


def notify(results: List[PacelineResult], no_email=False):
    n = len(results)
    subject = f'PACELINE: {n} new results on your search'
    body = "The following (new) matches were found for your scheduled search:"
    for result in results:
        body += f"\n[{result.thread.thread_id}] {result.pattern} ({result.url})"
    body += "\n\n Thank you for using paceline-monitor® †††"

    msg = MIMEText(body)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject

    if no_email:
        print(msg)
        print(body)
    else:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(user, pwd)
        s.sendmail(from_addr, [to_addr], msg.as_string())
