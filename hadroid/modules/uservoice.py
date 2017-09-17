"""Uservoice module.

Config:

    USERVOICE_SUBDOMAIN_NAME = 'zenodo'
    USERVOICE_API_KEY = 'CHANGEME'
    USERVOICE_API_SECRET = 'CHANGEME'

    USERVOICE_ADMINS = [
        (('slint', 'alex'), 'Alex'),
        (('krzysztof', 'kn'), 'Krzysztof'),
    ]
"""
from collections import Counter
from datetime import datetime
from operator import itemgetter
from urllib.parse import urlencode

import requests
from cached_property import cached_property
from dateutil.parser import parse
from uservoice import Client

from hadroid import C

USERVOICE_USAGE = '(uservoice | u)'


class Ticket(object):
    """Uservoice ticket class."""

    def __init__(self, ticket):
        """Constructor."""
        self.ticket = ticket

    @cached_property
    def notes(self):
        """Return notes sorted by created date."""
        return sorted(self.ticket.get('notes', []),
                      key=itemgetter('created_at'), reverse=True)

    @cached_property
    def id(self):
        return self.ticket['id']

    @cached_property
    def last_message_at(self):
        return parse(self.ticket['last_message_at'])

    def get_note_by_id(self, id_):
        """Get the note by its ID."""
        return next((n for n in self.notes if n['id'] == id_), None)

    @staticmethod
    def match(note_body, usernames):
        """
        Match the first assigment line in the note body (None otherwise).

        Return the matching username and the follow-up assignment text
        (sliced until first <br> tag and stripped of trailing whitespaces).

        Examples:
        >>> Ticket.match('@u1 foo <br>@u2 bar', ['u1', 'u2'])
        ('u1', 'foo')

        :param str note_body: HTMP body of the note.
        :param list usernames: list of users to match for.
        :return: Tuple with matched_username and assignment text
        """
        matches = [(note_body.index('@' + u), u) for u in usernames
                   if ('@' + u) in note_body]
        if not matches:
            return None
        idx, name = min(matches, key=lambda x: x[0])
        msg = note_body[idx + len(name) + 1:]
        b_idx = msg.find('<br>') if '<br>' in msg else None
        if b_idx is not None:
            msg = msg[:b_idx].strip()
        else:
            msg = msg.strip()
        return name, msg

    def match_first(self, usernames):
        """
        Match the first note which has an assignment (None otherwise).

        Return the note ID and the same info as Ticket.match:

        (123, 'u1', 'foo') == Ticket.match_first(t['notes'], ['u1'])

        """
        for note in self.notes:
            a_info = Ticket.match(note.get('body'), usernames)
            if a_info:
                username, msg = a_info
                return (note['id'], username, msg)


class TicketList(object):
    """Uservoice tickets list class."""

    def __init__(self, tickets):
        self.tickets = tickets

    def get_ticket_by_id(self, id_):
        """Get the ticket by its ID."""
        return next((t for t in self.tickets if t['id'] == id_), None)

    def get_ticket_stats(self):
        """Return ticket age stats."""
        today = datetime.utcnow()

        def week_offset(t):
            t_last_msg = parse(t['last_message_at'])
            t_last_msg = t_last_msg.replace(tzinfo=None)
            delta = today - t_last_msg
            return int(delta.days / 7)

        weekly_counts = Counter(map(week_offset, self.tickets))
        return [
            ('This week', weekly_counts.get(0, 0)),
            ('Week+ old', sum(n for w, n in weekly_counts.items()
                              if 1 <= w <= 3)),
            ('Month+ old', sum(n for w, n in weekly_counts.items() if w > 3)),
        ]

    def match_assignments(self, usernames):
        """Match tickets assigned to usernames through notes."""
        assignments = []
        unassigned = []
        for t_ in self.tickets:
            t = Ticket(t_)
            m = t.match_first(usernames)
            if m:
                note_id, username, msg = m
                assignments.append((t.id, note_id, username, msg))
            else:
                unassigned.append(t.id)
        return assignments, unassigned


def fetch_tickets(subdomain=None, key=None, secret=None, state='open',
                  count=100):
    """Fetch the ticket list from Uservoice."""

    uv_client = Client(subdomain or C.USERVOICE_SUBDOMAIN_NAME,
                       key or C.USERVOICE_API_KEY,
                       secret or C.USERVOICE_API_SECRET)
    with uv_client.login_as_owner() as uv_client:
        querystring = urlencode({
            'sort': 'newest',
            'per_page': count,
            'state': state,
        })
        tickets = uv_client.get('/api/v1/tickets.json?{}'.format(querystring))
        return tickets.get('tickets', [])


def aggregate_assignments_by_user(assignments, username_mapping):
    """Aggregates a flat list of ticket assignments per user."""
    data = {}
    for t_id, n_id, username, msg in assignments:
        gh_name = username_mapping[username]
        data.setdefault(gh_name, []).append((t_id, msg))
    return data


def generate_summary(tickets, usernames_config):
    # Create a flat list of all names for matching
    # and a mapping back to the primary (Gitter) username
    usernames = []
    mapping = {}
    for names, label in usernames_config:
        usernames.extend(names)
        for name in names:
            mapping[name] = names[0]

    tl = TicketList(tickets)
    assignments, unassigned = tl.match_assignments(usernames)
    aggregated = aggregate_assignments_by_user(assignments, mapping)
    ticket_stats = tl.get_ticket_stats()
    return {
        'stats': ticket_stats,
        'assignments': aggregated,
        'unassigned': unassigned,
    }


def summary_to_markdown(tickets, summary):
    content = []
    # Format header using ticket stats
    stats = summary.get('stats', {})
    age_str = ' | '.join(('{}: {}'.format(l, c) for l, c in stats))
    content.append(
        '### {} Tickets ({})'.format(len(tickets), age_str))

    tl = TicketList(tickets)
    # Format assignment stats
    assignments = sorted(summary.get('assignments', {}).items(),
                         key=lambda x: x[0])
    for username, assigned_tickets in assignments:
        content.append('\n**@{} - {} ticket(s):**\n'.format(
                       username, len(assigned_tickets)))
        for tid_msg in assigned_tickets:
            tid, msg = tid_msg
            ticket = tl.get_ticket_by_id(tid)
            t = Ticket(ticket)
            line = (
                '- [{subject} ({contactname})]({url}) - {last_msg_at}'
                .format(
                    subject=ticket['subject'],
                    contactname=ticket['contact']['name'],
                    url=ticket['url'],
                    last_msg_at=str(t.last_message_at.strftime('%d %B %Y'))
                    )
            )
            if msg:
                line += '\n   - {0}'.format(msg)
            content.append(line)
    unassigned = summary.get('unassigned', [])
    if unassigned:
        content.append('\n**@\\all - {} unassigned ticket(s):**\n'.format(
            len(unassigned)))
    for tid in unassigned:
        ticket = tl.get_ticket_by_id(tid)
        t = Ticket(ticket)
        line = (
            '- [{subject} ({contactname})]({url}) - {last_msg_at}'
            .format(
                subject=ticket['subject'],
                contactname=ticket['contact']['name'],
                url=ticket['url'],
                last_msg_at=str(t.last_message_at.strftime('%d %B %Y'))
                )
        )
        content.append(line)

    return '\n'.join(content) + '\n'


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


def uservoice(client, args, msg_json):
    tickets = fetch_tickets()
    username_config = C.USERVOICE_ADMINS
    summary = generate_summary(tickets, username_config)
    message = summary_to_markdown(tickets, summary)
    if len(message) < 4000:  # Approx. Gitter limit
        client.send(message)
    else:
        resp = send_summary_to_gist(message, "Uservoice report.")
        gist_url = resp.json()['html_url']
        client.send("Uservoice report too long. Available at {0}".format(
            gist_url))
