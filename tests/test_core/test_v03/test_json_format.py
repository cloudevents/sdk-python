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
from datetime import datetime, timezone

from cloudevents.core.formats.json import JSONFormat
from cloudevents.core.v03.event import CloudEvent


def test_v03_json_read_minimal() -> None:
    """Test reading a minimal v0.3 CloudEvent from JSON"""
    json_data = b"""{
        "specversion": "0.3",
        "type": "com.example.test",
        "source": "/test",
        "id": "test-123"
    }"""

    format = JSONFormat()
    event = format.read(CloudEvent, json_data)

    assert event.get_specversion() == "0.3"
    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "test-123"
    assert event.get_data() is None


def test_v03_json_write_minimal() -> None:
    """Test writing a minimal v0.3 CloudEvent to JSON"""
    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
        }
    )

    format = JSONFormat()
    json_bytes = format.write(event)
    json_str = json_bytes.decode("utf-8")

    assert '"specversion": "0.3"' in json_str
    assert '"type": "com.example.test"' in json_str
    assert '"source": "/test"' in json_str
    assert '"id": "test-123"' in json_str


def test_v03_json_with_schemaurl() -> None:
    """Test v0.3 schemaurl attribute in JSON"""
    json_data = b"""{
        "specversion": "0.3",
        "type": "com.example.test",
        "source": "/test",
        "id": "test-123",
        "schemaurl": "https://example.com/schema.json"
    }"""

    format = JSONFormat()
    event = format.read(CloudEvent, json_data)

    assert event.get_schemaurl() == "https://example.com/schema.json"
    assert event.get_dataschema() == "https://example.com/schema.json"


def test_v03_json_write_with_schemaurl() -> None:
    """Test writing v0.3 event with schemaurl to JSON"""
    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
            "schemaurl": "https://example.com/schema.json",
        }
    )

    format = JSONFormat()
    json_bytes = format.write(event)
    json_str = json_bytes.decode("utf-8")

    assert '"schemaurl": "https://example.com/schema.json"' in json_str


def test_v03_json_with_datacontentencoding_base64() -> None:
    """Test v0.3 datacontentencoding with base64 encoded data"""
    # In v0.3, when datacontentencoding is base64, the data field contains base64 string
    original_data = b"Hello World!"
    base64_data = base64.b64encode(original_data).decode("utf-8")

    json_data = f'''{{
        "specversion": "0.3",
        "type": "com.example.test",
        "source": "/test",
        "id": "test-123",
        "datacontentencoding": "base64",
        "data": "{base64_data}"
    }}'''.encode("utf-8")

    format = JSONFormat()
    event = format.read(CloudEvent, json_data)

    assert event.get_datacontentencoding() == "base64"
    assert event.get_data() == original_data  # Should be decoded


def test_v03_json_write_binary_data_with_base64() -> None:
    """Test writing v0.3 event with binary data (uses datacontentencoding)"""
    binary_data = b"Hello World!"

    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
        },
        data=binary_data,
    )

    format = JSONFormat()
    json_bytes = format.write(event)
    json_str = json_bytes.decode("utf-8")

    # v0.3 should use datacontentencoding with base64-encoded data field
    assert '"datacontentencoding": "base64"' in json_str
    assert '"data"' in json_str
    assert '"data_base64"' not in json_str  # v1.0 field should not be present

    # Verify we can read it back
    event_read = format.read(CloudEvent, json_bytes)
    assert event_read.get_data() == binary_data


def test_v03_json_round_trip_with_binary_data() -> None:
    """Test complete round-trip of v0.3 event with binary data"""
    original_data = b"\x00\x01\x02\x03\x04\x05"

    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
            "datacontenttype": "application/octet-stream",
        },
        data=original_data,
    )

    format = JSONFormat()

    # Write to JSON
    json_bytes = format.write(event)

    # Read back
    event_read = format.read(CloudEvent, json_bytes)

    assert event_read.get_specversion() == "0.3"
    assert event_read.get_data() == original_data
    assert event_read.get_datacontentencoding() == "base64"


def test_v03_json_with_dict_data() -> None:
    """Test v0.3 event with JSON dict data"""
    json_data = b"""{
        "specversion": "0.3",
        "type": "com.example.test",
        "source": "/test",
        "id": "test-123",
        "datacontenttype": "application/json",
        "data": {"message": "Hello", "count": 42}
    }"""

    format = JSONFormat()
    event = format.read(CloudEvent, json_data)

    data = event.get_data()
    assert isinstance(data, dict)
    assert data["message"] == "Hello"
    assert data["count"] == 42


def test_v03_json_write_with_dict_data() -> None:
    """Test writing v0.3 event with dict data"""
    event = CloudEvent(
        attributes={
            "specversion": "0.3",
            "type": "com.example.test",
            "source": "/test",
            "id": "test-123",
            "datacontenttype": "application/json",
        },
        data={"message": "Hello", "count": 42},
    )

    format = JSONFormat()
    json_bytes = format.write(event)
    json_str = json_bytes.decode("utf-8")

    assert (
        '"data": {"message": "Hello", "count": 42}' in json_str
        or '"data": {"count": 42, "message": "Hello"}' in json_str
    )


def test_v03_json_with_time() -> None:
    """Test v0.3 event with time attribute"""
    json_data = b"""{
        "specversion": "0.3",
        "type": "com.example.test",
        "source": "/test",
        "id": "test-123",
        "time": "2023-06-15T14:30:45Z"
    }"""

    format = JSONFormat()
    event = format.read(CloudEvent, json_data)

    time = event.get_time()
    assert isinstance(time, datetime)
    assert time.year == 2023
    assert time.month == 6
    assert time.day == 15


def test_v03_json_write_with_time() -> None:
    """Test writing v0.3 event with time"""
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

    format = JSONFormat()
    json_bytes = format.write(event)
    json_str = json_bytes.decode("utf-8")

    assert '"time": "2023-06-15T14:30:45Z"' in json_str


def test_v03_json_complete_event() -> None:
    """Test v0.3 event with all optional attributes"""
    json_data = b"""{
        "specversion": "0.3",
        "type": "com.example.test",
        "source": "/test",
        "id": "test-123",
        "time": "2023-06-15T14:30:45Z",
        "subject": "test-subject",
        "datacontenttype": "application/json",
        "schemaurl": "https://example.com/schema.json",
        "customext": "custom-value",
        "data": {"message": "Hello"}
    }"""

    format = JSONFormat()
    event = format.read(CloudEvent, json_data)

    assert event.get_specversion() == "0.3"
    assert event.get_type() == "com.example.test"
    assert event.get_source() == "/test"
    assert event.get_id() == "test-123"
    assert event.get_subject() == "test-subject"
    assert event.get_datacontenttype() == "application/json"
    assert event.get_schemaurl() == "https://example.com/schema.json"
    assert event.get_extension("customext") == "custom-value"
    assert event.get_data() == {"message": "Hello"}


def test_v03_json_round_trip_complete() -> None:
    """Test complete round-trip of v0.3 event with all attributes"""
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
        data={"message": "Hello", "count": 42},
    )

    format = JSONFormat()

    # Write to JSON
    json_bytes = format.write(event)

    # Read back
    event_read = format.read(CloudEvent, json_bytes)

    assert event_read.get_specversion() == event.get_specversion()
    assert event_read.get_type() == event.get_type()
    assert event_read.get_source() == event.get_source()
    assert event_read.get_id() == event.get_id()
    assert event_read.get_subject() == event.get_subject()
    assert event_read.get_datacontenttype() == event.get_datacontenttype()
    assert event_read.get_schemaurl() == event.get_schemaurl()
    assert event_read.get_extension("customext") == event.get_extension("customext")
    assert event_read.get_data() == event.get_data()
