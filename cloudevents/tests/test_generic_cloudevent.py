from cloudevents.generic import CloudEvent
import pytest


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


def test_data_read_is_abstract():
    """
    exists mainly for coverage reasons
    """
    with pytest.raises(NotImplementedError):
        CloudEvent()._data_read_model


def test_attributes_read_model_is_abstract():
    """
    exists mainly for coverage reasons
    """
    with pytest.raises(NotImplementedError):
        CloudEvent()._attributes_read_model
