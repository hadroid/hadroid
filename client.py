"""Base Client classes."""


class Client(object):
    """Base communication client."""

    def send(self, msg, *args, **kwargs):
        """Send a message to a destination."""
        raise NotImplementedError


class StdoutClient(Client):
    """Simple client for printing to console."""

    def send(self, msg, *args, **kwargs):
        """Send a message to standard output."""
        print(msg)
