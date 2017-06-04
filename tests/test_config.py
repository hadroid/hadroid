"""Test the hadroid configuration handling."""


def test_config_loader(env_testconfig):
    from hadroid import C
    assert C.GITTER_PERSONAL_ACCESS_TOKEN == 'xyz'
    assert C.BOT_NAME == 'Hadroid'
