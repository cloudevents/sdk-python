from cloudevents.generic import CloudEvent
import pytest


def test_del_is_abstract():
    """
    exists mainly for coverage reasons
    """
    with pytest.raises(TypeError):
        del CloudEvent()["a"]


def test_set_is_abstract():
    """
    exists mainly for coverage reasons
    """
    with pytest.raises(TypeError):
        CloudEvent()["a"] = 2


def test_create_is_abstract():
    """
    exists mainly for coverage reasons
    """
    assert CloudEvent.create({}, None) is None


def test_data_read_is_abstract():
    """
    exists mainly for coverage reasons
    """
    with pytest.raises(TypeError):
        CloudEvent()._data_read_model


def test_attributes_read_model_is_abstract():
    """
    exists mainly for coverage reasons
    """
    with pytest.raises(TypeError):
        CloudEvent()._attributes_read_model
