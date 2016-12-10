"""
{header}

Usage:
{usage}

Examples:
{examples}

Options:
{options}
"""


from hadroid import __version__, C

# Patch the docstring
__doc__ = __doc__.format(header=C.DOC_HEADER,
                         usage=C.DOC_USAGE,
                         examples=C.DOC_EXAMPLES,
                         options=C.DOC_OPTIONS)


def bot_main(client, args, msg_json=None):
    """Main bot function."""
    for m in C.MODULES:
        if any(args[name] for name in m.names):
            m.main(client, args, msg_json)


if __name__ == "__main__":
    """When executed directly, use a console client."""
    from docopt import docopt
    from hadroid.client import StdoutClient
    args = docopt(__doc__, version=__version__)
    bot_main(StdoutClient(), args)
