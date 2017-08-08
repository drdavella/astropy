import pytest

def pytest_addoption(parser):
    parser.addoption('--hi-guys', action='store_true', help='pretty much useless')

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    print("OH NO")
    config.args.append('astropy')
