import json
import smtplib
from email.mime.text import MIMEText
from typing import List

from pacelinemonitor.pacelinethread import PacelineThread

with open("secrets.json") as secretsfp:
    secrets = json.load(secretsfp)
    user = secrets['user']
    pwd = secrets['pwd']
    from_addr = secrets['from']
    to_addr = secrets['to']


def notify(results: List[PacelineThread], no_email=False):
    n = len(results)
    subject = f'PACELINE: {n} new results on your search'
    body = "The following (new) matches were found for your scheduled search:"
    for result in results:
        body += f"\n[{result.thread_id}] {result.title} ({result.link})"
    body += "\n Thank you for using paceline-monitor® †††"

    msg = MIMEText(body)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject

    if no_email:
        print(msg)
    else:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(user, pwd)
        s.sendmail(from_addr, [to_addr], msg.as_string())