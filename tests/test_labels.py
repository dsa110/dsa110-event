import pytest
from event import labels


def test_read():
    dd = labels.readfile(filename='data/t2trigger.json')
    assert len(dd)


def test_prob():
    labels.set_probability(0.0, candname=None, filename='data/t2trigger.json')


def test_label():
    labels.set_label('save', candname=None, filename='data/t2trigger.json')
