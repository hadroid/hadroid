"""CERN Restaurants menu fetching module."""

import requests

from datetime import datetime, timedelta
from dateutil import parser
from dateutil.tz import tzutc
from collections import defaultdict
from sklearn.externals import joblib
from hadroid import C

SPAM_USAGE = ('(spam | s) (records|communities) [--from=<from-date>] '
              '[--until=<until-date>] [--hours=<hours>] [--days=<days>]'
              '[--silent]')


def as_date(dt):
    return dt.date() if isinstance(dt, datetime) else dt


def parse_date(datestring):
    date = parser.parse(datestring)
    if not date.tzinfo:
        date = datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=date.hour,
            minute=date.minute,
            tzinfo=tzutc())
    return date


def harvest_zenodo_records(from_date, until_date):
    headers = {"Content-Type": "application/json"}
    params = {
        'size': 500,
        'page': 1,
        'q': 'created:[{from_date} TO {until_date}]'.format(
            from_date=as_date(from_date), until_date=as_date(until_date))
    }
    url = 'https://zenodo.org/api/records'
    records = []
    res = requests.get(url, headers=headers, params=params).json()
    records.extend(res['hits']['hits'])
    while 'next' in res['links']:
        res = requests.get(res['links']['next'], headers=headers).json()
        records.extend(res['hits']['hits'])
    return records


def harvest_zenodo_communities(from_date, until_date):
    headers = {"Content-Type": "application/json"}
    params = {
        'size': 500,
        'page': 1
    }
    url = 'https://zenodo.org/api/communities'
    communities = []
    res = requests.get(url, headers=headers, params=params).json()
    communities.extend(res['hits']['hits'])
    while 'next' in res['links']:
        res = requests.get(res['links']['next'], headers=headers).json()
        communities.extend(res['hits']['hits'])
    result = []
    for c in communities:
        created = parse_date(c['created'])
        if from_date <= created and created <= until_date:
            result.append(c)
    return result


def prepare_record_features(rec):
    return rec['metadata']['description'] + rec['metadata']['title']


def prepare_community_features(c):
    return c['description'] + c['title'] + c['curation_policy'] + c['page']


def load_model(model_path):
    text_clf = joblib.load(model_path)
    return text_clf


def format_communities_gist_text(res):
    text = "Found {0} spam communities.\n".format(len(res))
    for r in res:
        link = r['links']['html']
        title = r['title']
        text += "- {0} {1}\n".format(link, title)

    return text


def format_records_gist_text(res):
    d = defaultdict(lambda: [])
    for r in res:
        owner = r['owners'][0]
        link = r['links']['html']
        title = r['metadata']['title']
        d[owner].append((link, title))

    text = "Found {0} spam records.\n".format(len(res))
    for user, rec_links in d.items():
        text += "- User: {0}\n".format(user)
        for url, title in rec_links:
            text += '  - {0} ("{1}..")\n'.format(url, title[:25])
    return text


def send_summary_to_gist(contents, description):
    headers = {
        'Authorization': 'token {token}'.format(token=C.GITHUT_GIST_TOKEN),
        'Accept': 'application/vnd.github.v3+json',
    }

    url = 'https://api.github.com/gists'
    data = {
        'description': description,
        'public': False,
        'files': {
            'records_spam.md': {
                'content': contents
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response


def time_params_to_dates(args):
    now = datetime.now(tz=tzutc())
    if args['--hours'] or args['--days']:
        if args['--days']:
            hours = int(args['--days']) * 24
        else:
            hours = int(args['--hours'])
        until_date = now
        from_date = until_date - timedelta(hours=hours)
    else:
        if args['--from']:
            from_date = parse_date(args['--from'])
            if args['--until']:
                until_date = parse_date(args['--until'])
            else:
                until_date = now
        else:
            until_date = now
            from_date = until_date - timedelta(days=1)
    return from_date, until_date


def zenodo_spam(client, args, msg_json):
    from_date, until_date = time_params_to_dates(args)
    if args['records']:
        # Records API is not upper-bound inclusive.
        # We need to bump one day if user did not specify upper time bound
        # in order to get records from today
        if not args['--until']:
            until_date = until_date + timedelta(days=1)
        hits = harvest_zenodo_records(from_date, until_date)
        X = [prepare_record_features(rec) for rec in hits]
        model = load_model(C.ZENODO_RECORDS_SPAM_MODEL_PATH)
        y = model.predict(X)
        spam = list(r for r, y in zip(hits, y) if y)
        contents = format_records_gist_text(spam)
        description = "Spam records FROM {0} TO {1}".format(
            str(from_date), str(until_date))
    else:
        hits = harvest_zenodo_communities(from_date, until_date)
        X = [prepare_community_features(rec) for rec in hits]
        model = load_model(C.ZENODO_COMMUNITIES_SPAM_MODEL_PATH)
        y = model.predict(X)
        spam = list(r for r, y in zip(hits, y) if y)
        contents = format_communities_gist_text(spam)
        description = "Spam communities FROM {0} TO {1}".format(
            str(from_date), str(until_date))

    if spam:
        resp = send_summary_to_gist(contents, description)
        gist_url = resp.json()['html_url']
        client.send("Spam summary at {0}".format(gist_url))
    elif not args['--silent']:
        client.send("No spam found.")
