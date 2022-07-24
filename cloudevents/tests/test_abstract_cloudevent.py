import pytest

from cloudevents.abstract import CloudEvent


def test_del_is_abstract():
    """
    exists mainly for coverage reasons
    """
    with pytest.raises(NotImplementedError):
        del CloudEvent()["a"]


def test_set_is_abstract():
    """
    exists mainly for coverage reasons
    """
    with pytest.raises(NotImplementedError):
        CloudEvent()["a"] = 2


def test_create_is_abstract():
    """
    exists mainly for coverage reasons
    """
    with pytest.raises(NotImplementedError):
        assert CloudEvent.create({}, None) is None


def test_data_is_abstract():
    """
    exists mainly for coverage reasons
    """
    with pytest.raises(NotImplementedError):
        CloudEvent().data


def test_attributes_is_abstract():
    """
    exists mainly for coverage reasons
    """
    with pytest.raises(NotImplementedError):
        CloudEvent().attributes
