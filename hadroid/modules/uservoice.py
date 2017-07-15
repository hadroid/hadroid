"""Uservoice module.

Config:

    USERVOICE_SUBDOMAIN_NAME = 'zenodo'
    USERVOICE_API_KEY = 'CHANGEME'
    USERVOICE_API_SECRET = 'CHANGEME'

    USERVOICE_ADMINS = {
        'slint': 'Alex',
        'krzysztof': 'Krzysztof',
    }
"""
from collections import Counter, defaultdict
from datetime import datetime
from operator import itemgetter
from urllib.parse import urlencode

import fuzzywuzzy.process as fuzzy_match
from uservoice import Client

from hadroid import C

USERVOICE_USAGE = '(uservoice | u) stats'


class UservoiceClient:

    def __init__(self, subdomain=None, key=None, secret=None):
        self._client = Client(
            subdomain or C.USERVOICE_SUBDOMAIN_NAME,
            key or C.USERVOICE_API_KEY,
            secret or C.USERVOICE_API_SECRET)

    def _parse_uservoice_date(self, datestr):
        # Format: 2017/06/12 18:57:48 +0000
        return datetime.strptime(datestr[:10], '%Y/%m/%d')

    def fetch_tickets(self, state='open', count=100):
        with self._client.login_as_owner() as client:
            querystring = urlencode({
                'sort': 'newest',
                'per_page': count,
                'state': state,
            })
            tickets = client.get('/api/v1/tickets.json?{}'.format(querystring))
            return tickets.get('tickets', [])

    def extract_assigned_tickets(self, tickets):
        """Get tickets assigned to admins through Notes (eg. 'FOR JEFF')."""
        stats = defaultdict(list)
        tickets_with_notes = sorted([t for t in tickets if t.get('notes')],
                                    key=itemgetter('last_message_at'))
        for ticket in tickets_with_notes:
            notes_text = ' '.join((note.get('body', '')
                                   for note in ticket.get('notes', [])))
            search_terms = {k: (k, v) for k, v in C.USERVOICE_ADMINS.items()}
            match = fuzzy_match.extractOne(notes_text, search_terms)
            if match:
                stats[match[2]].append(ticket)
        return stats

    def extract_ticket_stats(self, tickets):
        """Return ticket age stats."""
        today = datetime.now()

        def week_offset(t):
            delta = today - self._parse_uservoice_date(t['last_message_at'])
            return int(delta.days / 7)

        weekly_counts = Counter(map(week_offset, tickets))
        return (
            ('w', weekly_counts.get(0, 0)),
            ('m', sum(n for w, n in weekly_counts.items() if 1 <= w <= 3)),
            ('>m', sum(n for w, n in weekly_counts.items() if w > 3)),
        )

    def generate_support_report(self):
        tickets = self.fetch_tickets()
        assignments = self.extract_assigned_tickets(tickets)
        ticket_stats = self.extract_ticket_stats(tickets)
        return {
            'tickets': tickets,
            'stats': ticket_stats,
            'assignments': assignments,
        }


def support_report_to_markdown(report):
    content = []

    # Format header using ticket stats
    stats = report.get('stats', {})
    age_str = ' | '.join(('{}: {}'.format(l, c) for l, c in stats))
    content.append(
        '### {} Tickets ({})'.format(len(report.get('tickets', [])), age_str))

    # Format assignment stats
    for gh_user, tickets in report.get('assignments', {}).items():
        content.append('\n**{} (@{})**\n'.format(
                       C.USERVOICE_ADMINS[gh_user], gh_user))
        for ticket in tickets:
            content.append(
                '- [{subject} ({contact[name]})]({url}) - {last_message_at}'
                .format(**ticket))

    return '\n'.join(content)


def uservoice(client, args, msg_json):
    if args['stats']:
        uservoice_client = UservoiceClient()
        report = uservoice_client.generate_support_report()
        message = support_report_to_markdown(report)
        client.send(message)
