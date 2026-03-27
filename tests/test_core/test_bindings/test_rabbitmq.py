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

from cloudevents.core.bindings.rabbitmq import (
    RabbitMQMessage,
    from_binary,
    from_rabbitmq,
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


def test_rabbitmq_message_creation() -> None:
    """Test basic RabbitMQMessage creation"""
    message = RabbitMQMessage(
        headers={"ce-type": "test"},
        content_type="application/json",
        body=b"test",
    )
    assert message.headers == {"ce-type": "test"}
    assert message.content_type == "application/json"
    assert message.body == b"test"


def test_rabbitmq_message_immutable() -> None:
    """Test that RabbitMQMessage is immutable (frozen dataclass)"""
    message = RabbitMQMessage(
        headers={"test": "value"},
        content_type="application/json",
        body=b"data",
    )

    with pytest.raises(Exception):  # FrozenInstanceError
        message.headers = {"new": "dict"}

    with pytest.raises(Exception):  # FrozenInstanceError
        message.content_type = "text/plain"

    with pytest.raises(Exception):  # FrozenInstanceError
        message.body = b"new data"


def test_rabbitmq_message_with_empty_headers() -> None:
    """Test RabbitMQMessage with empty headers"""
    message = RabbitMQMessage(headers={}, content_type=None, body=b"test")
    assert message.headers == {}
    assert message.content_type is None
    assert message.body == b"test"


def test_rabbitmq_message_with_empty_body() -> None:
    """Test RabbitMQMessage with empty body"""
    message = RabbitMQMessage(headers={"test": "value"}, content_type=None, body=b"")
    assert message.headers == {"test": "value"}
    assert message.body == b""


def test_rabbitmq_message_with_none_content_type() -> None:
    """Test RabbitMQMessage with None content_type"""
    message = RabbitMQMessage(headers={}, content_type=None, body=b"test")
    assert message.content_type is None


def test_to_binary_required_attributes() -> None:
    """Test to_binary with only required attributes"""
    event = create_event()
    message = to_binary(event, JSONFormat())

    assert "ce-type" in message.headers
    assert message.headers["ce-type"] == "com.example.test"
    assert message.headers["ce-source"] == "/test"
    assert message.headers["ce-id"] == "test-id-123"
    assert message.headers["ce-specversion"] == "1.0"


def test_to_binary_with_optional_attributes() -> None:
    """Test to_binary with optional attributes"""
    event = create_event(
        extra_attrs={
            "subject": "test-subject",
            "dataschema": "https://example.com/schema",
        }
    )
    message = to_binary(event, JSONFormat())

    assert message.headers["ce-subject"] == "test-subject"
    assert message.headers["ce-dataschema"] == "https://example.com/schema"


def test_to_binary_with_extensions() -> None:
    """Test to_binary with custom extension attributes"""
    event = create_event(extra_attrs={"customext": "custom-value"})
    message = to_binary(event, JSONFormat())

    assert message.headers["ce-customext"] == "custom-value"


def test_to_binary_datetime_as_iso8601() -> None:
    """Test to_binary converts datetime to ISO 8601 string"""
    dt = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
    event = create_event(extra_attrs={"time": dt})
    message = to_binary(event, JSONFormat())

    assert message.headers["ce-time"] == "2023-01-15T10:30:45Z"
    assert isinstance(message.headers["ce-time"], str)


def test_to_binary_datetime_utc_z_suffix() -> None:
    """Test to_binary uses Z suffix for UTC datetimes, not +00:00"""
    dt = datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    event = create_event(extra_attrs={"time": dt})
    message = to_binary(event, JSONFormat())

    assert message.headers["ce-time"].endswith("Z")
    assert "+00:00" not in message.headers["ce-time"]


def test_to_binary_datetime_non_utc() -> None:
    """Test to_binary preserves non-UTC timezone offset"""
    from datetime import timedelta

    custom_tz = timezone(timedelta(hours=5))
    dt = datetime(2023, 1, 15, 10, 30, 45, tzinfo=custom_tz)
    event = create_event(extra_attrs={"time": dt})
    message = to_binary(event, JSONFormat())

    assert "+05:00" in message.headers["ce-time"]


def test_to_binary_datacontenttype_mapping() -> None:
    """Test datacontenttype maps to content_type field, not a header"""
    event = create_event(
        extra_attrs={"datacontenttype": "application/json"}, data={"key": "value"}
    )
    message = to_binary(event, JSONFormat())

    assert message.content_type == "application/json"
    assert "ce-datacontenttype" not in message.headers


def test_to_binary_with_json_data() -> None:
    """Test to_binary with JSON dict data"""
    event = create_event(
        extra_attrs={"datacontenttype": "application/json"},
        data={"message": "Hello", "count": 42},
    )
    message = to_binary(event, JSONFormat())

    import json

    parsed = json.loads(message.body)
    assert parsed == {"message": "Hello", "count": 42}


def test_to_binary_with_string_data() -> None:
    """Test to_binary with string data"""
    event = create_event(data="Hello World")
    message = to_binary(event, JSONFormat())

    assert b"Hello World" in message.body


def test_to_binary_with_bytes_data() -> None:
    """Test to_binary with bytes data"""
    binary_data = b"\x00\x01\x02\x03"
    event = create_event(data=binary_data)
    message = to_binary(event, JSONFormat())

    assert len(message.body) > 0


def test_to_binary_with_none_data() -> None:
    """Test to_binary with None data"""
    event = create_event(data=None)
    message = to_binary(event, JSONFormat())

    assert message.body is not None


def test_to_binary_header_values_are_strings() -> None:
    """Test that all header values are strings, not bytes"""
    event = create_event(extra_attrs={"customext": "value"})
    message = to_binary(event, JSONFormat())

    for value in message.headers.values():
        assert isinstance(value, str)


def test_to_binary_integer_extension_converted_to_string() -> None:
    """Test to_binary converts integer extension to string"""
    event = create_event(extra_attrs={"intext": 42})
    message = to_binary(event, JSONFormat())

    assert message.headers["ce-intext"] == "42"
    assert isinstance(message.headers["ce-intext"], str)


def test_to_binary_boolean_extension_converted_to_string() -> None:
    """Test to_binary converts boolean extension to string"""
    event = create_event(extra_attrs={"boolext": True})
    message = to_binary(event, JSONFormat())

    assert message.headers["ce-boolext"] == "True"
    assert isinstance(message.headers["ce-boolext"], str)


def test_to_binary_no_content_type_when_no_datacontenttype() -> None:
    """Test to_binary sets content_type to None when datacontenttype is absent"""
    event = create_event(data=None)
    message = to_binary(event, JSONFormat())

    assert message.content_type is None


def test_from_binary_required_attributes() -> None:
    """Test from_binary extracts required attributes"""
    message = RabbitMQMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        content_type=None,
        body=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "123"
    assert event.get_specversion() == "1.0"


def test_from_binary_with_content_type() -> None:
    """Test from_binary maps content_type to datacontenttype"""
    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        content_type="application/json",
        body=b'{"message": "Hello"}',
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_datacontenttype() == "application/json"
    assert event.get_data() == {"message": "Hello"}


def test_from_binary_with_extensions() -> None:
    """Test from_binary extracts custom extension attributes"""
    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
            "ce-customext": "custom-value",
        },
        content_type=None,
        body=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_extension("customext") == "custom-value"


def test_from_binary_time_parsing() -> None:
    """Test from_binary parses ISO 8601 time string to datetime"""
    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
            "ce-time": "2023-01-15T10:30:45Z",
        },
        content_type=None,
        body=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    expected = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
    assert event.get_time() == expected
    assert isinstance(event.get_time(), datetime)


def test_from_binary_time_with_offset() -> None:
    """Test from_binary parses time with timezone offset"""
    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
            "ce-time": "2023-01-15T10:30:45+05:00",
        },
        content_type=None,
        body=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    from datetime import timedelta

    expected = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone(timedelta(hours=5)))
    assert event.get_time() == expected


def test_from_binary_ignores_non_ce_headers() -> None:
    """Test from_binary only extracts ce- prefixed headers"""
    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
            "custom-header": "should-be-ignored",
            "x-another": "also-ignored",
        },
        content_type=None,
        body=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "test"
    assert event.get_extension("custom-header") is None
    assert event.get_extension("x-another") is None


def test_from_binary_case_insensitive_prefix() -> None:
    """Test from_binary handles case-insensitive ce- prefix"""
    message = RabbitMQMessage(
        headers={
            "Ce-type": "com.example.test",
            "CE-source": "/test",
            "ce-id": "123",
            "CE-SPECVERSION": "1.0",
        },
        content_type=None,
        body=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "123"
    assert event.get_specversion() == "1.0"


def test_from_binary_with_text_data() -> None:
    """Test from_binary with text data"""
    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        content_type="text/plain",
        body=b"Hello World",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_data() == "Hello World"


def test_from_binary_with_bytes_data() -> None:
    """Test from_binary with binary data"""
    binary_data = b"\x00\x01\x02\x03"
    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        content_type="application/octet-stream",
        body=binary_data,
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert isinstance(event.get_data(), (bytes, str))


def test_from_binary_auto_detect_version() -> None:
    """Test from_binary auto-detects CloudEvents version when factory is None"""
    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        content_type=None,
        body=b"{}",
    )
    event = from_binary(message, JSONFormat())

    assert event.get_type() == "test"
    assert event.get_specversion() == "1.0"


def test_binary_round_trip() -> None:
    """Test binary mode round-trip preserves event data"""
    original = create_event(
        extra_attrs={"subject": "test-subject", "datacontenttype": "application/json"},
        data={"message": "Hello", "count": 42},
    )

    message = to_binary(original, JSONFormat())
    recovered = from_binary(message, JSONFormat(), CloudEvent)

    assert recovered.get_type() == original.get_type()
    assert recovered.get_source() == original.get_source()
    assert recovered.get_id() == original.get_id()
    assert recovered.get_specversion() == original.get_specversion()
    assert recovered.get_subject() == original.get_subject()
    assert recovered.get_data() == original.get_data()


def test_binary_round_trip_with_datetime() -> None:
    """Test binary mode round-trip preserves datetime"""
    dt = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
    original = create_event(extra_attrs={"time": dt})

    message = to_binary(original, JSONFormat())
    recovered = from_binary(message, JSONFormat(), CloudEvent)

    assert recovered.get_time() == dt
    assert isinstance(recovered.get_time(), datetime)


def test_binary_round_trip_with_extensions() -> None:
    """Test binary mode round-trip preserves extensions as strings"""
    original = create_event(extra_attrs={"ext1": "value1", "ext2": "value2"})

    message = to_binary(original, JSONFormat())
    recovered = from_binary(message, JSONFormat(), CloudEvent)

    assert recovered.get_extension("ext1") == "value1"
    assert recovered.get_extension("ext2") == "value2"


def test_to_structured_basic_event() -> None:
    """Test to_structured with basic event"""
    event = create_event(data={"message": "Hello"})
    message = to_structured(event, JSONFormat())

    assert message.content_type == "application/cloudevents+json"
    assert b"com.example.test" in message.body
    assert b"message" in message.body


def test_to_structured_content_type() -> None:
    """Test to_structured sets correct content_type"""
    event = create_event()
    message = to_structured(event, JSONFormat())

    assert message.content_type == "application/cloudevents+json"


def test_to_structured_empty_headers() -> None:
    """Test to_structured produces empty headers"""
    event = create_event()
    message = to_structured(event, JSONFormat())

    assert message.headers == {}


def test_to_structured_with_all_attributes() -> None:
    """Test to_structured includes all attributes in serialized form"""
    dt = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
    event = create_event(
        extra_attrs={
            "time": dt,
            "subject": "test-subject",
            "dataschema": "https://example.com/schema",
            "customext": "custom-value",
        },
        data={"message": "Hello"},
    )
    message = to_structured(event, JSONFormat())

    assert b"test-subject" in message.body
    assert b"customext" in message.body


def test_from_structured_basic_event() -> None:
    """Test from_structured parses complete event"""
    message = RabbitMQMessage(
        headers={},
        content_type="application/cloudevents+json",
        body=b'{"type": "com.example.test", "source": "/test", '
        b'"id": "123", "specversion": "1.0", "data": {"message": "Hello"}}',
    )
    event = from_structured(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "123"
    assert event.get_data() == {"message": "Hello"}


def test_structured_round_trip() -> None:
    """Test structured mode round-trip preserves event data"""
    original = create_event(
        extra_attrs={"subject": "test-subject", "datacontenttype": "application/json"},
        data={"message": "Hello", "count": 42},
    )

    message = to_structured(original, JSONFormat())
    recovered = from_structured(message, JSONFormat(), CloudEvent)

    assert recovered.get_type() == original.get_type()
    assert recovered.get_source() == original.get_source()
    assert recovered.get_id() == original.get_id()
    assert recovered.get_specversion() == original.get_specversion()
    assert recovered.get_subject() == original.get_subject()
    assert recovered.get_data() == original.get_data()


def test_from_rabbitmq_detects_binary_mode() -> None:
    """Test from_rabbitmq detects binary mode"""
    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        content_type="application/json",
        body=b'{"message": "Hello"}',
    )
    event = from_rabbitmq(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "test"
    assert event.get_data() == {"message": "Hello"}


def test_from_rabbitmq_detects_structured_mode() -> None:
    """Test from_rabbitmq detects structured mode"""
    message = RabbitMQMessage(
        headers={},
        content_type="application/cloudevents+json",
        body=b'{"type": "com.example.test", "source": "/test", '
        b'"id": "123", "specversion": "1.0"}',
    )
    event = from_rabbitmq(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"


def test_from_rabbitmq_case_insensitive_detection() -> None:
    """Test from_rabbitmq detection is case-insensitive"""
    message = RabbitMQMessage(
        headers={},
        content_type="application/CLOUDEVENTS+json",
        body=b'{"type": "com.example.test", "source": "/test", '
        b'"id": "123", "specversion": "1.0"}',
    )
    event = from_rabbitmq(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"


def test_from_rabbitmq_defaults_to_binary_when_no_content_type() -> None:
    """Test from_rabbitmq defaults to binary mode when content_type is None"""
    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        content_type=None,
        body=b"{}",
    )
    event = from_rabbitmq(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "test"


def test_from_rabbitmq_non_cloudevents_content_type_is_binary() -> None:
    """Test from_rabbitmq uses binary mode for non-cloudevents content types"""
    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        content_type="text/plain",
        body=b"Hello",
    )
    event = from_rabbitmq(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "test"


def test_unicode_in_attributes() -> None:
    """Test handling of unicode characters in attributes"""
    event = create_event(extra_attrs={"subject": "测试-subject-🌍"})
    message = to_binary(event, JSONFormat())
    recovered = from_binary(message, JSONFormat(), CloudEvent)

    assert recovered.get_subject() == "测试-subject-🌍"


def test_unicode_in_data() -> None:
    """Test handling of unicode characters in data"""
    event = create_event(data={"message": "Hello 世界 🌍"})
    message = to_binary(event, JSONFormat())
    recovered = from_binary(message, JSONFormat(), CloudEvent)

    data = recovered.get_data()
    if isinstance(data, dict):
        assert data == {"message": "Hello 世界 🌍"}
    else:
        assert "Hello 世界 🌍" in str(data)


def test_to_binary_event_defaults_json_format() -> None:
    """Test to_binary_event uses JSONFormat by default"""
    from cloudevents.core.bindings.rabbitmq import to_binary_event

    event = create_event(data={"key": "value"})
    message = to_binary_event(event)

    assert isinstance(message, RabbitMQMessage)
    assert "ce-type" in message.headers


def test_from_binary_event_defaults_json_format() -> None:
    """Test from_binary_event uses JSONFormat and CloudEvent by default"""
    from cloudevents.core.bindings.rabbitmq import from_binary_event

    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        content_type=None,
        body=b"{}",
    )
    event = from_binary_event(message)

    assert isinstance(event, CloudEvent)
    assert event.get_type() == "test"


def test_to_structured_event_defaults_json_format() -> None:
    """Test to_structured_event uses JSONFormat by default"""
    from cloudevents.core.bindings.rabbitmq import to_structured_event

    event = create_event(data={"key": "value"})
    message = to_structured_event(event)

    assert isinstance(message, RabbitMQMessage)
    assert message.content_type == "application/cloudevents+json"


def test_from_structured_event_defaults_json_format() -> None:
    """Test from_structured_event uses JSONFormat and CloudEvent by default"""
    from cloudevents.core.bindings.rabbitmq import from_structured_event

    message = RabbitMQMessage(
        headers={},
        content_type="application/cloudevents+json",
        body=b'{"type": "test", "source": "/test", "id": "123", "specversion": "1.0"}',
    )
    event = from_structured_event(message)

    assert isinstance(event, CloudEvent)
    assert event.get_type() == "test"


def test_from_rabbitmq_event_defaults_json_format() -> None:
    """Test from_rabbitmq_event uses JSONFormat and CloudEvent by default"""
    from cloudevents.core.bindings.rabbitmq import from_rabbitmq_event

    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        content_type="application/json",
        body=b"{}",
    )
    event = from_rabbitmq_event(message)

    assert isinstance(event, CloudEvent)
    assert event.get_type() == "test"


def test_to_binary_with_multiple_extensions() -> None:
    """Test to_binary with multiple custom extensions"""
    event = create_event(
        extra_attrs={
            "ext1": "value1",
            "ext2": "value2",
            "ext3": "value3",
        }
    )
    message = to_binary(event, JSONFormat())

    assert message.headers["ce-ext1"] == "value1"
    assert message.headers["ce-ext2"] == "value2"
    assert message.headers["ce-ext3"] == "value3"


def test_from_binary_with_none_content_type() -> None:
    """Test from_binary when content_type is None"""
    message = RabbitMQMessage(
        headers={
            "ce-type": "test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        content_type=None,
        body=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_datacontenttype() is None


def test_empty_headers_structured_mode() -> None:
    """Test message with empty headers (structured mode)"""
    message = RabbitMQMessage(
        headers={},
        content_type="application/cloudevents+json",
        body=b'{"type": "test", "source": "/test", "id": "123", "specversion": "1.0"}',
    )
    event = from_structured(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "test"
