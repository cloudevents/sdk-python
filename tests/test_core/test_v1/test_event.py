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

from cloudevents.core.v1.event import CloudEvent
from cloudevents.core.v1.exceptions import CloudEventValidationError


def test_missing_required_attributes() -> None:
    with pytest.raises(CloudEventValidationError) as e:
        CloudEvent({})

    assert e.value.errors == {
        "required": ["Missing required attribute(s): id, source, type, specversion"],
        "type": [
            "Attribute 'id' must not be None",
            "Attribute 'id' must be a string",
            "Attribute 'source' must be a string",
            "Attribute 'type' must be a string",
            "Attribute 'specversion' must be a string",
            "Attribute 'specversion' must be '1.0'",
        ],
    }


@pytest.mark.parametrize(
    "time,error",
    [
        (
            "2023-10-25T17:09:19.736166Z",
            {"optional": ["Attribute 'time' must be a datetime object"]},
        ),
        (
            datetime(2023, 10, 25, 17, 9, 19, 736166),
            {"optional": ["Attribute 'time' must be timezone aware"]},
        ),
        (1, {"optional": ["Attribute 'time' must be a datetime object"]}),
    ],
)
def test_time_validation(time: Any, error: dict) -> None:
    with pytest.raises(CloudEventValidationError) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "1.0",
                "time": time,
            }
        )

    assert e.value.errors == error


@pytest.mark.parametrize(
    "subject,error",
    [
        (1234, {"optional": ["Attribute 'subject' must be a string"]}),
        (
            "",
            {"optional": ["Attribute 'subject' must not be empty"]},
        ),
    ],
)
def test_subject_validation(subject: Any, error: dict) -> None:
    with pytest.raises(CloudEventValidationError) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "1.0",
                "subject": subject,
            }
        )

    assert e.value.errors == error


@pytest.mark.parametrize(
    "datacontenttype,error",
    [
        (1234, {"optional": ["Attribute 'datacontenttype' must be a string"]}),
        (
            "",
            {"optional": ["Attribute 'datacontenttype' must not be empty"]},
        ),
    ],
)
def test_datacontenttype_validation(datacontenttype: Any, error: dict) -> None:
    with pytest.raises(CloudEventValidationError) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "1.0",
                "datacontenttype": datacontenttype,
            }
        )

    assert e.value.errors == error


@pytest.mark.parametrize(
    "dataschema,error",
    [
        (1234, {"optional": ["Attribute 'dataschema' must be a string"]}),
        (
            "",
            {"optional": ["Attribute 'dataschema' must not be empty"]},
        ),
    ],
)
def test_dataschema_validation(dataschema: Any, error: str) -> None:
    with pytest.raises(CloudEventValidationError) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "1.0",
                "dataschema": dataschema,
            }
        )

    assert e.value.errors == error


@pytest.mark.parametrize(
    "extension_name,error",
    [
        (
            "",
            {
                "extensions": [
                    "Extension attribute '' should be between 1 and 20 characters long",
                    "Extension attribute '' should only contain lowercase letters and numbers",
                ]
            },
        ),
        (
            "thisisaverylongextension",
            {
                "extensions": [
                    "Extension attribute 'thisisaverylongextension' should be between 1 and 20 characters long"
                ]
            },
        ),
        (
            "data",
            {
                "extensions": [
                    "Extension attribute 'data' is reserved and must not be used"
                ]
            },
        ),
    ],
)
def test_custom_extension(extension_name: str, error: dict) -> None:
    with pytest.raises(CloudEventValidationError) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "1.0",
                extension_name: "value",
            }
        )

    assert e.value.errors == error


def test_cloud_event_constructor() -> None:
    id = "1"
    source = "/source"
    type = "com.test.type"
    specversion = "1.0"
    datacontenttype = "application/json"
    dataschema = "http://example.com/schema"
    subject = "test_subject"
    time = datetime.now(tz=timezone.utc)
    data = {"key": "value"}
    customextension = "customExtension"

    event = CloudEvent(
        attributes={
            "id": id,
            "source": source,
            "type": type,
            "specversion": specversion,
            "datacontenttype": datacontenttype,
            "dataschema": dataschema,
            "subject": subject,
            "time": time,
            "customextension": customextension,
        },
        data=data,
    )

    assert event.get_id() == id
    assert event.get_source() == source
    assert event.get_type() == type
    assert event.get_specversion() == specversion
    assert event.get_datacontenttype() == datacontenttype
    assert event.get_dataschema() == dataschema
    assert event.get_subject() == subject
    assert event.get_time() == time
    assert event.get_extension("customextension") == customextension
    assert event.get_data() == data
