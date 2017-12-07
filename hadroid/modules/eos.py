"""
Gets the EOS status.
"""
import re
import requests
import logging
from bs4 import BeautifulSoup
from hadroid import C

EOS_USAGE = 'eos (status|snow) [--verbose] [--ignore-seen]'


SEEN = {}
IS_DOWN = False
def get_eos_last_down_date():
    """Fetch the EOS down status."""
    status_url = C.EOS_STATUS_URL
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
    reason_url = C.EOS_REASON_URL
    res = requests.get(reason_url)
    if res.ok:
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.find_all('font')[1].text[:-1]


def get_eos_status(verbose=False, ignore_seen=False):
    res = requests.get(C.EOS_SERVICE_BOARD_URL)
    is_down = 'EOSPUBLIC&lt;/font&gt;\t Availability: 0' in res.text
    msg = None
    logging.info(is_down)
    if is_down and (not IS_DOWN or ignore_seen) :
        reason = get_reason()
        msg = ":warning:EOS Down. **Possible reason: {reason}**".format(
            reason=reason)
        IS_DOWN = True
    else:
        IS_DOWN = False
    if not is_down and verbose:
        msg = "**EOS: Everything operating smoothly.**"
    return msg


def get_eos_snow_ticket(verbose=False, ignore_seen=False):
    eos_status = get_eos_last_down_date()
    if eos_status is not None:
        link, date = eos_status
        reason = get_reason()
        if link not in SEEN or ignore_seen:
            SEEN[link] = (date, reason)
            return ":warning:[EOS Down ({date})]({link}). **Official reason: {reason}**".format(
                link=link, date=date, reason=reason)
    if not is_down and verbose:
        return "**EOS: Everything operating smoothly.**"
    return None


def eos(client, args, msg_json):
    if args['snow']:
        msg = get_eos_snow_ticket(verbose=args['--verbose'],
                                  ignore_seen=args['--ignore-seen'])
    elif args['status']:
        msg = get_eos_status(verbose=args['--verbose'],
                             ignore_seen=args['--ignore-seen'])

    if msg:
        logging.info(msg)
        client.send(msg)
