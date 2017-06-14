"""CERN Restaurants menu fetching module."""

import requests

from datetime import datetime, timedelta
from dateutil import parser
from collections import defaultdict
from sklearn.externals import joblib
from hadroid import C

SPAM_USAGE = '(spam | s) [<from-date>] [<to-date>]'


def harvest_zenodo_records(from_date=None, to_date=None):
    if not from_date:
        from_date = datetime.now()
    if not to_date:
        to_date = (from_date + timedelta(days=1)).date()
    if isinstance(from_date, datetime):
        from_date = from_date.date()
    if isinstance(to_date, datetime):
        to_date = to_date.date()
    headers = {"Content-Type": "application/json"}
    params = {
        'size': 500,
        'page': 1,
        'q': 'created:[{from_date} TO {to_date}]'.format(from_date=from_date,
                                                         to_date=to_date)
    }
    url = 'https://zenodo.org/api/records'
    records = []
    res = requests.get(url, headers=headers, params=params).json()
    records.extend(res['hits']['hits'])
    while 'next' in res['links']:
        res = requests.get(res['links']['next'], headers=headers).json()
        records.extend(res['hits']['hits'])
    return records


def prepare_features(rec):
    return rec['metadata']['description'] + rec['metadata']['title']


def load_model():
    model_path = C.ZENODO_SPAM_MODEL_PATH
    text_clf = joblib.load(model_path)
    return text_clf


def format_gist_text(res):
    d = defaultdict(lambda: [])
    for r in res:
        owner = r['owners'][0]
        link = r['links']['self']
        title = r['metadata']['title']
        d[owner].append((link, title))

    text = ""
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


def zenodo_spam(client, args, msg_json):
    from_date, to_date = None, None
    if args['<from-date>']:
        from_date = parser.parse(args['<from-date>'])
        if args['<to-date>']:
            to_date = parser.parse(args['<to-date>'])

    record_hits = harvest_zenodo_records(from_date, to_date)
    X = [prepare_features(rec) for rec in record_hits]
    model = load_model()
    y = model.predict(X)
    spams = list(r for r, y in zip(record_hits, y) if y)
    contents = format_gist_text(spams)
    description = "Spam records FROM {0} TO {1}".format(
        str(from_date), str(to_date))
    resp = send_summary_to_gist(contents, description)
    gist_url = resp.json()['html_url']
    client.send("Spam summary at {0}".format(gist_url))
