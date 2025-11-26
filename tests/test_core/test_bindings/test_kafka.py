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

from datetime import datetime, timezone
from typing import Any

import pytest

from cloudevents.core.base import BaseCloudEvent
from cloudevents.core.bindings.kafka import (
    KafkaMessage,
    from_binary,
    from_kafka,
    from_structured,
    to_binary,
    to_structured,
)
from cloudevents.core.formats.json import JSONFormat
from cloudevents.core.v1.event import CloudEvent


@pytest.fixture
def minimal_attributes() -> dict[str, str]:
    """Minimal valid CloudEvent attributes"""
    return {
        "type": "com.example.test",
        "source": "/test",
        "id": "test-id-123",
        "specversion": "1.0",
    }


def create_event(
    extra_attrs: dict[str, Any] | None = None,
    data: dict[str, Any] | str | bytes | None = None,
) -> CloudEvent:
    """Helper to create CloudEvent with valid required attributes"""
    attrs: dict[str, Any] = {
        "type": "com.example.test",
        "source": "/test",
        "id": "test-id-123",
        "specversion": "1.0",
    }
    if extra_attrs:
        attrs.update(extra_attrs)
    return CloudEvent(attributes=attrs, data=data)


def test_kafka_message_creation() -> None:
    """Test basic KafkaMessage creation"""
    message = KafkaMessage(
        headers={"content-type": b"application/json"},
        key=b"test-key",
        value=b"test",
    )
    assert message.headers == {"content-type": b"application/json"}
    assert message.key == b"test-key"
    assert message.value == b"test"


def test_kafka_message_immutable() -> None:
    """Test that KafkaMessage is immutable (frozen dataclass)"""
    message = KafkaMessage(headers={"test": b"value"}, key=None, value=b"data")

    with pytest.raises(Exception):  # FrozenInstanceError
        message.headers = {b"new": b"dict"}

    with pytest.raises(Exception):  # FrozenInstanceError
        message.value = b"new data"


def test_to_binary_required_attributes() -> None:
    """Test to_binary with only required attributes"""
    event = create_event()
    message = to_binary(event, JSONFormat())

    assert "ce_type" in message.headers
    assert message.headers["ce_type"] == b"com.example.test"
    assert "ce_source" in message.headers
    assert (
        message.headers["ce_source"] == b"%2Ftest"
    )  # Forward slash is percent-encoded
    assert "ce_id" in message.headers
    assert message.headers["ce_id"] == b"test-id-123"
    assert "ce_specversion" in message.headers
    assert message.headers["ce_specversion"] == b"1.0"


def test_to_binary_with_optional_attributes() -> None:
    """Test to_binary with optional attributes"""
    event = create_event(
        {"subject": "test-subject", "dataschema": "https://example.com/schema"},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    assert message.headers["ce_subject"] == b"test-subject"
    # All special characters including : and / are percent-encoded
    assert message.headers["ce_dataschema"] == b"https%3A%2F%2Fexample.com%2Fschema"


def test_to_binary_with_extensions() -> None:
    """Test to_binary with extension attributes"""
    event = create_event(
        {"customext": "custom-value", "anotherext": "another-value"},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    assert message.headers["ce_customext"] == b"custom-value"
    assert message.headers["ce_anotherext"] == b"another-value"


def test_to_binary_with_json_data() -> None:
    """Test to_binary with dict (JSON) data and datacontenttype"""
    event = create_event(
        {"datacontenttype": "application/json"}, data={"message": "Hello", "count": 42}
    )
    message = to_binary(event, JSONFormat())

    # With application/json datacontenttype, data should be serialized as JSON
    assert b'"message"' in message.value
    assert b'"Hello"' in message.value
    assert message.value != b""


def test_to_binary_with_string_data() -> None:
    """Test to_binary with string data"""
    event = create_event(data="Hello World")
    message = to_binary(event, JSONFormat())

    assert message.value == b"Hello World"


def test_to_binary_with_bytes_data() -> None:
    """Test to_binary with bytes data"""
    event = create_event(data=b"\x00\x01\x02\x03")
    message = to_binary(event, JSONFormat())

    assert message.value == b"\x00\x01\x02\x03"


def test_to_binary_with_none_data() -> None:
    """Test to_binary with None data"""
    event = create_event(data=None)
    message = to_binary(event, JSONFormat())

    assert message.value == b""


def test_to_binary_datetime_encoding() -> None:
    """Test to_binary with datetime attribute"""
    test_time = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
    event = create_event({"time": test_time})
    message = to_binary(event, JSONFormat())

    assert "ce_time" in message.headers
    # Should be ISO 8601 with Z suffix, percent-encoded
    assert b"2023-01-15T10%3A30%3A45Z" in message.headers["ce_time"]


def test_to_binary_special_characters() -> None:
    """Test to_binary with special characters in attributes"""
    event = create_event({"subject": 'Hello World! "quotes" & special'})
    message = to_binary(event, JSONFormat())

    assert "ce_subject" in message.headers
    assert b"%" in message.headers["ce_subject"]  # Percent encoding present


def test_to_binary_datacontenttype_mapping() -> None:
    """Test that datacontenttype maps to content-type header"""
    event = create_event({"datacontenttype": "application/json"}, data={"test": "data"})
    message = to_binary(event, JSONFormat())

    assert "content-type" in message.headers
    assert message.headers["content-type"] == b"application/json"
    assert "ce_datacontenttype" not in message.headers


def test_to_binary_partitionkey_in_key() -> None:
    """Test that partitionkey extension attribute becomes message key"""
    event = create_event({"partitionkey": "user-123"})
    message = to_binary(event, JSONFormat())

    assert message.key == "user-123"
    assert "ce_partitionkey" not in message.headers


def test_to_binary_custom_key_mapper() -> None:
    """Test to_binary with custom key mapper"""

    def custom_mapper(event: BaseCloudEvent) -> str:
        return f"custom-{event.get_type()}"

    event = create_event()
    message = to_binary(event, JSONFormat(), key_mapper=custom_mapper)

    assert message.key == "custom-com.example.test"


def test_to_binary_no_partitionkey() -> None:
    """Test to_binary without partitionkey returns None key"""
    event = create_event()
    message = to_binary(event, JSONFormat())

    assert message.key is None


def test_from_binary_required_attributes() -> None:
    """Test from_binary extracts required attributes"""
    message = KafkaMessage(
        headers={
            "ce_type": b"com.example.test",
            "ce_source": b"%2Ftest",
            "ce_id": b"test-123",
            "ce_specversion": b"1.0",
        },
        key=None,
        value=b"",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"  # Percent-decoded
    assert event.get_id() == "test-123"
    assert event.get_specversion() == "1.0"


def test_from_binary_with_optional_attributes() -> None:
    """Test from_binary with optional attributes"""
    message = KafkaMessage(
        headers={
            "ce_type": b"com.example.test",
            "ce_source": b"/test",
            "ce_id": b"123",
            "ce_specversion": b"1.0",
            "ce_subject": b"test-subject",
            "ce_dataschema": b"https%3A%2F%2Fexample.com%2Fschema",
        },
        key=None,
        value=b"",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_subject() == "test-subject"
    assert event.get_dataschema() == "https://example.com/schema"  # Percent-decoded


def test_from_binary_with_extensions() -> None:
    """Test from_binary with extension attributes"""
    message = KafkaMessage(
        headers={
            "ce_type": b"com.example.test",
            "ce_source": b"/test",
            "ce_id": b"123",
            "ce_specversion": b"1.0",
            "ce_customext": b"custom-value",
        },
        key=None,
        value=b"",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_extension("customext") == "custom-value"


def test_from_binary_with_json_data() -> None:
    """Test from_binary with JSON data"""
    message = KafkaMessage(
        headers={
            "ce_type": b"com.example.test",
            "ce_source": b"/test",
            "ce_id": b"123",
            "ce_specversion": b"1.0",
            "content-type": b"application/json",
        },
        key=None,
        value=b'{"message": "Hello", "count": 42}',
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    data = event.get_data()
    assert isinstance(data, dict)
    assert data["message"] == "Hello"
    assert data["count"] == 42


def test_from_binary_datetime_parsing() -> None:
    """Test from_binary parses datetime correctly"""
    message = KafkaMessage(
        headers={
            "ce_type": b"com.example.test",
            "ce_source": b"/test",
            "ce_id": b"123",
            "ce_specversion": b"1.0",
            "ce_time": b"2023-01-15T10%3A30%3A45Z",
        },
        key=None,
        value=b"",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    time = event.get_time()
    assert isinstance(time, datetime)
    assert time.year == 2023
    assert time.month == 1
    assert time.day == 15


def test_from_binary_case_insensitive_headers() -> None:
    """Test from_binary handles case-insensitive headers"""
    message = KafkaMessage(
        headers={
            "CE_TYPE": b"com.example.test",
            "CE_SOURCE": b"/test",
            "ce_id": b"123",
            "Ce_Specversion": b"1.0",
        },
        key=None,
        value=b"",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"


def test_from_binary_content_type_as_datacontenttype() -> None:
    """Test that content-type header becomes datacontenttype attribute"""
    message = KafkaMessage(
        headers={
            "ce_type": b"com.example.test",
            "ce_source": b"/test",
            "ce_id": b"123",
            "ce_specversion": b"1.0",
            "content-type": b"application/json",
        },
        key=None,
        value=b'{"test": "data"}',
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_datacontenttype() == "application/json"


def test_from_binary_key_to_partitionkey() -> None:
    """Test that message key becomes partitionkey extension attribute"""
    message = KafkaMessage(
        headers={
            "ce_type": b"com.example.test",
            "ce_source": b"/test",
            "ce_id": b"123",
            "ce_specversion": b"1.0",
        },
        key=b"user-123",
        value=b"",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_extension("partitionkey") == "user-123"


def test_from_binary_round_trip() -> None:
    """Test round-trip conversion preserves all data"""
    original = create_event(
        {
            "time": datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc),
            "subject": "test-subject",
            "partitionkey": "user-456",
        },
        data={"message": "Hello", "count": 42},
    )

    message = to_binary(original, JSONFormat())
    recovered = from_binary(message, JSONFormat(), CloudEvent)

    assert recovered.get_type() == original.get_type()
    assert recovered.get_source() == original.get_source()
    assert recovered.get_id() == original.get_id()
    assert recovered.get_subject() == original.get_subject()
    assert recovered.get_extension("partitionkey") == "user-456"


def test_to_structured_basic_event() -> None:
    """Test to_structured with basic event"""
    event = create_event(data={"message": "Hello"})
    message = to_structured(event, JSONFormat())

    assert "content-type" in message.headers
    assert message.headers["content-type"] == b"application/cloudevents+json"
    assert b"type" in message.value
    assert b"source" in message.value


def test_to_structured_with_all_attributes() -> None:
    """Test to_structured with all optional attributes"""
    event = create_event(
        {
            "time": datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc),
            "subject": "test-subject",
            "datacontenttype": "application/json",
            "dataschema": "https://example.com/schema",
        },
        data={"message": "Hello"},
    )
    message = to_structured(event, JSONFormat())

    assert b"time" in message.value
    assert b"subject" in message.value
    assert b"datacontenttype" in message.value


def test_to_structured_partitionkey_in_key() -> None:
    """Test that partitionkey becomes message key in structured mode"""
    event = create_event({"partitionkey": "user-789"})
    message = to_structured(event, JSONFormat())

    assert message.key == "user-789"


def test_to_structured_custom_key_mapper() -> None:
    """Test to_structured with custom key mapper"""

    def custom_mapper(event: BaseCloudEvent) -> str:
        return f"type-{event.get_type().split('.')[-1]}"

    event = create_event()
    message = to_structured(event, JSONFormat(), key_mapper=custom_mapper)

    assert message.key == "type-test"


def test_to_structured_with_binary_data() -> None:
    """Test to_structured with binary data (should be base64 encoded)"""
    event = create_event(data=b"\x00\x01\x02\x03")
    message = to_structured(event, JSONFormat())

    # Binary data should be base64 encoded in structured mode
    assert b"data_base64" in message.value


def test_from_structured_basic_event() -> None:
    """Test from_structured with basic event"""
    message = KafkaMessage(
        headers={"content-type": b"application/cloudevents+json"},
        key=None,
        value=b'{"type":"com.example.test","source":"/test","id":"123","specversion":"1.0","data":{"message":"Hello"}}',
    )
    event = from_structured(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_data() == {"message": "Hello"}


def test_from_structured_key_to_partitionkey() -> None:
    """Test that message key becomes partitionkey in structured mode"""
    message = KafkaMessage(
        headers={"content-type": b"application/cloudevents+json"},
        key=b"user-999",
        value=b'{"type":"com.example.test","source":"/test","id":"123","specversion":"1.0"}',
    )
    event = from_structured(message, JSONFormat(), CloudEvent)

    assert event.get_extension("partitionkey") == "user-999"


def test_from_structured_round_trip() -> None:
    """Test structured mode round-trip"""
    original = create_event(
        {
            "time": datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc),
            "subject": "test-subject",
            "partitionkey": "key-123",
        },
        data={"message": "Hello", "count": 42},
    )

    message = to_structured(original, JSONFormat())
    recovered = from_structured(message, JSONFormat(), CloudEvent)

    assert recovered.get_type() == original.get_type()
    assert recovered.get_source() == original.get_source()
    assert recovered.get_extension("partitionkey") == "key-123"


def test_from_kafka_detects_binary_mode() -> None:
    """Test from_kafka detects binary mode (ce_ headers present)"""
    message = KafkaMessage(
        headers={
            "ce_type": b"com.example.test",
            "ce_source": b"/test",
            "ce_id": b"123",
            "ce_specversion": b"1.0",
        },
        key=None,
        value=b'{"message": "Hello"}',
    )
    event = from_kafka(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"


def test_from_kafka_detects_structured_mode() -> None:
    """Test from_kafka detects structured mode (no ce_ headers)"""
    message = KafkaMessage(
        headers={"content-type": b"application/cloudevents+json"},
        key=None,
        value=b'{"type":"com.example.test","source":"/test","id":"123","specversion":"1.0"}',
    )
    event = from_kafka(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"


def test_from_kafka_case_insensitive_detection() -> None:
    """Test from_kafka detection is case-insensitive"""
    message = KafkaMessage(
        headers={
            "CE_TYPE": b"com.example.test",
            "CE_SOURCE": b"/test",
            "ce_id": b"123",
            "ce_specversion": b"1.0",
        },
        key=None,
        value=b"",
    )
    event = from_kafka(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"


def test_from_kafka_binary_with_partitionkey() -> None:
    """Test from_kafka binary mode with partition key"""
    message = KafkaMessage(
        headers={
            "ce_type": b"com.example.test",
            "ce_source": b"/test",
            "ce_id": b"123",
            "ce_specversion": b"1.0",
        },
        key=b"user-555",
        value=b"",
    )
    event = from_kafka(message, JSONFormat(), CloudEvent)

    assert event.get_extension("partitionkey") == "user-555"


def test_from_kafka_structured_with_partitionkey() -> None:
    """Test from_kafka structured mode with partition key"""
    message = KafkaMessage(
        headers={"content-type": b"application/cloudevents+json"},
        key=b"user-666",
        value=b'{"type":"com.example.test","source":"/test","id":"123","specversion":"1.0"}',
    )
    event = from_kafka(message, JSONFormat(), CloudEvent)

    assert event.get_extension("partitionkey") == "user-666"


def test_empty_headers() -> None:
    """Test handling of empty headers in structured mode"""
    message = KafkaMessage(
        headers={},
        key=None,
        value=b'{"type":"com.example.test","source":"/test","id":"123","specversion":"1.0"}',
    )
    # Should default to structured mode
    event = from_kafka(message, JSONFormat(), CloudEvent)
    assert event.get_type() == "com.example.test"


def test_unicode_in_attributes() -> None:
    """Test handling of unicode characters in attributes"""
    event = create_event({"subject": "Hello 世界 🌍"})
    message = to_binary(event, JSONFormat())
    recovered = from_binary(message, JSONFormat(), CloudEvent)

    assert recovered.get_subject() == "Hello 世界 🌍"


def test_unicode_in_data() -> None:
    """Test handling of unicode characters in data"""
    event = create_event(
        {"datacontenttype": "application/json"}, data={"message": "Hello 世界 🌍"}
    )
    message = to_binary(event, JSONFormat())
    recovered = from_binary(message, JSONFormat(), CloudEvent)

    assert isinstance(recovered.get_data(), dict)
    assert recovered.get_data()["message"] == "Hello 世界 🌍"


def test_string_key_vs_bytes_key() -> None:
    """Test that both string and bytes keys work"""
    # String key
    event1 = create_event({"partitionkey": "string-key"})
    msg1 = to_binary(event1, JSONFormat())
    assert msg1.key == "string-key"

    # Bytes key through custom mapper
    def bytes_mapper(event: BaseCloudEvent) -> bytes:
        return b"bytes-key"

    event2 = create_event()
    msg2 = to_binary(event2, JSONFormat(), key_mapper=bytes_mapper)
    assert msg2.key == b"bytes-key"
