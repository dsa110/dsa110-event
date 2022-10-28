import pytest
from os import path
from event import event
from astropy import time

_install_dir = path.abspath(path.dirname(event.__file__))

def test_create():
    print("testing t2trigger.json")
    dd = event.create_event(f"{_install_dir}/data/t2trigger.json")
    assert isinstance(dd, event.DSAEvent)

    print("testing t2trigger0.json")
    dd = event.create_event(f"{_install_dir}/data/t2trigger0.json")
    assert isinstance(dd, event.DSAEvent)

def test_tojson():
    dd = event.create_event(f"{_install_dir}/data/t2trigger.json")
    jj = dd.tojson()
    assert isinstance(jj, str)
    assert '{' in jj and '}' in jj

def test_write():
    dd = event.create_event(f"{_install_dir}/data/t2trigger.json")
    dd.dm = 0.
    dd.writejson(outpath=".")

# requires client to use dask lock?
#def test_writelock():
#    dd = event.create_event("data/t2trigger.json")
#    dd.writejson(outpath="./testout.json", lock=LOCK)
