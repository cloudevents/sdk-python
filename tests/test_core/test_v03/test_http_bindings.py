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

from cloudevents.core.bindings.http import (
    HTTPMessage,
    from_binary,
    from_binary_event,
    from_http,
    from_http_event,
    from_structured,
    from_structured_event,
    to_binary,
    to_structured,
)
from cloudevents.core.formats.json import JSONFormat
from cloudevents.core.v03.event import CloudEvent


def test_v03_to_binary_minimal() -> None:
    """Test converting minimal v0.3 event to HTTP binary mode"""
    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
        }
    )

    message = to_binary(event, JSONFormat())

    assert "ce-specversion" in message.headers
    assert message.headers["ce-specversion"] == "0.3"
    assert "ce-type" in message.headers
    assert "ce-source" in message.headers
    assert "ce-id" in message.headers


def test_v03_to_binary_with_schemaurl() -> None:
    """Test converting v0.3 event with schemaurl to HTTP binary mode"""
    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
            "schemaurl": "https://example.com/schema.json",
        }
    )

    message = to_binary(event, JSONFormat())

    assert "ce-schemaurl" in message.headers
    # URL should be percent-encoded
    assert "https" in message.headers["ce-schemaurl"]


def test_v03_to_binary_with_datacontentencoding() -> None:
    """Test converting v0.3 event with datacontentencoding to HTTP binary mode"""
    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
            "datacontentencoding": "base64",
        }
    )

    message = to_binary(event, JSONFormat())

    assert "ce-datacontentencoding" in message.headers
    assert message.headers["ce-datacontentencoding"] == "base64"


def test_v03_from_binary_minimal() -> None:
    """Test parsing minimal v0.3 binary HTTP message"""
    message = HTTPMessage(
        headers={
            "ce-specversion": "0.3",
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
        },
        body=b"",
    )

    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_specversion() == "0.3"
    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "test-123"


def test_v03_from_binary_with_schemaurl() -> None:
    """Test parsing v0.3 binary HTTP message with schemaurl"""
    message = HTTPMessage(
        headers={
            "ce-specversion": "0.3",
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
            "ce-schemaurl": "https://example.com/schema.json",
        },
        body=b"",
    )

    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_schemaurl() == "https://example.com/schema.json"


def test_v03_from_binary_with_datacontentencoding() -> None:
    """Test parsing v0.3 binary HTTP message with datacontentencoding"""
    message = HTTPMessage(
        headers={
            "ce-specversion": "0.3",
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
            "ce-datacontentencoding": "base64",
        },
        body=b"",
    )

    event = from_binary(message, JSONFormat(), CloudEvent)

    assert event.get_datacontentencoding() == "base64"


def test_v03_binary_round_trip() -> None:
    """Test v0.3 binary mode round-trip"""
    original = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
            "subject": "test-subject",
            "schemaurl": "https://example.com/schema.json",
            "datacontenttype": "application/json",
        },
        data={"message": "Hello", "count": 42},
    )

    # Convert to binary
    message = to_binary(original, JSONFormat())

    # Parse back
    parsed = from_binary(message, JSONFormat(), CloudEvent)

    assert parsed.get_specversion() == original.get_specversion()
    assert parsed.get_type() == original.get_type()
    assert parsed.get_source() == original.get_source()
    assert parsed.get_id() == original.get_id()
    assert parsed.get_subject() == original.get_subject()
    assert parsed.get_schemaurl() == original.get_schemaurl()
    assert parsed.get_datacontenttype() == original.get_datacontenttype()
    assert parsed.get_data() == original.get_data()


def test_v03_to_structured_minimal() -> None:
    """Test converting minimal v0.3 event to HTTP structured mode"""
    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
        }
    )

    message = to_structured(event, JSONFormat())

    assert message.headers["content-type"] == "application/cloudevents+json"
    assert b'"specversion": "0.3"' in message.body
    assert b'"type": "com.example.test"' in message.body


def test_v03_to_structured_with_schemaurl() -> None:
    """Test converting v0.3 event with schemaurl to structured mode"""
    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
            "schemaurl": "https://example.com/schema.json",
        }
    )

    message = to_structured(event, JSONFormat())

    assert b'"schemaurl": "https://example.com/schema.json"' in message.body


def test_v03_from_structured_minimal() -> None:
    """Test parsing minimal v0.3 structured HTTP message"""
    message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"specversion": "0.3", "type": "com.example.test", "source": "/test", "id": "test-123"}',
    )

    event = from_structured(message, JSONFormat(), CloudEvent)

    assert event.get_specversion() == "0.3"
    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "test-123"


def test_v03_from_structured_with_schemaurl() -> None:
    """Test parsing v0.3 structured HTTP message with schemaurl"""
    message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"specversion": "0.3", "type": "com.example.test", "source": "/test", "id": "test-123", "schemaurl": "https://example.com/schema.json"}',
    )

    event = from_structured(message, JSONFormat(), CloudEvent)

    assert event.get_schemaurl() == "https://example.com/schema.json"


def test_v03_structured_round_trip() -> None:
    """Test v0.3 structured mode round-trip"""
    original = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
            "subject": "test-subject",
            "schemaurl": "https://example.com/schema.json",
            "datacontenttype": "application/json",
        },
        data={"message": "Hello", "count": 42},
    )

    # Convert to structured
    message = to_structured(original, JSONFormat())

    # Parse back
    parsed = from_structured(message, JSONFormat(), CloudEvent)

    assert parsed.get_specversion() == original.get_specversion()
    assert parsed.get_type() == original.get_type()
    assert parsed.get_source() == original.get_source()
    assert parsed.get_id() == original.get_id()
    assert parsed.get_subject() == original.get_subject()
    assert parsed.get_schemaurl() == original.get_schemaurl()
    assert parsed.get_datacontenttype() == original.get_datacontenttype()
    assert parsed.get_data() == original.get_data()


def test_v03_from_http_auto_detects_binary() -> None:
    """Test that from_http auto-detects v0.3 binary mode"""
    message = HTTPMessage(
        headers={
            "ce-specversion": "0.3",
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
        },
        body=b"",
    )

    event = from_http(message, JSONFormat(), CloudEvent)

    assert event.get_specversion() == "0.3"
    assert event.get_type() == "com.example.test"


def test_v03_from_http_auto_detects_structured() -> None:
    """Test that from_http auto-detects v0.3 structured mode"""
    message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"specversion": "0.3", "type": "com.example.test", "source": "/test", "id": "test-123"}',
    )

    event = from_http(message, JSONFormat(), CloudEvent)

    assert event.get_specversion() == "0.3"
    assert event.get_type() == "com.example.test"


def test_v03_auto_detect_version_from_binary_headers() -> None:
    """Test auto-detection of v0.3 from binary mode headers"""
    message = HTTPMessage(
        headers={
            "ce-specversion": "0.3",
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
        },
        body=b"",
    )

    # Don't provide event_factory, let it auto-detect
    event = from_binary(message, JSONFormat())

    assert isinstance(event, CloudEvent)
    assert event.get_specversion() == "0.3"


def test_v03_auto_detect_version_from_structured_body() -> None:
    """Test auto-detection of v0.3 from structured mode body"""
    message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"specversion": "0.3", "type": "com.example.test", "source": "/test", "id": "test-123"}',
    )

    # Don't provide event_factory, let it auto-detect
    event = from_structured(message, JSONFormat())

    assert isinstance(event, CloudEvent)
    assert event.get_specversion() == "0.3"


def test_v03_from_http_auto_detect_version_binary() -> None:
    """Test from_http auto-detects v0.3 with no explicit factory"""
    message = HTTPMessage(
        headers={
            "ce-specversion": "0.3",
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
        },
        body=b"",
    )

    # Auto-detect both mode and version
    event = from_http(message, JSONFormat())

    assert isinstance(event, CloudEvent)
    assert event.get_specversion() == "0.3"


def test_v03_from_http_auto_detect_version_structured() -> None:
    """Test from_http auto-detects v0.3 structured with no explicit factory"""
    message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"specversion": "0.3", "type": "com.example.test", "source": "/test", "id": "test-123"}',
    )

    # Auto-detect both mode and version
    event = from_http(message, JSONFormat())

    assert isinstance(event, CloudEvent)
    assert event.get_specversion() == "0.3"


def test_v03_convenience_wrappers_binary() -> None:
    """Test convenience wrapper functions with v0.3 binary mode"""
    message = HTTPMessage(
        headers={
            "ce-specversion": "0.3",
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
        },
        body=b"",
    )

    event = from_binary_event(message)

    assert isinstance(event, CloudEvent)
    assert event.get_specversion() == "0.3"


def test_v03_convenience_wrappers_structured() -> None:
    """Test convenience wrapper functions with v0.3 structured mode"""
    message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"specversion": "0.3", "type": "com.example.test", "source": "/test", "id": "test-123"}',
    )

    event = from_structured_event(message)

    assert isinstance(event, CloudEvent)
    assert event.get_specversion() == "0.3"


def test_v03_convenience_wrappers_from_http() -> None:
    """Test from_http_event convenience wrapper with v0.3"""
    # Binary mode
    binary_message = HTTPMessage(
        headers={
            "ce-specversion": "0.3",
            "ce-type": "com.example.test",
            "ce-source": "/test",
            "ce-id": "test-123",
        },
        body=b"",
    )

    event1 = from_http_event(binary_message)
    assert event1.get_specversion() == "0.3"

    # Structured mode
    structured_message = HTTPMessage(
        headers={"content-type": "application/cloudevents+json"},
        body=b'{"specversion": "0.3", "type": "com.example.test", "source": "/test", "id": "test-123"}',
    )

    event2 = from_http_event(structured_message)
    assert event2.get_specversion() == "0.3"


def test_v03_binary_with_time() -> None:
    """Test v0.3 binary mode with time attribute"""
    dt = datetime(2023, 6, 15, 14, 30, 45, tzinfo=timezone.utc)

    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
            "time": dt,
        }
    )

    message = to_binary(event, JSONFormat())
    parsed = from_binary(message, JSONFormat(), CloudEvent)

    assert parsed.get_time() is not None
    assert parsed.get_time().year == 2023


def test_v03_complete_binary_event() -> None:
    """Test v0.3 complete event with all attributes in binary mode"""
    dt = datetime(2023, 6, 15, 14, 30, 45, tzinfo=timezone.utc)

    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
            "time": dt,
            "subject": "test-subject",
            "datacontenttype": "application/json",
            "datacontentencoding": "base64",
            "schemaurl": "https://example.com/schema.json",
            "customext": "custom-value",
        },
        data={"message": "Hello World!"},
    )

    message = to_binary(event, JSONFormat())
    parsed = from_binary(message, JSONFormat())  # Auto-detect

    assert isinstance(parsed, CloudEvent)
    assert parsed.get_specversion() == "0.3"
    assert parsed.get_type() == "com.example.test"
    assert parsed.get_source() == "/test"
    assert parsed.get_id() == "test-123"
    assert parsed.get_subject() == "test-subject"
    assert parsed.get_datacontenttype() == "application/json"
    assert parsed.get_datacontentencoding() == "base64"
    assert parsed.get_schemaurl() == "https://example.com/schema.json"
    assert parsed.get_extension("customext") == "custom-value"
    assert parsed.get_data() == {"message": "Hello World!"}


def test_v03_complete_structured_event() -> None:
    """Test v0.3 complete event with all attributes in structured mode"""
    dt = datetime(2023, 6, 15, 14, 30, 45, tzinfo=timezone.utc)

    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
            "time": dt,
            "subject": "test-subject",
            "datacontenttype": "application/json",
            "schemaurl": "https://example.com/schema.json",
            "customext": "custom-value",
        },
        data={"message": "Hello World!"},
    )

    message = to_structured(event, JSONFormat())
    parsed = from_structured(message, JSONFormat())  # Auto-detect

    assert isinstance(parsed, CloudEvent)
    assert parsed.get_specversion() == "0.3"
    assert parsed.get_type() == "com.example.test"
    assert parsed.get_source() == "/test"
    assert parsed.get_id() == "test-123"
    assert parsed.get_subject() == "test-subject"
    assert parsed.get_datacontenttype() == "application/json"
    assert parsed.get_schemaurl() == "https://example.com/schema.json"
    assert parsed.get_extension("customext") == "custom-value"
    assert parsed.get_data() == {"message": "Hello World!"}
