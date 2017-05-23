"""Test the hadroid."""


def test_version():
    """Test version import."""
    from hadroid import __version__
    assert __version__
