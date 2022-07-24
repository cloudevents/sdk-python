import pytest

from cloudevents.abstract import CloudEvent


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
        CloudEvent.get_data(CloudEvent())


def test_attributes_is_abstract():
    """
    exists mainly for coverage reasons
    """
    with pytest.raises(NotImplementedError):
        CloudEvent.get_attributes(CloudEvent())
