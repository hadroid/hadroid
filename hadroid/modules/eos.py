"""
Gets the EOS status.
"""
import re
import requests
import logging
from bs4 import BeautifulSoup
from hadroid import C

EOSSTATUS_USAGE = '(eosstatus) [--verbose] [--ignore-seen]'


SEEN = {}
def get_eos_last_down_date():
    """Fetch the EOS down status."""
    status_url = C.EOSSTATUS_STATUS_URL
    res = requests.get(status_url)
    if res.ok:
        soup = BeautifulSoup(res.text, 'html.parser')
        eos_incident_link_tag = soup.find(
            'a', {'class': 'csp-menu-match'},
            text=re.compile('EOSPUBLIC down'))
        incident_link = eos_incident_link_tag['href']
        eos_row = eos_incident_link_tag.parent.parent
        if eos_row:
            date = eos_row.find('td', {'class': 'csp-cell-date'}).text.strip()
            return incident_link, date
        else:
            return None


def get_reason():
    """Get the reason."""
    reason_url = C.EOSSTATUS_REASON_URL
    res = requests.get(reason_url)
    if res.ok:
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.find_all('font')[1].text[:-1]


def get_eos_status(verbose=False, ignore_seen=False):
    eos_status = get_eos_last_down_date()
    if eos_status is not None:
        link, date = eos_status
        reason = get_reason()
        if link not in SEEN or ignore_seen:
            SEEN[link] = (date, reason)
            return ":warning:[EOS Down ({date})]({link}). **Reason: {reason}**".format(
                link=link, date=date, reason=reason)
    if verbose:
        return "**EOS: Everything operating smoothly.**"
    return None


def eosstatus(client, args, msg_json):
    status_msg = get_eos_status(verbose=args['--verbose'],
                                ignore_seen=args['--ignore-seen'])
    logging.warning(status_msg)

    if status_msg:
        client.send(status_msg)
