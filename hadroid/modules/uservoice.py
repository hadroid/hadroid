"""Uservoice module.

Config:

    USERVOICE_SUBDOMAIN_NAME = 'zenodo'
    USERVOICE_API_KEY = 'CHANGEME'
    USERVOICE_API_SECRET = 'CHANGEME'

    USERVOICE_ADMINS = [
        ('slint', 'Alex', ('alex',)),
        ('krzysztof', 'Krzysztof' ('kn', )),
    ]
"""
from collections import Counter, defaultdict
from datetime import datetime
from operator import itemgetter
from urllib.parse import urlencode

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
        """Fetch the ticket list from Uservoice."""
        with self._client.login_as_owner() as client:
            querystring = urlencode({
                'sort': 'newest',
                'per_page': count,
                'state': state,
            })
            tickets = client.get('/api/v1/tickets.json?{}'.format(querystring))
            return tickets.get('tickets', [])

    def _match_assignee(self, note_body):
        for admin_gh, name, aliases in C.USERVOICE_ADMINS:
            names = (admin_gh, ) + aliases
            matched_name = next((name for name in names if '@{0}'.format(name)
                                 in note_body), None)
            if matched_name:
                a_idx = note_body.index(matched_name)
                msg = note_body[a_idx + len(matched_name):]
                b_idx = msg.find('\n') if '\n' in msg else -1
                msg = msg[:b_idx]
                return msg, admin_gh

    def extract_assigned_tickets(self, tickets):
        """Get tickets assigned to admins through notes (eg. '@kn')."""
        stats = defaultdict(list)
        tickets_with_notes = sorted([t for t in tickets if t.get('notes')],
                                    key=itemgetter('last_message_at'))
        assigned_ticket_ids = []
        for ticket in tickets_with_notes:
            notes = sorted([n for n in ticket.get('notes')],
                           key=itemgetter('created_at'), reverse=True)
            assign_info = next((r for r in
                                (self._match_assignee(n.get('body'))
                                 for n in notes) if r), None)
            if assign_info:
                msg, admin_gh = assign_info
                ticket['admin_msg'] = msg
                stats[admin_gh].append(ticket)
                assigned_ticket_ids.append(ticket['id'])
        unassigned = [t for t in tickets if t['id'] not in assigned_ticket_ids]
        stats['/all'] = unassigned
        return stats

    def extract_ticket_stats(self, tickets):
        """Return ticket age stats."""
        today = datetime.now()

        def week_offset(t):
            delta = today - self._parse_uservoice_date(t['last_message_at'])
            return int(delta.days / 7)

        weekly_counts = Counter(map(week_offset, tickets))
        return (
            ('This week', weekly_counts.get(0, 0)),
            ('Week+ old', sum(n for w, n in weekly_counts.items()
                              if 1 <= w <= 3)),
            ('Month+ old', sum(n for w, n in weekly_counts.items() if w > 3)),
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
    gh2name = dict((gh, name) for gh, name, _ in C.USERVOICE_ADMINS)
    for gh_user, tickets in report.get('assignments', {}).items():
        content.append('\n**{} (@{}) - {} ticket(s):**\n'.format(
                       gh2name[gh_user], gh_user, len(tickets)))
        for ticket in tickets:
            msg = ('- [{subject} ({contact[name]})]({url}) - {last_message_at}'
                   .format(**ticket))
            if 'admin_msg' in ticket:
                msg += '\n   -{0}'.format(ticket['admin_msg'])
            content.append(msg)

    return '\n'.join(content)


def uservoice(client, args, msg_json):
    if args['stats']:
        uservoice_client = UservoiceClient()
        report = uservoice_client.generate_support_report()
        message = support_report_to_markdown(report)
        client.send(message)
