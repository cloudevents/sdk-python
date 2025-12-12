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

from cloudevents.core.bindings.amqp import (
    AMQPMessage,
    from_amqp,
    from_binary,
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


def test_amqp_message_creation() -> None:
    """Test basic AMQPMessage creation"""
    message = AMQPMessage(
        properties={"content-type": "application/json"},
        application_properties={"cloudEvents_type": "test"},
        application_data=b"test",
    )
    assert message.properties == {"content-type": "application/json"}
    assert message.application_properties == {"cloudEvents_type": "test"}
    assert message.application_data == b"test"


def test_amqp_message_immutable() -> None:
    """Test that AMQPMessage is immutable (frozen dataclass)"""
    message = AMQPMessage(
        properties={"test": "value"},
        application_properties={},
        application_data=b"data",
    )

    with pytest.raises(Exception):  # FrozenInstanceError
        message.properties = {"new": "dict"}

    with pytest.raises(Exception):  # FrozenInstanceError
        message.application_properties = {"new": "dict"}

    with pytest.raises(Exception):  # FrozenInstanceError
        message.application_data = b"new data"


def test_amqp_message_with_empty_properties() -> None:
    """Test AMQPMessage with empty properties"""
    message = AMQPMessage(
        properties={}, application_properties={}, application_data=b"test"
    )
    assert message.properties == {}
    assert message.application_properties == {}
    assert message.application_data == b"test"


def test_amqp_message_with_empty_application_data() -> None:
    """Test AMQPMessage with empty application data"""
    message = AMQPMessage(
        properties={"test": "value"}, application_properties={}, application_data=b""
    )
    assert message.properties == {"test": "value"}
    assert message.application_data == b""


def test_to_binary_required_attributes() -> None:
    """Test to_binary with only required attributes"""
    event = create_event()
    message = to_binary(event, JSONFormat())

    assert "cloudEvents_type" in message.application_properties
    assert message.application_properties["cloudEvents_type"] == "com.example.test"
    assert message.application_properties["cloudEvents_source"] == "/test"
    assert message.application_properties["cloudEvents_id"] == "test-id-123"
    assert message.application_properties["cloudEvents_specversion"] == "1.0"


def test_to_binary_with_optional_attributes() -> None:
    """Test to_binary with optional attributes"""
    event = create_event(
        extra_attrs={
            "subject": "test-subject",
            "dataschema": "https://example.com/schema",
        }
    )
    message = to_binary(event, JSONFormat())

    assert message.application_properties["cloudEvents_subject"] == "test-subject"
    assert (
        message.application_properties["cloudEvents_dataschema"]
        == "https://example.com/schema"
    )


def test_to_binary_with_extensions() -> None:
    """Test to_binary with custom extension attributes"""
    event = create_event(extra_attrs={"customext": "custom-value"})
    message = to_binary(event, JSONFormat())

    assert message.application_properties["cloudEvents_customext"] == "custom-value"


def test_to_binary_datetime_as_timestamp() -> None:
    """Test to_binary converts datetime to AMQP timestamp (milliseconds since epoch)"""
    dt = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
    event = create_event(extra_attrs={"time": dt})
    message = to_binary(event, JSONFormat())

    # Should be serialized as AMQP timestamp (milliseconds since epoch)
    expected_timestamp = int(dt.timestamp() * 1000)  # 1673781045000
    assert message.application_properties["cloudEvents_time"] == expected_timestamp
    assert isinstance(message.application_properties["cloudEvents_time"], int)


def test_to_binary_boolean_as_boolean() -> None:
    """Test to_binary preserves boolean type (not converted to string)"""
    event = create_event(extra_attrs={"boolext": True})
    message = to_binary(event, JSONFormat())

    # Should be native boolean, not string "true" or "True"
    assert message.application_properties["cloudEvents_boolext"] is True
    assert isinstance(message.application_properties["cloudEvents_boolext"], bool)


def test_to_binary_integer_as_long() -> None:
    """Test to_binary preserves integer type (not converted to string)"""
    event = create_event(extra_attrs={"intext": 42})
    message = to_binary(event, JSONFormat())

    # Should be native int/long, not string "42"
    assert message.application_properties["cloudEvents_intext"] == 42
    assert isinstance(message.application_properties["cloudEvents_intext"], int)


def test_to_binary_datacontenttype_mapping() -> None:
    """Test datacontenttype maps to AMQP content-type property"""
    event = create_event(
        extra_attrs={"datacontenttype": "application/json"}, data={"key": "value"}
    )
    message = to_binary(event, JSONFormat())

    # datacontenttype should go to properties, not application_properties
    assert message.properties["content-type"] == "application/json"
    assert "cloudEvents_datacontenttype" not in message.application_properties


def test_to_binary_with_json_data() -> None:
    """Test to_binary with JSON dict data"""
    event = create_event(
        extra_attrs={"datacontenttype": "application/json"},
        data={"message": "Hello", "count": 42},
    )
    message = to_binary(event, JSONFormat())

    # JSON serialization may vary in formatting, so check it can be parsed back
    import json

    parsed = json.loads(message.application_data)
    assert parsed == {"message": "Hello", "count": 42}


def test_to_binary_with_string_data() -> None:
    """Test to_binary with string data"""
    event = create_event(data="Hello World")
    message = to_binary(event, JSONFormat())

    # String data should be serialized
    assert b"Hello World" in message.application_data


def test_to_binary_with_bytes_data() -> None:
    """Test to_binary with bytes data"""
    binary_data = b"\x00\x01\x02\x03"
    event = create_event(data=binary_data)
    message = to_binary(event, JSONFormat())

    # Bytes should be preserved in application_data
    assert len(message.application_data) > 0


def test_to_binary_with_none_data() -> None:
    """Test to_binary with None data"""
    event = create_event(data=None)
    message = to_binary(event, JSONFormat())

    # None data should result in empty or null serialization
    assert message.application_data is not None  # Should be bytes


def test_from_binary_required_attributes() -> None:
    """Test from_binary extracts required attributes"""
    message = AMQPMessage(
        properties={},
        application_properties={
            "cloudEvents_type": "com.example.test",
            "cloudEvents_source": "/test",
            "cloudEvents_id": "123",
            "cloudEvents_specversion": "1.0",
        },
        application_data=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "123"
    assert event.get_specversion() == "1.0"


def test_from_binary_with_timestamp_property() -> None:
    """Test from_binary parses AMQP timestamp (int milliseconds) to datetime"""
    dt = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
    timestamp_ms = int(dt.timestamp() * 1000)  # 1673781045000

    message = AMQPMessage(
        properties={},
        application_properties={
            "cloudEvents_type": "test",
            "cloudEvents_source": "/test",
            "cloudEvents_id": "123",
            "cloudEvents_specversion": "1.0",
            "cloudEvents_time": timestamp_ms,  # AMQP timestamp as int
        },
        application_data=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_time() == dt
    assert isinstance(event.get_time(), datetime)


def test_from_binary_with_timestamp_string() -> None:
    """Test from_binary also accepts ISO 8601 string (canonical form per spec)"""
    dt = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)

    message = AMQPMessage(
        properties={},
        application_properties={
            "cloudEvents_type": "test",
            "cloudEvents_source": "/test",
            "cloudEvents_id": "123",
            "cloudEvents_specversion": "1.0",
            "cloudEvents_time": "2023-01-15T10:30:45Z",  # ISO 8601 string (also valid)
        },
        application_data=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_time() == dt
    assert isinstance(event.get_time(), datetime)


def test_from_binary_with_boolean_property() -> None:
    """Test from_binary preserves boolean type"""
    message = AMQPMessage(
        properties={},
        application_properties={
            "cloudEvents_type": "test",
            "cloudEvents_source": "/test",
            "cloudEvents_id": "123",
            "cloudEvents_specversion": "1.0",
            "cloudEvents_boolext": True,
        },
        application_data=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_extension("boolext") is True
    assert isinstance(event.get_extension("boolext"), bool)


def test_from_binary_with_long_property() -> None:
    """Test from_binary preserves integer/long type"""
    message = AMQPMessage(
        properties={},
        application_properties={
            "cloudEvents_type": "test",
            "cloudEvents_source": "/test",
            "cloudEvents_id": "123",
            "cloudEvents_specversion": "1.0",
            "cloudEvents_intext": 42,
        },
        application_data=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_extension("intext") == 42
    assert isinstance(event.get_extension("intext"), int)


def test_from_binary_with_json_data() -> None:
    """Test from_binary with JSON data"""
    message = AMQPMessage(
        properties={"content-type": "application/json"},
        application_properties={
            "cloudEvents_type": "test",
            "cloudEvents_source": "/test",
            "cloudEvents_id": "123",
            "cloudEvents_specversion": "1.0",
        },
        application_data=b'{"message": "Hello"}',
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_data() == {"message": "Hello"}
    assert event.get_datacontenttype() == "application/json"


def test_from_binary_with_text_data() -> None:
    """Test from_binary with text data"""
    message = AMQPMessage(
        properties={"content-type": "text/plain"},
        application_properties={
            "cloudEvents_type": "test",
            "cloudEvents_source": "/test",
            "cloudEvents_id": "123",
            "cloudEvents_specversion": "1.0",
        },
        application_data=b"Hello World",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    # JSONFormat will decode as UTF-8 string for non-JSON content types
    assert event.get_data() == "Hello World"


def test_from_binary_with_bytes_data() -> None:
    """Test from_binary with binary data"""
    binary_data = b"\x00\x01\x02\x03"
    message = AMQPMessage(
        properties={"content-type": "application/octet-stream"},
        application_properties={
            "cloudEvents_type": "test",
            "cloudEvents_source": "/test",
            "cloudEvents_id": "123",
            "cloudEvents_specversion": "1.0",
        },
        application_data=binary_data,
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    # Binary data should be preserved
    assert isinstance(event.get_data(), (bytes, str))


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


def test_binary_preserves_types() -> None:
    """Test binary mode preserves native types (bool, int, datetime)"""
    dt = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
    original = create_event(
        extra_attrs={"time": dt, "boolext": True, "intext": 42, "strext": "value"}
    )

    message = to_binary(original, JSONFormat())
    recovered = from_binary(message, JSONFormat(), CloudEvent)

    # Types should be preserved
    assert recovered.get_time() == dt
    assert isinstance(recovered.get_time(), datetime)
    assert recovered.get_extension("boolext") is True
    assert isinstance(recovered.get_extension("boolext"), bool)
    assert recovered.get_extension("intext") == 42
    assert isinstance(recovered.get_extension("intext"), int)
    assert recovered.get_extension("strext") == "value"


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


def test_to_structured_basic_event() -> None:
    """Test to_structured with basic event"""
    event = create_event(data={"message": "Hello"})
    message = to_structured(event, JSONFormat())

    # Should have content-type in properties
    assert message.properties["content-type"] == "application/cloudevents+json"

    # application_data should contain the complete event
    assert b"com.example.test" in message.application_data
    assert b"message" in message.application_data


def test_to_structured_content_type_header() -> None:
    """Test to_structured sets correct content-type"""
    event = create_event()
    message = to_structured(event, JSONFormat())

    assert "content-type" in message.properties
    assert message.properties["content-type"] == "application/cloudevents+json"


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

    # All attributes should be in the serialized data
    assert b"test-subject" in message.application_data
    assert b"customext" in message.application_data


def test_from_structured_basic_event() -> None:
    """Test from_structured parses complete event"""
    message = AMQPMessage(
        properties={"content-type": "application/cloudevents+json"},
        application_properties={},
        application_data=b'{"type": "com.example.test", "source": "/test", '
        b'"id": "123", "specversion": "1.0", "data": {"message": "Hello"}}',
    )
    event = from_structured(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "123"
    assert event.get_data() == {"message": "Hello"}


def test_from_amqp_detects_binary_mode() -> None:
    """Test from_amqp detects binary mode"""
    message = AMQPMessage(
        properties={"content-type": "application/json"},
        application_properties={
            "cloudEvents_type": "test",
            "cloudEvents_source": "/test",
            "cloudEvents_id": "123",
            "cloudEvents_specversion": "1.0",
        },
        application_data=b'{"message": "Hello"}',
    )
    event = from_amqp(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "test"
    assert event.get_data() == {"message": "Hello"}


def test_from_amqp_detects_structured_mode() -> None:
    """Test from_amqp detects structured mode"""
    message = AMQPMessage(
        properties={"content-type": "application/cloudevents+json"},
        application_properties={},
        application_data=b'{"type": "com.example.test", "source": "/test", '
        b'"id": "123", "specversion": "1.0"}',
    )
    event = from_amqp(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"


def test_from_amqp_case_insensitive_detection() -> None:
    """Test from_amqp detection is case-insensitive"""
    # Uppercase CLOUDEVENTS
    message = AMQPMessage(
        properties={"content-type": "application/CLOUDEVENTS+json"},
        application_properties={},
        application_data=b'{"type": "com.example.test", "source": "/test", '
        b'"id": "123", "specversion": "1.0"}',
    )
    event = from_amqp(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"


def test_from_amqp_defaults_to_binary_when_no_content_type() -> None:
    """Test from_amqp defaults to binary mode when content-type is missing"""
    message = AMQPMessage(
        properties={},  # No content-type
        application_properties={
            "cloudEvents_type": "test",
            "cloudEvents_source": "/test",
            "cloudEvents_id": "123",
            "cloudEvents_specversion": "1.0",
        },
        application_data=b"{}",
    )
    event = from_amqp(message, JSONFormat(), CloudEvent)

    # Should successfully parse as binary mode
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

    # Data should be preserved, whether as dict or string representation
    data = recovered.get_data()
    if isinstance(data, dict):
        assert data == {"message": "Hello 世界 🌍"}
    else:
        assert "Hello 世界 🌍" in str(data)


def test_datetime_utc_handling() -> None:
    """Test datetime with UTC timezone"""
    dt_utc = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
    event = create_event(extra_attrs={"time": dt_utc})
    message = to_binary(event, JSONFormat())
    recovered = from_binary(message, JSONFormat(), CloudEvent)

    assert recovered.get_time() == dt_utc


def test_datetime_non_utc_handling() -> None:
    """Test datetime with non-UTC timezone"""
    from datetime import timedelta

    # Create a custom timezone (UTC+5)
    custom_tz = timezone(timedelta(hours=5))
    dt_custom = datetime(2023, 1, 15, 10, 30, 45, tzinfo=custom_tz)

    event = create_event(extra_attrs={"time": dt_custom})
    message = to_binary(event, JSONFormat())
    recovered = from_binary(message, JSONFormat(), CloudEvent)

    # Datetime should be preserved
    assert recovered.get_time() == dt_custom


def test_empty_application_properties() -> None:
    """Test message with no application properties (structured mode)"""
    message = AMQPMessage(
        properties={"content-type": "application/cloudevents+json"},
        application_properties={},
        application_data=b'{"type": "test", "source": "/test", "id": "123", '
        b'"specversion": "1.0"}',
    )
    event = from_structured(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "test"


def test_to_binary_with_multiple_extensions() -> None:
    """Test to_binary with multiple custom extensions"""
    event = create_event(
        extra_attrs={
            "ext1": "value1",
            "ext2": "value2",
            "ext3": 123,
            "ext4": True,
        }
    )
    message = to_binary(event, JSONFormat())

    assert message.application_properties["cloudEvents_ext1"] == "value1"
    assert message.application_properties["cloudEvents_ext2"] == "value2"
    assert message.application_properties["cloudEvents_ext3"] == 123
    assert message.application_properties["cloudEvents_ext4"] is True


def test_from_binary_ignores_non_cloudevents_properties() -> None:
    """Test from_binary only extracts cloudEvents_ prefixed properties"""
    message = AMQPMessage(
        properties={},
        application_properties={
            "cloudEvents_type": "test",
            "cloudEvents_source": "/test",
            "cloudEvents_id": "123",
            "cloudEvents_specversion": "1.0",
            "custom_property": "should-be-ignored",  # No cloudEvents_ prefix
            "another_prop": "also-ignored",
        },
        application_data=b"{}",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    # Only cloudEvents_ prefixed properties should be extracted
    assert event.get_type() == "test"
    # Non-prefixed properties should not become extensions
    # get_extension returns None for missing extensions
    assert event.get_extension("custom_property") is None
    assert event.get_extension("another_prop") is None
