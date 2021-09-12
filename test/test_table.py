import pytest
from qzemoji import query


def test_hit():
    assert '🐷' == query('400343.gif')
    assert '[/困]' == query(125)


def test_miss():
    assert query('0.png') is None
    assert query(1) is None


def test_exc():
    assert query('125') is not None
    assert query('125.tar.gz') is not None
    pytest.raises(ValueError, query, 'qvq.png')
