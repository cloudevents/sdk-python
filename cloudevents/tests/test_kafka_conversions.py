#  Copyright 2018-Present The CloudEvents Authors
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import base64
import datetime
import json

import pytest

from cloudevents.http import CloudEvent
from cloudevents.kafka.conversion import (
    ProtocolMessage,
    from_binary,
    from_structured,
    to_binary,
    to_structured,
)
from cloudevents.sdk.event.attribute import SpecVersion


@pytest.fixture
def source_event():
    return CloudEvent.create(
        attributes={
            "specversion": "1.0",
            "id": "1234-1234-1234",
            "source": "pytest",
            "type": "com.pytest.test",
            "time": datetime.datetime(2000, 1, 1, 6, 42, 33).isoformat(),
            "content-type": "foo",
            "key": "test_key_123",
        },
        data={"name": "test", "amount": 1},
    )


@pytest.fixture
def source_binary_json_message():
    return ProtocolMessage(
        headers={
            "ce_specversion": "1.0".encode("utf-8"),
            "ce_id": "1234-1234-1234".encode("utf-8"),
            "ce_source": "pytest".encode("utf-8"),
            "ce_type": "com.pytest.test".encode("utf-8"),
            "ce_time": datetime.datetime(2000, 1, 1, 6, 42, 33)
            .isoformat()
            .encode("utf-8"),
            "content-type": "foo".encode("utf-8"),
        },
        value=json.dumps({"name": "test", "amount": 1}).encode("utf-8"),
        key="test_key_123",
    )


@pytest.fixture
def source_binary_bytes_message():
    return ProtocolMessage(
        headers={
            "ce_specversion": "1.0".encode("utf-8"),
            "ce_id": "1234-1234-1234".encode("utf-8"),
            "ce_source": "pytest".encode("utf-8"),
            "ce_type": "com.pytest.test".encode("utf-8"),
            "ce_time": datetime.datetime(2000, 1, 1, 6, 42, 33)
            .isoformat()
            .encode("utf-8"),
            "content-type": "foo".encode("utf-8"),
        },
        value=bytes("hello".encode("utf-8")),
        key="test_key_123",
    )


def test_to_binary_set_value_default_marshaller(source_event):
    result = to_binary(source_event)
    assert result.value == json.dumps(source_event.data).encode("utf-8")


def test_to_binary_set_value_custom_marshaller(source_event):
    marshaller = lambda data: bytes(str(data).encode("utf-8"))
    result = to_binary(source_event, data_marshaller=marshaller)
    assert result.value == bytes(str(source_event.data).encode("utf-8"))


def test_to_binary_sets_key(source_event):
    result = to_binary(source_event)
    assert result.key == source_event["key"]


def test_to_binary_none_key(source_event):
    source_event["key"] = None
    result = to_binary(source_event)
    assert result.key == None


def test_to_binary_no_key(source_event):
    del source_event["key"]
    result = to_binary(source_event)
    assert result.key == None


def test_to_binary_sets_headers(source_event):
    result = to_binary(source_event)
    assert result.headers["ce_id"] == source_event["id"].encode("utf-8")
    assert result.headers["ce_specversion"] == source_event["specversion"].encode(
        "utf-8"
    )
    assert result.headers["ce_source"] == source_event["source"].encode("utf-8")
    assert result.headers["ce_type"] == source_event["type"].encode("utf-8")
    assert result.headers["ce_time"] == source_event["time"].encode("utf-8")
    assert result.headers["content-type"] == source_event["content-type"].encode(
        "utf-8"
    )
    assert "data" not in result.headers
    assert "key" not in result.headers


def test_from_binary_default_marshaller(source_binary_json_message):
    result = from_binary(source_binary_json_message)
    assert result.data == json.loads(source_binary_json_message.value.decode())


def test_from_binary_custom_marshaller(source_binary_bytes_message):
    unmarshaller = lambda data: data.decode()
    result = from_binary(
        source_binary_bytes_message, CloudEvent, data_unmarshaller=unmarshaller
    )
    assert result.data == source_binary_bytes_message.value.decode()


def test_from_binary_sets_key(source_binary_json_message):
    result = from_binary(source_binary_json_message)
    assert result["key"] == source_binary_json_message.key


def test_from_binary_no_key(source_binary_json_message):
    keyless_message = ProtocolMessage(
        headers=source_binary_json_message.headers,
        key=None,
        value=source_binary_json_message.value,
    )
    result = from_binary(keyless_message)
    assert "key" not in result.get_attributes()


def test_from_binary_sets_attrs_from_headers(source_binary_json_message):
    result = from_binary(source_binary_json_message)
    assert result["id"] == source_binary_json_message.headers["ce_id"].decode()
    assert (
        result["specversion"]
        == source_binary_json_message.headers["ce_specversion"].decode()
    )
    assert result["source"] == source_binary_json_message.headers["ce_source"].decode()
    assert result["type"] == source_binary_json_message.headers["ce_type"].decode()
    assert result["time"] == source_binary_json_message.headers["ce_time"].decode()
    assert (
        result["content-type"]
        == source_binary_json_message.headers["content-type"].decode()
    )
