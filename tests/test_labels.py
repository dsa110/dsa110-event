import pytest
from event import labels


def test_list():
    labels.list_cands_labels(filename='data/t2trigger.json')


def test_read():
    dd = labels.readfile(filename='data/t2trigger.json')
    assert len(dd)
