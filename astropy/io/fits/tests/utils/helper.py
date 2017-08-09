# Licensed under a 3-clause BSD style license - see PYFITS.rst
from __future__ import division  # confidence high

import os
import shutil
import stat
import tempfile
import time
import numpy as np

from astropy.io import fits
from astropy.io.fits.util import decode_ascii


def comparefloats(a, b):
    """
    Compare two float scalars or arrays and see if they are consistent

    Consistency is determined ensuring the difference is less than the
    expected amount. Return True if consistent, False if any differences.
    """

    aa = a
    bb = b
    # compute expected precision
    if aa.dtype.name == 'float32' or bb.dtype.name == 'float32':
        precision = 0.000001
    else:
        precision = 0.0000000000000001
    precision = 0.00001  # until precision problem is fixed in astropy.io.fits
    diff = np.absolute(aa - bb)
    mask0 = aa == 0
    masknz = aa != 0.
    if np.any(mask0):
        if diff[mask0].max() != 0.:
            return False
    if np.any(masknz):
        if (diff[masknz] / np.absolute(aa[masknz])).max() > precision:
            return False
    return True


def comparerecords(a, b):
    """
    Compare two record arrays

    Does this field by field, using approximation testing for float columns
    (Complex not yet handled.)
    Column names not compared, but column types and sizes are.
    """

    nfieldsa = len(a.dtype.names)
    nfieldsb = len(b.dtype.names)
    if nfieldsa != nfieldsb:
        print("number of fields don't match")
        return False
    for i in range(nfieldsa):
        fielda = a.field(i)
        fieldb = b.field(i)
        if fielda.dtype.char == 'S':
            fielda = decode_ascii(fielda)
        if fieldb.dtype.char == 'S':
            fieldb = decode_ascii(fieldb)
        if (not isinstance(fielda, type(fieldb)) and not
            isinstance(fieldb, type(fielda))):
            print("type(fielda): ", type(fielda), " fielda: ", fielda)
            print("type(fieldb): ", type(fieldb), " fieldb: ", fieldb)
            print('field {0} type differs'.format(i))
            return False
        if len(fielda) and isinstance(fielda[0], np.floating):
            if not comparefloats(fielda, fieldb):
                print("fielda: ", fielda)
                print("fieldb: ", fieldb)
                print('field {0} differs'.format(i))
                return False
        elif (isinstance(fielda, fits.column._VLF) or
              isinstance(fieldb, fits.column._VLF)):
            for row in range(len(fielda)):
                if np.any(fielda[row] != fieldb[row]):
                    print('fielda[{0}]: {1}'.format(row, fielda[row]))
                    print('fieldb[{0}]: {1}'.format(row, fieldb[row]))
                    print('field {0} differs in row {1}'.format(i, row))
        else:
            if np.any(fielda != fieldb):
                print("fielda: ", fielda)
                print("fieldb: ", fieldb)
                print('field {0} differs'.format(i))
                return False
    return True


class FitsTestCase(object):
    def setup(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '../data')
        self.temp_dir = tempfile.mkdtemp(prefix='fits-test-')

        # Restore global settings to defaults
        # TODO: Replace this when there's a better way to in the config API to
        # force config values to their defaults
        fits.conf.enable_record_valued_keyword_cards = True
        fits.conf.extension_name_case_sensitive = False
        fits.conf.strip_header_whitespace = True
        fits.conf.use_memmap = True

    def teardown(self):
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            tries = 3
            while tries:
                try:
                    shutil.rmtree(self.temp_dir)
                    break
                except OSError:
                    # Probably couldn't delete the file because for whatever
                    # reason a handle to it is still open/hasn't been
                    # garbage-collected
                    time.sleep(0.5)
                    tries -= 1

        fits.conf.reset('enable_record_valued_keyword_cards')
        fits.conf.reset('extension_name_case_sensitive')
        fits.conf.reset('strip_header_whitespace')
        fits.conf.reset('use_memmap')

    def copy_file(self, filename):
        """Copies a backup of a test data file to the temp dir and sets its
        mode to writeable.
        """

        shutil.copy(self.data(filename), self.temp(filename))
        os.chmod(self.temp(filename), stat.S_IREAD | stat.S_IWRITE)

    def data(self, filename):
        """Returns the path to a test data file."""

        return os.path.join(self.data_dir, filename)

    def temp(self, filename):
        """ Returns the full path to a file in the test temp dir."""

        return os.path.join(self.temp_dir, filename)
