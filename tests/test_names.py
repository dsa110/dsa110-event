import pytest
import os.path
from event import names
from astropy import time


def test_lastname():
    name = names.get_lastname()
    assert name is None  # only works if nothing set in etcd


def test_newnamet():
    mjd = time.Time.now().mjd
    name = names.increment_name(mjd)

    assert name is not None

def test_increment():
    mjd = time.Time.now().mjd
    name = names.increment_name(mjd)
    name2 = names.increment_name(mjd, lastname=name)

    assert name != name2
