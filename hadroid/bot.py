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
usage_str = "\n".join(("    @{0} {1}".format(C.BOT_NAME,
                                             m.usage or m.names[0])
                       for m in C.MODULES))
__doc__ = __doc__.format(botname=C.BOT_NAME,
                         usage=usage_str,
                         header=C.DOC_HEADER.format(botname=C.BOT_NAME),
                         examples=C.DOC_EXAMPLES.format(botname=C.BOT_NAME),
                         options=C.DOC_OPTIONS.format(botname=C.BOT_NAME))


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
