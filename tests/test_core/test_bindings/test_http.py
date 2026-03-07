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

from cloudevents.core.bindings.http import (
    HTTPMessage,
    from_binary,
    from_binary_event,
    from_http,
    from_http_event,
    from_structured,
    from_structured_event,
    to_binary,
    to_binary_event,
    to_structured,
    to_structured_event,
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


def test_http_message_creation() -> None:
    """Test basic HTTPMessage creation"""
    message = HTTPMessage(headers={"content-type": "application/json"}, body=b"test")
    assert message.headers == {"content-type": "application/json"}
    assert message.body == b"test"


def test_http_message_immutable() -> None:
    """Test that HTTPMessage is immutable (frozen dataclass)"""
    message = HTTPMessage(headers={"test": "value"}, body=b"data")

    with pytest.raises(Exception):  # FrozenInstanceError
        message.headers = {"new": "dict"}

    with pytest.raises(Exception):  # FrozenInstanceError
        message.body = b"new data"


def test_http_message_with_empty_headers() -> None:
    """Test HTTPMessage with empty headers"""
    message = HTTPMessage(headers={}, body=b"test")
    assert message.headers == {}
    assert message.body == b"test"


def test_http_message_with_empty_body() -> None:
    """Test HTTPMessage with empty body"""
    message = HTTPMessage(headers={"test": "value"}, body=b"")
    assert message.headers == {"test": "value"}
    assert message.body == b""


def test_http_message_equality() -> None:
    """Test HTTPMessage equality comparison"""
    msg1 = HTTPMessage(headers={"test": "value"}, body=b"data")
    msg2 = HTTPMessage(headers={"test": "value"}, body=b"data")
    msg3 = HTTPMessage(headers={"other": "value"}, body=b"data")

    assert msg1 == msg2
    assert msg1 != msg3


def test_to_binary_returns_http_message() -> None:
    """Test that to_binary returns an HTTPMessage instance"""
    event = create_event()
    message = to_binary(event, JSONFormat())
    assert isinstance(message, HTTPMessage)


def test_to_binary_required_attributes() -> None:
    """Test to_binary with only required attributes"""
    event = create_event()
    message = to_binary(event, JSONFormat())

    assert "ce-type" in message.headers
    assert message.headers["ce-type"] == "com.example.test"
    assert "ce-source" in message.headers
    assert message.headers["ce-source"] == "/test"  # Printable ASCII is not encoded
    assert "ce-id" in message.headers
    assert message.headers["ce-id"] == "test-id-123"
    assert "ce-specversion" in message.headers
    assert message.headers["ce-specversion"] == "1.0"


def test_to_binary_with_optional_attributes() -> None:
    """Test to_binary with optional attributes"""
    event = create_event(
        {"subject": "test-subject", "dataschema": "https://example.com/schema"},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    assert message.headers["ce-subject"] == "test-subject"
    # Printable ASCII (including : and /) is not encoded per CE spec 3.1.3.2
    assert message.headers["ce-dataschema"] == "https://example.com/schema"


def test_to_binary_with_extensions() -> None:
    """Test to_binary with extension attributes"""
    event = create_event(
        {"customext": "custom-value", "anotherext": "another-value"},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    assert message.headers["ce-customext"] == "custom-value"
    assert message.headers["ce-anotherext"] == "another-value"


def test_to_binary_with_json_data() -> None:
    """Test to_binary with dict (JSON) data"""
    event = create_event(
        {"datacontenttype": "application/json"},
        data={"message": "Hello", "count": 42},
    )
    message = to_binary(event, JSONFormat())

    assert message.body == b'{"message": "Hello", "count": 42}'
    assert message.headers["content-type"] == "application/json"


def test_to_binary_with_string_data() -> None:
    """Test to_binary with string data"""
    event = create_event(
        {"datacontenttype": "text/plain"},
        data="Hello World",
    )
    message = to_binary(event, JSONFormat())

    assert message.body == b"Hello World"
    assert message.headers["content-type"] == "text/plain"


def test_to_binary_with_bytes_data() -> None:
    """Test to_binary with bytes data"""
    event = create_event(
        {"datacontenttype": "application/octet-stream"},
        data=b"\x00\x01\x02\x03",
    )
    message = to_binary(event, JSONFormat())

    assert message.body == b"\x00\x01\x02\x03"
    assert message.headers["content-type"] == "application/octet-stream"


def test_to_binary_with_none_data() -> None:
    """Test to_binary with None data"""
    event = create_event()
    message = to_binary(event, JSONFormat())

    assert message.body == b""


def test_to_binary_datetime_encoding() -> None:
    """Test to_binary with datetime (time attribute)"""
    dt = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
    event = create_event(
        {"time": dt},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    # Should encode with 'Z' suffix for UTC, colons not encoded per CE spec
    assert "ce-time" in message.headers
    assert "2023-01-15T10:30:45Z" == message.headers["ce-time"]


def test_to_binary_special_characters() -> None:
    """Test to_binary with special characters in attributes"""
    event = create_event(
        {"subject": "Hello World!"},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    # Only space is encoded; ! is printable ASCII and left as-is per CE spec
    assert "ce-subject" in message.headers
    assert "Hello%20World!" == message.headers["ce-subject"]


def test_to_binary_datacontenttype_mapping() -> None:
    """Test that datacontenttype maps to Content-Type header"""
    event = create_event(
        {"datacontenttype": "application/xml"},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    assert "content-type" in message.headers
    assert message.headers["content-type"] == "application/xml"


def test_to_binary_no_ce_prefix_on_content_type() -> None:
    """Test that Content-Type header does not have ce- prefix"""
    event = create_event(
        {"datacontenttype": "application/json"},
        data={"test": "data"},
    )
    message = to_binary(event, JSONFormat())

    assert "content-type" in message.headers
    assert "ce-datacontenttype" not in message.headers


def test_to_binary_header_encoding() -> None:
    """Test percent encoding in headers"""
    event = create_event(
        {"subject": "test with spaces and special: chars"},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    # Per CE spec 3.1.3.2: only space, double-quote, percent, and non-printable ASCII encoded
    encoded_subject = message.headers["ce-subject"]
    assert " " not in encoded_subject  # Spaces should be encoded
    assert "%20" in encoded_subject  # Encoded space
    assert ":" in encoded_subject  # Colon is printable ASCII, not encoded


def test_from_binary_accepts_http_message() -> None:
    """Test that from_binary accepts HTTPMessage parameter"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-id",
            "ce-specversion": "1.0",
        },
        body=b"",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)
    assert event.get_type() == "com.example.test"


def test_from_binary_required_attributes() -> None:
    """Test from_binary parsing required attributes"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
            "ce-specversion": "1.0",
        },
        body=b"",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "test-123"
    assert event.get_specversion() == "1.0"


def test_from_binary_with_optional_attributes() -> None:
    """Test from_binary with optional attributes"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
            "ce-specversion": "1.0",
            "ce-subject": "test-subject",
            "ce-dataschema": "https://example.com/schema",
        },
        body=b"",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_subject() == "test-subject"
    assert event.get_dataschema() == "https://example.com/schema"


def test_from_binary_with_extensions() -> None:
    """Test from_binary with extension attributes"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
            "ce-specversion": "1.0",
            "ce-customext": "custom-value",
        },
        body=b"",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    attributes = event.get_attributes()
    assert attributes["customext"] == "custom-value"


def test_from_binary_with_json_data() -> None:
    """Test from_binary with JSON body"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
            "ce-specversion": "1.0",
            "content-type": "application/json",
        },
        body=b'{"message": "Hello", "count": 42}',
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    data = event.get_data()
    assert isinstance(data, dict)
    assert data["message"] == "Hello"
    assert data["count"] == 42


def test_from_binary_with_text_data() -> None:
    """Test from_binary with text body"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
            "ce-specversion": "1.0",
            "content-type": "text/plain",
        },
        body=b"Hello World",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    data = event.get_data()
    assert data == "Hello World"


def test_from_binary_with_bytes_data() -> None:
    """Test from_binary with binary body"""
    # Use bytes that are NOT valid UTF-8 to test binary handling
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
            "ce-specversion": "1.0",
            "content-type": "application/octet-stream",
        },
        body=b"\xff\xfe\xfd\xfc",  # Invalid UTF-8 bytes
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    data = event.get_data()
    # For non-UTF8 data, should remain as bytes
    assert isinstance(data, bytes)
    assert data == b"\xff\xfe\xfd\xfc"


def test_from_binary_datetime_parsing() -> None:
    """Test from_binary parsing time attribute"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
            "ce-specversion": "1.0",
            "ce-time": "2023-01-15T10%3A30%3A45Z",
        },
        body=b"",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    time = event.get_time()
    assert isinstance(time, datetime)
    assert time.year == 2023
    assert time.month == 1
    assert time.day == 15


def test_from_binary_header_decoding() -> None:
    """Test percent decoding of headers"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
            "ce-specversion": "1.0",
            "ce-subject": "Hello%20World%21",
        },
        body=b"",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    # Should be percent-decoded
    assert event.get_subject() == "Hello World!"


def test_from_binary_case_insensitive_headers() -> None:
    """Test that header parsing is case-insensitive"""
    message = HTTPMessage(
        headers={
            "CE-Type": "com.example.test",
            "Ce-Source": "/test",
            "ce-ID": "test-123",
            "CE-SPECVERSION": "1.0",
            "Content-Type": "application/json",
        },
        body=b'{"test": "data"}',
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"


def test_from_binary_content_type_as_datacontenttype() -> None:
    """Test that Content-Type header becomes datacontenttype attribute"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
            "ce-specversion": "1.0",
            "content-type": "application/xml",
        },
        body=b"<xml>data</xml>",
    )
    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_datacontenttype() == "application/xml"


def test_from_binary_round_trip() -> None:
    """Test that to_binary followed by from_binary preserves the event"""
    original = create_event(
        {"subject": "round-trip", "datacontenttype": "application/json"},
        data={"message": "Hello", "value": 123},
    )

    # Convert to binary
    message = to_binary(original, JSONFormat())

    # Parse back
    parsed = from_binary(message, JSONFormat(), CloudEvent)

    # Verify attributes
    assert parsed.get_type() == original.get_type()
    assert parsed.get_source() == original.get_source()
    assert parsed.get_subject() == original.get_subject()
    assert parsed.get_datacontenttype() == original.get_datacontenttype()

    # Verify data
    assert parsed.get_data() == original.get_data()


def test_to_structured_returns_http_message() -> None:
    """Test that to_structured returns an HTTPMessage instance"""
    event = create_event()
    message = to_structured(event, JSONFormat())
    assert isinstance(message, HTTPMessage)


def test_to_structured_basic_event() -> None:
    """Test to_structured with basic event"""
    event = create_event()
    message = to_structured(event, JSONFormat())

    # Should have JSON CloudEvents content type
    assert message.headers["content-type"] == "application/cloudevents+json"

    # Body should contain serialized event
    assert b'"type"' in message.body
    assert b'"source"' in message.body
    assert b"com.example.test" in message.body


def test_to_structured_content_type_header() -> None:
    """Test that to_structured sets correct Content-Type header"""
    event = create_event()
    message = to_structured(event, JSONFormat())

    assert "content-type" in message.headers
    assert message.headers["content-type"] == "application/cloudevents+json"


def test_to_structured_with_all_attributes() -> None:
    """Test to_structured with all attributes"""
    event = create_event(
        {
            "subject": "test-subject",
            "datacontenttype": "application/json",
            "dataschema": "https://example.com/schema",
            "customext": "custom-value",
        },
        data={"message": "Hello"},
    )
    message = to_structured(event, JSONFormat())

    # All attributes should be in the body
    assert b'"type"' in message.body
    assert b'"source"' in message.body
    assert b'"subject"' in message.body
    assert b'"datacontenttype"' in message.body
    assert b'"dataschema"' in message.body
    assert b'"customext"' in message.body
    assert b'"data"' in message.body


def test_to_structured_with_binary_data() -> None:
    """Test to_structured with binary data"""
    event = create_event(
        data=b"\x00\x01\x02\x03",
    )
    message = to_structured(event, JSONFormat())

    # Binary data should be base64 encoded in JSON
    assert b'"data_base64"' in message.body
    assert b'"data"' not in message.body  # Should not have 'data' field


def test_from_structured_accepts_http_message() -> None:
    """Test that from_structured accepts HTTPMessage parameter"""
    message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"type": "com.example.test", "source": "/test", "id": "123", "specversion": "1.0"}',
    )
    event = from_structured(message, JSONFormat(), CloudEvent)
    assert event.get_type() == "com.example.test"


def test_from_structured_basic_event() -> None:
    """Test from_structured with basic event"""
    message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"type": "com.example.test", "source": "/test", "id": "123", "specversion": "1.0"}',
    )
    event = from_structured(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "123"
    assert event.get_specversion() == "1.0"


def test_from_structured_round_trip() -> None:
    """Test that to_structured followed by from_structured preserves the event"""
    original = create_event(
        {
            "subject": "round-trip",
            "datacontenttype": "application/json",
            "customext": "custom-value",
        },
        data={"message": "Hello", "value": 123},
    )

    # Convert to structured
    message = to_structured(original, JSONFormat())

    # Parse back
    parsed = from_structured(message, JSONFormat(), CloudEvent)

    # Verify attributes
    assert parsed.get_type() == original.get_type()
    assert parsed.get_source() == original.get_source()
    assert parsed.get_subject() == original.get_subject()
    assert parsed.get_datacontenttype() == original.get_datacontenttype()

    # Verify data
    assert parsed.get_data() == original.get_data()


def test_from_http_accepts_http_message() -> None:
    """Test that from_http accepts HTTPMessage parameter"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        body=b"",
    )
    event = from_http(message, JSONFormat(), CloudEvent)
    assert event.get_type() == "com.example.test"


def test_from_http_detects_binary_mode() -> None:
    """Test that from_http detects binary mode from ce- headers"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        body=b"test data",
    )
    event = from_http(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"


def test_from_http_detects_structured_mode() -> None:
    """Test that from_http detects structured mode when no ce- headers"""
    message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"type": "com.example.test", "source": "/test", "id": "123", "specversion": "1.0"}',
    )
    event = from_http(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"


def test_from_http_binary_mode_with_content_type() -> None:
    """Test from_http with binary mode and Content-Type"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
            "content-type": "application/json",
        },
        body=b'{"message": "Hello"}',
    )
    event = from_http(message, JSONFormat(), CloudEvent)

    # Should detect binary mode due to ce- headers
    data = event.get_data()
    assert isinstance(data, dict)
    assert data["message"] == "Hello"


def test_from_http_structured_mode_json() -> None:
    """Test from_http with structured JSON event"""
    message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"type": "com.example.test", "source": "/test", "id": "123", "specversion": "1.0", "data": {"msg": "Hi"}}',
    )
    event = from_http(message, JSONFormat(), CloudEvent)

    assert event.get_type() == "com.example.test"
    data = event.get_data()
    assert isinstance(data, dict)
    assert data["msg"] == "Hi"


def test_from_http_defaults_to_structured() -> None:
    """Test that from_http defaults to structured mode when ambiguous"""
    message = HTTPMessage(
        headers={"content-type": "application/json"},
        body=b'{"type": "com.example.test", "source": "/test", "id": "123", "specversion": "1.0"}',
    )
    event = from_http(message, JSONFormat(), CloudEvent)

    # Should parse as structured mode
    assert event.get_type() == "com.example.test"


def test_from_http_case_insensitive_detection() -> None:
    """Test that from_http detection is case-insensitive"""
    message = HTTPMessage(
        headers={
            "CE-Type": "com.example.test",
            "CE-Source": "/test",
            "CE-ID": "123",
            "CE-SPECVERSION": "1.0",
        },
        body=b"",
    )
    event = from_http(message, JSONFormat(), CloudEvent)

    # Should detect binary mode despite mixed case
    assert event.get_type() == "com.example.test"


def test_from_http_mixed_headers() -> None:
    """Test from_http when both ce- headers and structured content are present"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.binary",
            "ce-source": "/binary",
            "ce-id": "123",
            "ce-specversion": "1.0",
            "content-type": "application/cloudevents+json",
        },
        body=b'{"type": "com.example.structured", "source": "/structured", "id": "456", "specversion": "1.0"}',
    )
    event = from_http(message, JSONFormat(), CloudEvent)

    # Binary mode should take precedence (ce- headers present)
    assert event.get_type() == "com.example.binary"
    assert event.get_source() == "/binary"


def test_percent_encoding_special_chars() -> None:
    """Test percent encoding of special characters"""
    event = create_event(
        {"subject": 'Hello World! "quotes" & special'},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    # Per CE spec: space and double-quote are encoded, but & is printable ASCII
    encoded = message.headers["ce-subject"]
    assert " " not in encoded
    assert '"' not in encoded
    assert "&" in encoded  # & is printable ASCII (U+0026), not encoded


def test_percent_encoding_spec_example() -> None:
    """Test the example from CE HTTP binding spec section 3.1.3.2:
    'Euro € 😀' SHOULD be encoded as 'Euro%20%E2%82%AC%20%F0%9F%98%80'
    """
    event = create_event(
        {"subject": "Euro € 😀"},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    assert message.headers["ce-subject"] == "Euro%20%E2%82%AC%20%F0%9F%98%80"

    # Round-trip: decode back to original
    parsed = from_binary(message, JSONFormat(), CloudEvent)
    assert parsed.get_subject() == "Euro € 😀"


def test_percent_encoding_unicode() -> None:
    """Test percent encoding of unicode characters"""
    event = create_event(
        {"subject": "Hello 世界 🌍"},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    # Unicode should be percent-encoded
    encoded = message.headers["ce-subject"]
    assert "世界" not in encoded
    assert "🌍" not in encoded
    assert "%" in encoded  # Should have percent-encoded bytes


def test_percent_decoding_round_trip() -> None:
    """Test that percent encoding/decoding is reversible"""
    original_subject = 'Test: "quotes", spaces & unicode 世界'
    event = create_event(
        {"subject": original_subject},
        data=None,
    )

    # Encode
    message = to_binary(event, JSONFormat())

    # Decode
    parsed = from_binary(message, JSONFormat(), CloudEvent)

    # Should match original
    assert parsed.get_subject() == original_subject


def test_datetime_encoding_utc() -> None:
    """Test datetime encoding for UTC timezone"""
    dt_utc = datetime(2023, 6, 15, 14, 30, 45, tzinfo=timezone.utc)
    event = create_event(
        {"time": dt_utc},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    # Should use 'Z' suffix for UTC
    time_header = message.headers["ce-time"]
    assert "Z" in time_header or "%5A" in time_header  # Z or encoded Z


def test_datetime_encoding_non_utc() -> None:
    """Test datetime encoding for non-UTC timezone"""
    from datetime import timedelta

    # Create timezone +05:30 (IST)
    dt_ist = datetime(
        2023, 6, 15, 14, 30, 45, tzinfo=timezone(timedelta(hours=5, minutes=30))
    )
    event = create_event(
        {"time": dt_ist},
        data=None,
    )
    message = to_binary(event, JSONFormat())

    # Should preserve timezone offset
    time_header = message.headers["ce-time"]
    # Will be percent-encoded but should contain timezone info
    assert "ce-time" in message.headers


def test_datetime_parsing_rfc3339() -> None:
    """Test parsing various RFC 3339 datetime formats"""
    test_cases = [
        "2023-01-15T10:30:45Z",
        "2023-01-15T10%3A30%3A45Z",
        "2023-01-15T10:30:45.123Z",
        "2023-01-15T10:30:45%2B00:00",
    ]

    for time_str in test_cases:
        message = HTTPMessage(
            headers={
                "ce-type": "com.example.test",
                "ce-source": "/test",
                "ce-id": "123",
                "ce-specversion": "1.0",
                "ce-time": time_str,
            },
            body=b"",
        )
        event = from_binary(message, JSONFormat(), CloudEvent)

        # Should successfully parse to datetime
        time = event.get_time()
        assert isinstance(time, datetime)


def test_http_binary_with_json_format() -> None:
    """Test complete binary mode flow with JSON format"""
    # Create event
    event = create_event(
        {
            "type": "com.example.order.created",
            "source": "/orders/service",
            "subject": "order-123",
            "datacontenttype": "application/json",
        },
        data={"orderId": "123", "amount": 99.99, "status": "pending"},
    )

    # Convert to HTTP binary mode
    message = to_binary(event, JSONFormat())

    # Verify headers
    assert message.headers["ce-type"] == "com.example.order.created"
    assert message.headers["content-type"] == "application/json"

    # Verify body
    assert b'"orderId"' in message.body
    assert b'"123"' in message.body

    # Parse back
    parsed = from_binary(message, JSONFormat(), CloudEvent)

    # Verify round-trip
    assert parsed.get_type() == event.get_type()
    assert parsed.get_source() == event.get_source()
    parsed_data = parsed.get_data()
    assert isinstance(parsed_data, dict)
    assert parsed_data["orderId"] == "123"


def test_http_structured_with_json_format() -> None:
    """Test complete structured mode flow with JSON format"""
    # Create event
    event = create_event(
        {
            "type": "com.example.user.registered",
            "source": "/users/service",
            "datacontenttype": "application/json",
        },
        data={"userId": "user-456", "email": "test@example.com"},
    )

    # Convert to HTTP structured mode
    message = to_structured(event, JSONFormat())

    # Verify content type
    assert message.headers["content-type"] == "application/cloudevents+json"

    # Verify body contains everything
    assert b'"type"' in message.body
    assert b'"source"' in message.body
    assert b'"data"' in message.body
    assert b'"userId"' in message.body

    # Parse back
    parsed = from_structured(message, JSONFormat(), CloudEvent)

    # Verify round-trip
    assert parsed.get_type() == event.get_type()
    assert parsed.get_source() == event.get_source()
    parsed_data = parsed.get_data()
    assert isinstance(parsed_data, dict)
    assert parsed_data["userId"] == "user-456"


def test_custom_event_factory() -> None:
    """Test using custom event factory function"""

    def custom_factory(
        attributes: dict[str, Any], data: dict[str, Any] | str | bytes | None
    ) -> CloudEvent:
        # Custom factory that adds a prefix to the type
        attributes["type"] = f"custom.{attributes.get('type', 'unknown')}"
        return CloudEvent(attributes, data)

    message = HTTPMessage(
        headers={
            "ce-type": "test.event",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        body=b"",
    )

    event = from_binary(message, JSONFormat(), custom_factory)

    # Should use custom factory
    assert event.get_type() == "custom.test.event"


def test_real_world_scenario() -> None:
    """Test a realistic end-to-end scenario"""
    # Simulate a webhook notification
    original_event = create_event(
        {
            "type": "com.github.push",
            "source": "https://github.com/myorg/myrepo",
            "subject": "refs/heads/main",
            "datacontenttype": "application/json",
        },
        data={
            "ref": "refs/heads/main",
            "commits": [
                {"id": "abc123", "message": "Fix bug"},
                {"id": "def456", "message": "Add feature"},
            ],
        },
    )

    # Send as HTTP binary mode
    http_message = to_binary(original_event, JSONFormat())

    # Simulate network transmission (receiver side)
    # Receiver auto-detects mode and parses
    received_event = from_http(http_message, JSONFormat(), CloudEvent)

    # Verify data integrity
    assert received_event.get_type() == "com.github.push"
    assert received_event.get_source() == "https://github.com/myorg/myrepo"
    assert received_event.get_subject() == "refs/heads/main"

    data = received_event.get_data()
    assert isinstance(data, dict)
    assert data["ref"] == "refs/heads/main"
    assert len(data["commits"]) == 2
    assert data["commits"][0]["message"] == "Fix bug"


def test_to_binary_with_defaults() -> None:
    """Test to_binary_event convenience wrapper using default JSONFormat"""
    event = create_event(
        extra_attrs={"datacontenttype": "application/json"},
        data={"message": "Hello"},
    )

    message = to_binary_event(event)

    assert "ce-type" in message.headers
    assert message.headers["ce-type"] == "com.example.test"
    assert b'"message"' in message.body
    assert b'"Hello"' in message.body


def test_to_structured_with_defaults() -> None:
    """Test to_structured_event convenience wrapper using default JSONFormat"""
    event = create_event(data={"message": "Hello"})

    message = to_structured_event(event)

    assert "content-type" in message.headers
    assert message.headers["content-type"] == "application/cloudevents+json"
    assert b'"type"' in message.body
    assert b'"com.example.test"' in message.body
    assert b'"data"' in message.body


def test_from_binary_with_defaults() -> None:
    """Test from_binary_event convenience wrapper using default JSONFormat and CloudEvent factory"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
            "content-type": "application/json",
        },
        body=b'{"message": "Hello"}',
    )

    event = from_binary_event(message)

    assert isinstance(event, CloudEvent)
    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "123"
    assert event.get_data() == {"message": "Hello"}


def test_from_structured_with_defaults() -> None:
    """Test from_structured_event convenience wrapper using default JSONFormat and CloudEvent factory"""
    message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"type": "com.example.test", "source": "/test", "id": "123", "specversion": "1.0", "data": {"message": "Hello"}}',
    )

    event = from_structured_event(message)

    assert isinstance(event, CloudEvent)
    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "123"
    assert event.get_data() == {"message": "Hello"}


def test_from_http_with_defaults_binary() -> None:
    """Test from_http_event convenience wrapper with auto-detection (binary mode)"""
    message = HTTPMessage(
        headers={
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "123",
            "ce-specversion": "1.0",
        },
        body=b'{"message": "Hello"}',
    )

    event = from_http_event(message)

    assert isinstance(event, CloudEvent)
    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"


def test_from_http_with_defaults_structured() -> None:
    """Test from_http_event convenience wrapper with auto-detection (structured mode)"""
    message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"type": "com.example.test", "source": "/test", "id": "123", "specversion": "1.0"}',
    )

    # Call wrapper function (should use defaults and detect structured mode)
    event = from_http_event(message)

    assert isinstance(event, CloudEvent)
    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"


def test_convenience_roundtrip_binary() -> None:
    """Test complete roundtrip using convenience wrapper functions with binary mode"""
    original_event = create_event(
        extra_attrs={"datacontenttype": "application/json"},
        data={"message": "Roundtrip test"},
    )

    # Convert to message using wrapper
    message = to_binary_event(original_event)

    # Convert back using wrapper
    recovered_event = from_binary_event(message)

    assert recovered_event.get_type() == original_event.get_type()
    assert recovered_event.get_source() == original_event.get_source()
    assert recovered_event.get_id() == original_event.get_id()
    assert recovered_event.get_data() == original_event.get_data()


def test_convenience_roundtrip_structured() -> None:
    """Test complete roundtrip using convenience wrapper functions with structured mode"""
    original_event = create_event(
        extra_attrs={"datacontenttype": "application/json"},
        data={"message": "Roundtrip test"},
    )

    # Convert to message using wrapper
    message = to_structured_event(original_event)

    # Convert back using wrapper
    recovered_event = from_structured_event(message)

    assert recovered_event.get_type() == original_event.get_type()
    assert recovered_event.get_source() == original_event.get_source()
    assert recovered_event.get_id() == original_event.get_id()
    assert recovered_event.get_data() == original_event.get_data()


def test_convenience_with_explicit_format_override() -> None:
    """Test that wrapper functions can override format (still flexible)"""
    event = create_event(
        extra_attrs={"datacontenttype": "application/json"},
        data={"message": "Hello"},
    )

    message = to_binary_event(event, JSONFormat())
    recovered = from_binary_event(message, JSONFormat())

    assert recovered.get_type() == event.get_type()
    assert recovered.get_data() == event.get_data()
