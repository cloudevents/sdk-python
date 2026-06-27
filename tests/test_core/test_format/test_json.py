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
from json import loads

import pytest

from cloudevents.core.exceptions import BaseCloudEventException
from cloudevents.core.formats.json import JSONFormat
from cloudevents.core.v1.event import CloudEvent


def test_write_cloud_event_to_json_with_attributes_only() -> None:
    attributes = {
        "id": "123",
        "source": "source",
        "type": "type",
        "specversion": "1.0",
        "time": datetime(2023, 10, 25, 17, 9, 19, 736166, tzinfo=timezone.utc),
        "datacontenttype": "application/json",
        "dataschema": "http://example.com/schema",
        "subject": "test_subject",
    }
    event = CloudEvent(attributes=attributes, data=None)
    formatter = JSONFormat()
    result = formatter.write(event)

    assert (
        result
        == '{"id": "123", "source": "source", "type": "type", "specversion": "1.0", "time": "2023-10-25T17:09:19.736166Z", "datacontenttype": "application/json", "dataschema": "http://example.com/schema", "subject": "test_subject"}'.encode(
            "utf-8"
        )
    )


def test_write_cloud_event_to_json_with_data_as_json() -> None:
    attributes = {
        "id": "123",
        "source": "source",
        "type": "type",
        "specversion": "1.0",
        "time": datetime(2023, 10, 25, 17, 9, 19, 736166, tzinfo=timezone.utc),
        "datacontenttype": "application/json",
        "dataschema": "http://example.com/schema",
        "subject": "test_subject",
    }
    event = CloudEvent(attributes=attributes, data={"key": "value"})
    formatter = JSONFormat()
    result = formatter.write(event)

    assert (
        result
        == '{"id": "123", "source": "source", "type": "type", "specversion": "1.0", "time": "2023-10-25T17:09:19.736166Z", "datacontenttype": "application/json", "dataschema": "http://example.com/schema", "subject": "test_subject", "data": {"key": "value"}}'.encode(
            "utf-8"
        )
    )


def test_write_cloud_event_to_json_with_data_as_bytes() -> None:
    attributes = {
        "id": "123",
        "source": "source",
        "type": "type",
        "specversion": "1.0",
        "time": datetime(2023, 10, 25, 17, 9, 19, 736166, tzinfo=timezone.utc),
        "datacontenttype": "application/json",
        "dataschema": "http://example.com/schema",
        "subject": "test_subject",
    }
    event = CloudEvent(attributes=attributes, data=b"test")
    formatter = JSONFormat()
    result = formatter.write(event)

    assert (
        result
        == '{"id": "123", "source": "source", "type": "type", "specversion": "1.0", "time": "2023-10-25T17:09:19.736166Z", "datacontenttype": "application/json", "dataschema": "http://example.com/schema", "subject": "test_subject", "data_base64": "dGVzdA=="}'.encode(
            "utf-8"
        )
    )


def test_write_cloud_event_to_json_with_data_as_str_and_content_type_not_json() -> None:
    attributes = {
        "id": "123",
        "source": "source",
        "type": "type",
        "specversion": "1.0",
        "time": datetime(2023, 10, 25, 17, 9, 19, 736166, tzinfo=timezone.utc),
        "datacontenttype": "text/plain",
        "dataschema": "http://example.com/schema",
        "subject": "test_subject",
    }
    event = CloudEvent(attributes=attributes, data="test")
    formatter = JSONFormat()
    result = formatter.write(event)

    assert (
        result
        == '{"id": "123", "source": "source", "type": "type", "specversion": "1.0", "time": "2023-10-25T17:09:19.736166Z", "datacontenttype": "text/plain", "dataschema": "http://example.com/schema", "subject": "test_subject", "data": "test"}'.encode(
            "utf-8"
        )
    )


def test_write_cloud_event_to_json_with_no_content_type_set_and_data_as_str() -> None:
    attributes = {
        "id": "123",
        "source": "source",
        "type": "type",
        "specversion": "1.0",
        "time": datetime(2023, 10, 25, 17, 9, 19, 736166, tzinfo=timezone.utc),
        "dataschema": "http://example.com/schema",
        "subject": "test_subject",
    }
    event = CloudEvent(attributes=attributes, data="I'm just a string")
    formatter = JSONFormat()
    result = formatter.write(event)

    assert (
        result
        == '{"id": "123", "source": "source", "type": "type", "specversion": "1.0", "time": "2023-10-25T17:09:19.736166Z", "dataschema": "http://example.com/schema", "subject": "test_subject", "data": "I\'m just a string"}'.encode(
            "utf-8"
        )
    )


def test_write_cloud_event_to_json_with_no_content_type_set_and_data_as_json() -> None:
    attributes = {
        "id": "123",
        "source": "source",
        "type": "type",
        "specversion": "1.0",
        "time": datetime(2023, 10, 25, 17, 9, 19, 736166, tzinfo=timezone.utc),
        "dataschema": "http://example.com/schema",
        "subject": "test_subject",
    }
    event = CloudEvent(attributes=attributes, data={"key": "value"})
    formatter = JSONFormat()
    result = formatter.write(event)

    assert (
        result
        == '{"id": "123", "source": "source", "type": "type", "specversion": "1.0", "time": "2023-10-25T17:09:19.736166Z", "dataschema": "http://example.com/schema", "subject": "test_subject", "data": {"key": "value"}}'.encode(
            "utf-8"
        )
    )


def test_read_cloud_event_from_json_with_attributes_only() -> None:
    data = '{"id": "123", "source": "source", "type": "type", "specversion": "1.0", "time": "2023-10-25T17:09:19.736166Z", "datacontenttype": "application/json", "dataschema": "http://example.com/schema", "subject": "test_subject"}'.encode(
        "utf-8"
    )
    formatter = JSONFormat()
    result = formatter.read(CloudEvent, data)

    assert result.get_id() == "123"
    assert result.get_source() == "source"
    assert result.get_type() == "type"
    assert result.get_specversion() == "1.0"
    assert result.get_time() == datetime(
        2023, 10, 25, 17, 9, 19, 736166, tzinfo=timezone.utc
    )
    assert result.get_datacontenttype() == "application/json"
    assert result.get_dataschema() == "http://example.com/schema"
    assert result.get_subject() == "test_subject"
    assert result.get_data() is None


def test_read_cloud_event_from_json_with_bytes_as_data() -> None:
    data = '{"id": "123", "source": "source", "type": "type", "specversion": "1.0", "time": "2023-10-25T17:09:19.736166Z", "datacontenttype": "application/json", "dataschema": "http://example.com/schema", "subject": "test_subject", "data_base64": "dGVzdA=="}'.encode(
        "utf-8"
    )
    formatter = JSONFormat()
    result = formatter.read(CloudEvent, data)

    assert result.get_id() == "123"
    assert result.get_source() == "source"
    assert result.get_type() == "type"
    assert result.get_specversion() == "1.0"
    assert result.get_time() == datetime(
        2023, 10, 25, 17, 9, 19, 736166, tzinfo=timezone.utc
    )
    assert result.get_datacontenttype() == "application/json"
    assert result.get_dataschema() == "http://example.com/schema"
    assert result.get_subject() == "test_subject"
    assert result.get_data() == b"test"


def test_read_cloud_event_from_json_with_json_as_data() -> None:
    data = '{"id": "123", "source": "source", "type": "type", "specversion": "1.0", "time": "2023-10-25T17:09:19.736166Z", "datacontenttype": "application/json", "dataschema": "http://example.com/schema", "subject": "test_subject", "data": {"key": "value"}}'.encode(
        "utf-8"
    )
    formatter = JSONFormat()
    result = formatter.read(CloudEvent, data)

    assert result.get_id() == "123"
    assert result.get_source() == "source"
    assert result.get_type() == "type"
    assert result.get_specversion() == "1.0"
    assert result.get_time() == datetime(
        2023, 10, 25, 17, 9, 19, 736166, tzinfo=timezone.utc
    )
    assert result.get_datacontenttype() == "application/json"
    assert result.get_dataschema() == "http://example.com/schema"
    assert result.get_subject() == "test_subject"
    assert result.get_data() == {"key": "value"}


def test_write_cloud_event_with_extension_attributes() -> None:
    attributes = {
        "id": "123",
        "source": "source",
        "type": "type",
        "specversion": "1.0",
        "customext1": "value1",
        "customext2": 123,
    }
    event = CloudEvent(attributes=attributes, data=None)
    formatter = JSONFormat()
    result = formatter.write(event)

    assert b'"customext1": "value1"' in result
    assert b'"customext2": 123' in result


def test_read_cloud_event_with_extension_attributes() -> None:
    data = '{"id": "123", "source": "source", "type": "type", "specversion": "1.0", "customext1": "value1", "customext2": 123}'.encode(
        "utf-8"
    )
    formatter = JSONFormat()
    result = formatter.read(CloudEvent, data)

    assert result.get_extension("customext1") == "value1"
    assert result.get_extension("customext2") == 123


def test_write_cloud_event_with_different_json_content_types() -> None:
    test_cases = [
        ("application/vnd.api+json", {"key": "value"}),
        ("text/json", {"key": "value"}),
        ("application/json; charset=utf-8", {"key": "value"}),
    ]

    for content_type, data in test_cases:
        attributes = {
            "id": "123",
            "source": "source",
            "type": "type",
            "specversion": "1.0",
            "datacontenttype": content_type,
        }
        event = CloudEvent(attributes=attributes, data=data)
        formatter = JSONFormat()
        result = formatter.write(event)

        assert b'"data": {"key": "value"}' in result


def test_read_cloud_event_with_string_data() -> None:
    data = '{"id": "123", "source": "source", "type": "type", "specversion": "1.0", "data": "plain string data"}'.encode(
        "utf-8"
    )
    formatter = JSONFormat()
    result = formatter.read(CloudEvent, data)

    assert result.get_data() == "plain string data"


def test_write_cloud_event_with_utc_timezone_z_suffix() -> None:
    attributes = {
        "id": "123",
        "source": "source",
        "type": "type",
        "specversion": "1.0",
        "time": datetime(2023, 10, 25, 17, 9, 19, 736166, tzinfo=timezone.utc),
    }
    event = CloudEvent(attributes=attributes, data=None)
    formatter = JSONFormat()
    result = formatter.write(event)

    assert b'"time": "2023-10-25T17:09:19.736166Z"' in result


def test_write_cloud_event_with_unicode_data() -> None:
    attributes = {
        "id": "123",
        "source": "source",
        "type": "type",
        "specversion": "1.0",
    }
    event = CloudEvent(attributes=attributes, data="Hello 世界 🌍")
    formatter = JSONFormat()
    result = formatter.write(event)

    decoded = result.decode("utf-8")
    assert '"data": "Hello' in decoded
    assert "Hello" in decoded


def test_read_cloud_event_with_unicode_data() -> None:
    data = '{"id": "123", "source": "source", "type": "type", "specversion": "1.0", "data": "Hello 世界 🌍"}'.encode(
        "utf-8"
    )
    formatter = JSONFormat()
    result = formatter.read(CloudEvent, data)

    assert result.get_data() == "Hello 世界 🌍"


def test_read_cloud_event_from_string_input() -> None:
    data = '{"id": "123", "source": "source", "type": "type", "specversion": "1.0"}'
    formatter = JSONFormat()
    result = formatter.read(CloudEvent, data)

    assert result.get_id() == "123"
    assert result.get_source() == "source"


@pytest.mark.parametrize(
    "content_type", [None, "application/json", "application/octet-stream"]
)
def test_write_data_dict(content_type: str) -> None:
    formatter = JSONFormat()
    data = {"key": "value", "nested": {"a": 1}}
    result = formatter.write_data(data, datacontenttype=content_type)

    assert isinstance(result, bytes)
    assert loads(result) == data


@pytest.mark.parametrize("content_type", [None, "application/json"])
def test_read_data_json_body(content_type: str) -> None:
    formatter = JSONFormat()
    body = b'{"key": "value"}'
    result = formatter.read_data(body, content_type)

    assert result == {"key": "value"}


def test_write_batch_with_multiple_events() -> None:
    formatter = JSONFormat()
    event1 = CloudEvent(
        attributes={
            "id": "1",
            "source": "source",
            "type": "type",
            "specversion": "1.0",
        },
        data={"key": "value1"},
    )
    event2 = CloudEvent(
        attributes={
            "id": "2",
            "source": "source",
            "type": "type",
            "specversion": "1.0",
        },
        data={"key": "value2"},
    )

    result = formatter.write_batch([event1, event2])

    parsed = loads(result.decode("utf-8"))
    assert isinstance(parsed, list)
    assert len(parsed) == 2
    assert parsed[0]["id"] == "1"
    assert parsed[0]["data"] == {"key": "value1"}
    assert parsed[1]["id"] == "2"
    assert parsed[1]["data"] == {"key": "value2"}


def test_write_batch_empty_returns_empty_array() -> None:
    formatter = JSONFormat()
    assert formatter.write_batch([]) == b"[]"


def test_read_batch_round_trip() -> None:
    formatter = JSONFormat()
    event1 = CloudEvent(
        attributes={
            "id": "1",
            "source": "source",
            "type": "type",
            "specversion": "1.0",
        },
        data={"key": "value1"},
    )
    event2 = CloudEvent(
        attributes={
            "id": "2",
            "source": "source",
            "type": "type",
            "specversion": "1.0",
        },
        data={"key": "value2"},
    )

    serialized = formatter.write_batch([event1, event2])
    events = formatter.read_batch(CloudEvent, serialized)

    assert len(events) == 2
    assert events[0].get_id() == "1"
    assert events[0].get_data() == {"key": "value1"}
    assert events[1].get_id() == "2"
    assert events[1].get_data() == {"key": "value2"}


def test_read_batch_empty_array_returns_empty_list() -> None:
    formatter = JSONFormat()
    assert formatter.read_batch(CloudEvent, b"[]") == []


def test_read_batch_auto_detects_mixed_versions() -> None:
    from cloudevents.core.v03.event import CloudEvent as CloudEventV03

    formatter = JSONFormat()
    body = (
        b'[{"id": "1", "source": "source", "type": "type", "specversion": "1.0"},'
        b' {"id": "2", "source": "source", "type": "type", "specversion": "0.3"}]'
    )

    events = formatter.read_batch(None, body)

    assert isinstance(events[0], CloudEvent)
    assert isinstance(events[1], CloudEventV03)


def test_read_batch_with_data_base64_element() -> None:
    formatter = JSONFormat()
    event = CloudEvent(
        attributes={
            "id": "1",
            "source": "source",
            "type": "type",
            "specversion": "1.0",
        },
        data=b"binary-data",
    )

    serialized = formatter.write_batch([event])
    events = formatter.read_batch(CloudEvent, serialized)

    assert events[0].get_data() == b"binary-data"


def test_read_batch_non_array_body_raises() -> None:
    formatter = JSONFormat()
    body = b'{"id": "1", "source": "source", "type": "type", "specversion": "1.0"}'

    with pytest.raises(ValueError):
        formatter.read_batch(CloudEvent, body)


def test_read_batch_invalid_element_aborts() -> None:
    formatter = JSONFormat()
    # second element is missing the required 'type' attribute
    body = (
        b'[{"id": "1", "source": "source", "type": "type", "specversion": "1.0"},'
        b' {"id": "2", "source": "source", "specversion": "1.0"}]'
    )

    with pytest.raises(BaseCloudEventException):
        formatter.read_batch(CloudEvent, body)


def test_get_batch_content_type() -> None:
    formatter = JSONFormat()
    assert formatter.get_batch_content_type() == "application/cloudevents-batch+json"
