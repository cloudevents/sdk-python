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
