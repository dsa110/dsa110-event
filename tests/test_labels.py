import pytest
from event import labels

_install_dir = path.abspath(path.dirname(event.__file__))


def test_read():
    dd = labels.readfile(filename=f"{_install_dir}/data/t2trigger.json")
    assert len(dd)


def test_prob():
    labels.set_probability(0.0, candname=None, filename=f"{_install_dir}/data/t2trigger.json")


def test_label():
    labels.set_label('save', candname=None, filename=f"{_install_dir}/data/t2trigger.json")
