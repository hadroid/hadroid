"""Test the hadroid."""

from hadroid.modules.uservoice import Ticket, TicketList, \
    aggregate_assignments_by_user, generate_summary, summary_to_markdown


def test_ticket_note_match_assignment():
    """Test matching the assignment to a note body."""

    # Simple testcases
    assert Ticket.match('', ['user1', ]) is None
    assert Ticket.match('@user1', ['user1', ]) == ('user1', '')
    assert Ticket.match('@user1    ', ['user1', ]) == ('user1', '')
    assert Ticket.match('@user1 Foo baz', ['user1', ]) == ('user1', 'Foo baz')
    assert Ticket.match('@user1    Foo baz    ', ['user1', ]) == \
        ('user1', 'Foo baz')
    assert Ticket.match(' @u1  Foo baz  <br>Bar', ['u1', ]) == \
        ('u1', 'Foo baz')

    # Test multi-user matching with HTML body
    note_body = ("Some text before <br><br>"
                 "@user1 First user text<br>"
                 "Some text below<br><br>"
                 "@user1 More text below<br>")
    assert Ticket.match(note_body, ['user1', ]) == ('user1', 'First user text')
    assert Ticket.match(note_body, ['user2', ]) is None

    note_body = ("Some text before <br><br>"
                 "@user1 User1 is first<br>"
                 "Some text below<br><br>"
                 "@user2 User2 assigned later<br>")

    assert Ticket.match(note_body, ['user2', 'user1', ]) == \
        ('user1', 'User1 is first')

    assert Ticket.match(note_body, ['user2', ]) == \
        ('user2', 'User2 assigned later')


def test_ticket_note_find_assignment():
    """Test finding the first assignment in the ticket's notes."""
    t = Ticket({})
    assert t.match_first([]) is None
    assert t.match_first(['user1', 'user2']) is None
    notes = [
        {
            'id': 100,
            'body': '@user1 foo',
            'created_at': '2017/09/08 09:00:05 +0000'
        },
        {
            'id': 101,
            'body': '@user2 bar',
            'created_at': '2017/09/08 09:00:06 +0000'
        },
        {
            'id': 102,
            'body': 'Hello',
            'created_at': '2017/09/08 09:00:07 +0000'
        },
    ]
    t = Ticket({'notes': notes})
    assert t.match_first(['user3', ]) is None
    assert t.match_first(['user1', 'user2']) == \
        (101, 'user2', 'bar')


def test_ticket_get_note_by_id():
    """Test fetching the note by its ID."""
    notes = [
        {
            'id': 100,
            'body': 'Foo',
            'created_at': '2017/09/08 09:00:05 +0000'
        },
        {
            'id': 101,
            'body': 'Bar',
            'created_at': '2017/09/08 09:00:06 +0000'
        },
    ]
    t = Ticket({'notes': notes})
    assert t.get_note_by_id(100) == notes[0]
    assert t.get_note_by_id(101) == notes[1]
    assert t.get_note_by_id(102) is None


def test_tickets_match_assignments():
    """Test matching the assignments for all tickets."""
    tickets = [
        {
            'id': 1000,
            'notes': [
                {
                    'id': 100,
                    'body': '@user1 Foo',
                    'created_at': '2017/09/08 09:00:05 +0000'
                }
            ]
        },
        {
            'id': 2000,
            'notes': [
                {
                    'id': 200,
                    'body': '@user2 Bar',
                    'created_at': '2017/09/08 09:00:05 +0000'
                }
            ]
        },
        {
            'id': 3000,
            'notes': [
                {
                    'id': 300,
                    'body': 'Baz',
                    'created_at': '2017/09/08 09:00:05 +0000'
                }
            ]
        },
    ]
    tl = TicketList(tickets)
    assigned, unassigned = tl.match_assignments(['user1', 'user2'])

    assert set(assigned) == set([(1000, 100, 'user1', 'Foo'),
                                 (2000, 200, 'user2', 'Bar'), ])
    assert unassigned == [3000, ]


def test_aggregate_assignments():
    """Test assignment aggregation by the primary username."""
    assignments = [
        (1, 10, 'user1', 'A'),
        (2, 20, 'user2', 'B'),
        (3, 30, 'u2', 'C'),
        (4, 40, 'u1', 'D'),
        (5, 50, 'user3', 'E'),
        (6, 60, 'username3', 'F'),
    ]
    mapping = {
        'user1': 'user1',
        'u1': 'user1',
        'user2': 'user2',
        'u2': 'user2',
        'username3': 'user3',
        'user3': 'user3',
    }
    ret = aggregate_assignments_by_user(assignments, mapping)
    assert ret == {
        'user1': [(1, 'A'), (4, 'D')],
        'user2': [(2, 'B'), (3, 'C')],
        'user3': [(5, 'E'), (6, 'F')],
    }


def test_generate_summary_and_markdown():
    """Test summary generation."""
    tickets = [
        {
            'id': 1,
            'subject': 'Subject one',
            'url': 'https://foo.uservoice.com/admin/tickets/1',
            'last_message_at': '2017/09/04 17:04:53 +0000',
            'contact': {'name': 'Jane Smith'},
            'notes': [
                {
                    'id': 10,
                    'body': '@user1 Foo',
                    'created_at': '2017/09/08 09:00:05 +0000'
                }
            ]
        },
        {
            'id': 2,
            'subject': 'Subject two',
            'url': 'https://foo.uservoice.com/admin/tickets/2',
            'last_message_at': '2017/09/03 17:04:53 +0000',
            'contact': {'name': 'John Doe'},
            'notes': [
                {
                    'id': 20,
                    'body': '@user2 Bar',
                    'created_at': '2017/09/08 09:00:05 +0000'
                }
            ]
        },
        {
            'id': 3,
            'subject': 'Subject three',
            'url': 'https://foo.uservoice.com/admin/tickets/3',
            'last_message_at': '2017/09/01 17:04:53 +0000',
            'contact': {'name': 'Foo Smith'},
            'notes': [
                {
                    'id': 30,
                    'body': '@u2 Bar',
                    'created_at': '2017/09/08 09:00:05 +0000'
                }
            ]
        },
        {
            'id': 4,
            'subject': 'Subject four',
            'url': 'https://foo.uservoice.com/admin/tickets/4',
            'last_message_at': '2017/08/04 17:04:53 +0000',
            'contact': {'name': 'Jim Doe'},
            'notes': [
                {
                    'id': 40,
                    'body': 'Baz',
                    'created_at': '2017/09/08 09:00:05 +0000'
                }
            ]
        },
        {
            'id': 5,
            'subject': 'Subject five',
            'url': 'https://foo.uservoice.com/admin/tickets/5',
            'last_message_at': '2017/05/04 17:04:53 +0000',
            'contact': {'name': 'Bob Bob'},
            'notes': [
                {
                    'id': 50,
                    'body': 'Baz',
                    'created_at': '2017/09/08 09:00:05 +0000'
                }
            ]
        },
    ]
    usernames_config = [
        (('user1', 'u1'), "User one"),
        (('user2', 'u2'), "User two"),
    ]
    summary = generate_summary(tickets, usernames_config)
    assert summary == {
        "stats": [
            ("This week", 2),
            ("Week+ old", 1),
            ("Month+ old", 2)
        ],
        "assignments": {
            "user1": [
                (1, "Foo")
            ],
            "user2": [
                (2, "Bar"),
                (3, "Bar")
            ]
        },
        "unassigned": [
            4,
            5
        ]
    }

    markdown = summary_to_markdown(tickets, summary)
    out = (
        "### 5 Tickets (This week: 2 | Week+ old: 1 | Month+ old: 2)\n"
        "\n**@user1 - 1 ticket(s):**\n\n"
        "- [Subject one (Jane Smith)](https://foo.uservoice.com/admin/"
        "tickets/1) - 2017/09/04 17:04:53 +0000\n"
        "   - Foo\n"
        "\n**@user2 - 2 ticket(s):**\n\n"
        "- [Subject two (John Doe)](https://foo.uservoice.com/admin/tickets/2)"
        " - 2017/09/03 17:04:53 +0000\n"
        "   - Bar\n"
        "- [Subject three (Foo Smith)](https://foo.uservoice.com/admin/"
        "tickets/3) - 2017/09/01 17:04:53 +0000\n"
        "   - Bar\n"
        "\n**@\\all - 2 unassigned ticket(s):**\n\n"
        "- [Subject four (Jim Doe)](https://foo.uservoice.com/admin/tickets/4)"
        " - 2017/08/04 17:04:53 +0000\n"
        "- [Subject five (Bob Bob)](https://foo.uservoice.com/admin/tickets/5)"
        " - 2017/05/04 17:04:53 +0000\n"
    )
    assert markdown == out
