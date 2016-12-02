"""Patched version of docopt."""


def docopt_parse(doc, argv=None, version=None):
    import docopt as _docopt

    def extras_patch(help, version, options, doc):
        """Patch of docopt.extra handler.

        Patch for docopt's 'extras' function is needed, as it is hard
        sys-exiting the bot after '--help/-h' or '--version' commands
        """
        exc = None
        if help and any((o.name in ('-h', '--help')) and o.value
                        for o in options):
            exc = _docopt.DocoptExit()
            exc.args = (doc.strip("\n"), )
        if version and any(o.name == '--version' and o.value for o in options):
            exc = _docopt.DocoptExit()
            exc.args = (version, )
        if exc is not None:
            raise exc

    # Apply the patch above to docopt.extras
    _docopt.extras = extras_patch
    return _docopt.docopt(doc, argv=argv, version=version)
