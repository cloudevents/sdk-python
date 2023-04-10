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
import datetime
from json import loads

import pytest
from pydantic import ValidationError

from cloudevents.conversion import _json_or_string
from cloudevents.exceptions import IncompatibleArgumentsError
from cloudevents.pydantic import CloudEvent
from cloudevents.sdk.event.attribute import SpecVersion

_DUMMY_SOURCE = "dummy:source"
_DUMMY_TYPE = "tests.cloudevents.override"
_DUMMY_TIME = "2022-07-16T11:20:34.284130+00:00"
_DUMMY_ID = "my-id"


@pytest.fixture(params=["0.3", "1.0"])
def specversion(request):
    return request.param


@pytest.fixture()
def dummy_attributes(specversion):
    return {
        "source": _DUMMY_SOURCE,
        "specversion": specversion,
        "id": _DUMMY_ID,
        "time": _DUMMY_TIME,
        "type": _DUMMY_TYPE,
        "datacontenttype": "application/json",
        "subject": "my-subject",
        "dataschema": "myschema:dummy",
    }


@pytest.fixture()
def my_dummy_data():
    return '{"name":"john"}'


@pytest.fixture()
def your_dummy_data():
    return '{"name":"paul"}'


@pytest.fixture()
def dummy_event(dummy_attributes, my_dummy_data):
    return CloudEvent(attributes=dummy_attributes, data=my_dummy_data)


@pytest.fixture()
def non_exiting_attribute_name(dummy_event):
    result = "nonexisting"
    assert result not in dummy_event
    return result


def test_pydantic_cloudevent_equality(dummy_attributes, my_dummy_data, your_dummy_data):
    data = my_dummy_data
    event1 = CloudEvent(dummy_attributes, data)
    event2 = CloudEvent(dummy_attributes, data)
    assert event1 == event2
    # Test different attributes
    for key in dummy_attributes:
        if key in ("specversion", "time", "datacontenttype", "dataschema"):
            continue
        else:
            dummy_attributes[key] = f"noise-{key}"
        event3 = CloudEvent(dummy_attributes, data)
        event2 = CloudEvent(dummy_attributes, data)
        assert event2 == event3
        assert event1 != event2 and event3 != event1

    # Test different data
    data = your_dummy_data
    event3 = CloudEvent(dummy_attributes, data)
    event2 = CloudEvent(dummy_attributes, data)
    assert event2 == event3
    assert event1 != event2 and event3 != event1


@pytest.mark.parametrize(
    "non_cloudevent_value",
    (
        1,
        None,
        object(),
        "Hello World",
    ),
)
def test_http_cloudevent_must_not_equal_to_non_cloudevent_value(
    dummy_event, non_cloudevent_value
):
    assert not dummy_event == non_cloudevent_value


def test_http_cloudevent_mutates_equality(
    dummy_attributes, my_dummy_data, your_dummy_data
):
    data = my_dummy_data
    event1 = CloudEvent(dummy_attributes, data)
    event2 = CloudEvent(dummy_attributes, data)
    event3 = CloudEvent(dummy_attributes, data)

    assert event1 == event2
    # Test different attributes
    for key in dummy_attributes:
        if key in ("specversion", "time", "datacontenttype"):
            continue
        else:
            event2[key] = f"noise-{key}"
            event3[key] = f"noise-{key}"
        assert event2 == event3
        assert event1 != event2 and event3 != event1

    # Test different data
    event2.data = your_dummy_data
    event3.data = your_dummy_data
    assert event2 == event3
    assert event1 != event2 and event3 != event1


def test_cloudevent_missing_specversion():
    attributes = {"specversion": "0.2", "source": "s", "type": "t"}
    with pytest.raises(ValidationError) as e:
        _ = CloudEvent(attributes, None)
    assert "value is not a valid enumeration member; permitted: '0.3', '1.0'" in str(
        e.value
    )


def test_cloudevent_missing_minimal_required_fields():
    attributes = {"type": "t"}
    with pytest.raises(ValidationError) as e:
        _ = CloudEvent(attributes, None)
    assert "\nsource\n  field required " in str(e.value)

    attributes = {"source": "s"}
    with pytest.raises(ValidationError) as e:
        _ = CloudEvent(attributes, None)
    assert "\ntype\n  field required " in str(e.value)


def test_cloudevent_general_overrides():
    event = CloudEvent(
        {
            "source": "my-source",
            "type": "com.test.overrides",
            "subject": "my-subject",
        },
        None,
    )
    expected_attributes = [
        "time",
        "source",
        "id",
        "specversion",
        "type",
        "subject",
        "datacontenttype",
        "dataschema",
    ]

    assert len(event) == len(expected_attributes)
    for attribute in expected_attributes:
        assert attribute in event
        del event[attribute]
    assert len(event) == 0


def test_none_json_or_string():
    assert _json_or_string(None) is None


def test_get_operation_on_non_existing_attribute_must_not_raise_exception(
    dummy_event, non_exiting_attribute_name
):
    dummy_event.get(non_exiting_attribute_name)


def test_get_must_return_attribute_value_if_exists(dummy_event):
    assert dummy_event.get("source") == dummy_event["source"]


def test_get_operation_on_non_existing_attribute_must_return_none_by_default(
    dummy_event, non_exiting_attribute_name
):
    assert dummy_event.get(non_exiting_attribute_name) is None


def test_get_operation_on_non_existing_attribute_must_return_default_value_if_given(
    dummy_event, non_exiting_attribute_name
):
    dummy_value = "Hello World"
    assert dummy_event.get(non_exiting_attribute_name, dummy_value) == dummy_value


def test_get_operation_on_non_existing_attribute_should_not_copy_default_value(
    dummy_event, non_exiting_attribute_name
):
    dummy_value = object()
    assert dummy_event.get(non_exiting_attribute_name, dummy_value) is dummy_value


@pytest.mark.xfail()  # https://github.com/cloudevents/sdk-python/issues/185
def test_json_data_serialization_without_explicit_type():
    assert loads(
        CloudEvent(
            source=_DUMMY_SOURCE, type=_DUMMY_TYPE, data='{"hello": "world"}'
        ).json()
    )["data"] == {"hello": "world"}


@pytest.mark.xfail()  # https://github.com/cloudevents/sdk-python/issues/185
@pytest.mark.parametrize(
    "json_content_type",
    [
        "application/json",
        "application/ld+json",
        "application/x-my-custom-type+json",
        "text/html+json",
    ],
)
def test_json_data_serialization_with_explicit_json_content_type(
    dummy_attributes, json_content_type
):
    dummy_attributes["datacontenttype"] = json_content_type
    assert loads(
        CloudEvent(
            dummy_attributes,
            data='{"hello": "world"}',
        ).json()
    )[
        "data"
    ] == {"hello": "world"}


_NON_JSON_CONTENT_TYPES = [
    pytest.param("video/mp2t", id="MPEG transport stream"),
    pytest.param("text/plain", id="Text, (generally ASCII or ISO 8859-n)"),
    pytest.param("application/vnd.visio", id="Microsoft Visio"),
    pytest.param("audio/wav", id="Waveform Audio Format"),
    pytest.param("audio/webm", id="WEBM audio"),
    pytest.param("video/webm", id="WEBM video"),
    pytest.param("image/webp", id="WEBP image"),
    pytest.param("application/gzip", id="GZip Compressed Archive"),
    pytest.param("image/gif", id="Graphics Interchange Format (GIF)"),
    pytest.param("text/html", id="HyperText Markup Language (HTML)"),
    pytest.param("image/vnd.microsoft.icon", id="Icon format"),
    pytest.param("text/calendar", id="iCalendar format"),
    pytest.param("application/java-archive", id="Java Archive (JAR)"),
    pytest.param("image/jpeg", id="JPEG images"),
]


@pytest.mark.parametrize("datacontenttype", _NON_JSON_CONTENT_TYPES)
def test_json_data_serialization_with_explicit_non_json_content_type(
    dummy_attributes, datacontenttype
):
    dummy_attributes["datacontenttype"] = datacontenttype
    event = CloudEvent(
        dummy_attributes,
        data='{"hello": "world"}',
    ).json()
    assert loads(event)["data"] == '{"hello": "world"}'


@pytest.mark.parametrize("datacontenttype", _NON_JSON_CONTENT_TYPES)
def test_binary_data_serialization(dummy_attributes, datacontenttype):
    dummy_attributes["datacontenttype"] = datacontenttype
    event = CloudEvent(
        dummy_attributes,
        data=b"\x00\x00\x11Hello World",
    ).json()
    result_json = loads(event)
    assert result_json["data_base64"] == "AAARSGVsbG8gV29ybGQ="
    assert "daata" not in result_json


def test_binary_data_deserialization():
    given = (
        b'{"source": "dummy:source", "id": "11775cb2-fd00-4487-a18b-30c3600eaa5f",'
        b' "type": "dummy.type", "specversion": "1.0", "time":'
        b' "2022-07-16T12:03:20.519216+00:00", "subject": null, "datacontenttype":'
        b' "application/octet-stream", "dataschema": null, "data_base64":'
        b' "AAARSGVsbG8gV29ybGQ="}'
    )
    expected = {
        "data": b"\x00\x00\x11Hello World",
        "datacontenttype": "application/octet-stream",
        "dataschema": None,
        "id": "11775cb2-fd00-4487-a18b-30c3600eaa5f",
        "source": "dummy:source",
        "specversion": SpecVersion.v1_0,
        "subject": None,
        "time": datetime.datetime(
            2022, 7, 16, 12, 3, 20, 519216, tzinfo=datetime.timezone.utc
        ),
        "type": "dummy.type",
    }
    assert CloudEvent.parse_raw(given).dict() == expected


def test_access_data_event_attribute_should_raise_key_error(dummy_event):
    with pytest.raises(KeyError):
        dummy_event["data"]


def test_delete_data_event_attribute_should_raise_key_error(dummy_event):
    with pytest.raises(KeyError):
        del dummy_event["data"]


def test_setting_data_attribute_should_not_affect_actual_data(dummy_event):
    my_data = object()
    dummy_event["data"] = my_data
    assert dummy_event.data != my_data


def test_event_length(dummy_event, dummy_attributes):
    assert len(dummy_event) == len(dummy_attributes)


def test_access_data_attribute_with_get_should_return_default(dummy_event):
    default = object()
    assert dummy_event.get("data", default) is default


def test_pydantic_repr_should_contain_attributes_and_data(dummy_event):
    assert "attributes" in repr(dummy_event)
    assert "data" in repr(dummy_event)


def test_data_must_never_exist_as_an_attribute_name(dummy_event):
    assert "data" not in dummy_event


def test_attributes_and_kwards_are_incompatible():
    with pytest.raises(IncompatibleArgumentsError):
        CloudEvent({"a": "b"}, other="hello world")
