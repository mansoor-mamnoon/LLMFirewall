from prompt_injection_lab.version import __version__


def test_version_exists():
    assert isinstance(__version__, str)
    assert __version__.count(".") == 2
