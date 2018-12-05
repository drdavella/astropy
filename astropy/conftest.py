# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This file contains pytest configuration settings that are astropy-specific
(i.e.  those that would not necessarily be shared by affiliated packages
making use of astropy's test runner).
"""
import builtins
from importlib.util import find_spec

import py.path

from astropy.tests.plugins.display import PYTEST_HEADER_MODULES
from astropy.tests.helper import enable_deprecations_as_exceptions

try:
    import matplotlib
except ImportError:
    HAS_MATPLOTLIB = False
else:
    HAS_MATPLOTLIB = True

if find_spec('asdf') is not None:
    from asdf import __version__ as asdf_version
    if asdf_version >= '2.3.0':
        pytest_plugins = ['asdf.tests.schema_tester']
        PYTEST_HEADER_MODULES['Asdf'] = 'asdf'

enable_deprecations_as_exceptions(
    include_astropy_deprecations=False,
    # This is a workaround for the OpenSSL deprecation warning that comes from
    # the `requests` module. It only appears when both asdf and sphinx are
    # installed. This can be removed once pyopenssl 1.7.20+ is released.
    modules_to_ignore_on_import=['requests'])

if HAS_MATPLOTLIB:
    matplotlib.use('Agg')

matplotlibrc_cache = {}


def pytest_ignore_collect(path, config):
    asdf_path = py.path.local(os.path.join(os.path.dirname(__file__), 'io', 'misc', 'asdf'))
    if path.common(asdf_path) != asdf_path:
        return False

    try:
        import asdf
        from distutils.version import LooseVersion
        # Only skip if we don't have a sufficiently recent version of ASDF
        return LooseVersion(asdf.__version__) < LooseVersion('2.3.0')
    except ImportError:
        pass

    # If we make it here, then skip all tests at this level and below
    return True

def pytest_configure(config):
    builtins._pytest_running = True
    # do not assign to matplotlibrc_cache in function scope
    if HAS_MATPLOTLIB:
        matplotlibrc_cache.update(matplotlib.rcParams)
        matplotlib.rcdefaults()


def pytest_unconfigure(config):
    builtins._pytest_running = False
    # do not assign to matplotlibrc_cache in function scope
    if HAS_MATPLOTLIB:
        matplotlib.rcParams.update(matplotlibrc_cache)
        matplotlibrc_cache.clear()


PYTEST_HEADER_MODULES['Cython'] = 'cython'
