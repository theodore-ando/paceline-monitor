# paceline-monitor

This tool helps you keep track of the large number of Classified listings that are posted on the
paceline every day. You provide a list of regular expressions, and the monitor will set up an
hourly cron job to check the new listings. If any listing matches any of your patterns, then
you will receive an email with a list of results and links to the threads.

## Install

Use `pipenv` to install: 
```shell
pip3 install --user pipenv
pipenv install 
```

## Setup

### SMTP Server

In order to receive email notifications on the new listings, you must have access to an SMTP
server. Currently, the app is setup to use a gmail app password. If you have another SMTP server
you would like to use, visit [notification.py](pacelinemonitor/notification.py) and amend it to
your needs. Otherwise, follow the below instructions.

First, you must allow an app access to your gmail account. This can be done by visiting
`Account Settings > Security > Signing in to Google`, under this section you will find
`App Passwords`. If you do not see it, this is probably because you have not enabled two-factor
security which honestly you should've enabled already >:(. Create an app password and copy it
somewhere temporarily. It will only be shown to you once, so don't lose it or you'll have to
create it again.

### Credentials

Create a file `secrets.json` in this directory (the top level directory of the repo). Do not fear,
the file is excluded by the `.gitignore`, but do not manually add it or push it. Inside
`secrets.json`, place the following:

```json
{
  "from": "<the email the notification will appear to be from>",
  "to": "<email to receive notifications>",
  "user": "<gmail account>",
  "pwd": "<app password>"
}
```

## Usage

You can invoke the tool by running 
```shell
pipenv run ./entrypoint.py
```
It will show you help messages.

### Specifying your search
Create a file `patterns.txt`. In it, specify the regular expressions you would like to be notified
for, with one per line. Please end the file on a new line. By default, the expressions are
matched insensitive to case. For example if you would like to be given notifications on GRX Di2 
components and i9 wheels, yours might look like:
```
(?=.*grx)(?=.*di2)
(?=.*i9)(?=.*wheel)

```
This type of pattern will match `grx` and `di2` in any position and in either order within the 
text of the post+title irrespective of upper/lower case. 

### Run manually (test)

You can manually run the monitor by invoking the entrypoint script:
```bash
pipenv run ./entrypoint scrape --no-email
```
This will allow you to test out your patterns or email config (by using `--email` instead).

### Create the cron job

```bash
pipenv run ./entrypoint.py init
```

## Caveats

Currently, indefinitely stores a cache of downloaded threads, which you could clear periodically.

Currently, only searches first page of classifieds.  If more than a page appears in an hour then 
you are SoL.
