# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-

import pytest

asdf = pytest.importorskip('asdf')

import astropy.units as u

from asdf.tests.helpers import assert_roundtrip_tree

from astropy.coordinates import Longitude, Latitude, Angle

from ....extension import AstropyExtension


def test_angle(tmpdir):
    tree = {'angle': Angle(100, u.deg)}
    assert_roundtrip_tree(tree, tmpdir)


def test_latitude(tmpdir):
    tree = {'angle': Latitude(10, u.deg)}
    assert_roundtrip_tree(tree, tmpdir)


def test_longitude(tmpdir):
    tree = {'angle': Longitude(-100, u.deg, wrap_angle=180*u.deg)}
    assert_roundtrip_tree(tree, tmpdir)

def test_ndarray_latitude(tmpdir):
    tmpfile = str(tmpdir.join('lat.asdf'))

    tree = {'lat': Latitude([1, 1.1, 1.5], u.rad)}
    with asdf.AsdfFile(tree) as af:
        af.write_to(tmpfile)

    with asdf.open(tmpfile) as ff:
        assert all(ff.tree['lat'] == tree['lat'])

def test_ndarray_longitude(tmpdir):
    tmpfile = str(tmpdir.join('long.asdf'))

    tree = {'long': Longitude([1, 1.1, 1.5], u.rad)}
    with asdf.AsdfFile(tree) as af:
        af.write_to(tmpfile)

    with asdf.open(tmpfile) as ff:
        assert all(ff.tree['long'] == tree['long'])
