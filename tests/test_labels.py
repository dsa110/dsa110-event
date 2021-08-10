import pytest
from event import labels


def test_list():
    labels.list_cands_labels('data/t2trigger.json')


def test_read():
    dd = labels.readfile('data/t2trigger.json')
    assert len(dd)
