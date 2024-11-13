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
from cloudevents.core.v1.exceptions import (
    CloudEventValidationError,
    CustomExtensionAttributeError,
    InvalidAttributeTypeError,
    MissingRequiredAttributeError,
)


def test_missing_required_attributes() -> None:
    with pytest.raises(CloudEventValidationError) as e:
        CloudEvent({})

    expected_errors = {
        "id": [
            str(MissingRequiredAttributeError("id")),
            str(InvalidAttributeTypeError("Attribute 'id' must not be None")),
            str(InvalidAttributeTypeError("Attribute 'id' must be a string")),
        ],
        "source": [
            str(MissingRequiredAttributeError("source")),
            str(InvalidAttributeTypeError("Attribute 'source' must be a string")),
        ],
        "type": [
            str(MissingRequiredAttributeError("type")),
            str(InvalidAttributeTypeError("Attribute 'type' must be a string")),
        ],
        "specversion": [
            str(MissingRequiredAttributeError("specversion")),
            str(InvalidAttributeTypeError("Attribute 'specversion' must be a string")),
            str(InvalidAttributeTypeError("Attribute 'specversion' must be '1.0'")),
        ],
    }

    actual_errors = {
        key: [str(e) for e in value] for key, value in e.value.errors.items()
    }
    assert actual_errors == expected_errors


@pytest.mark.parametrize(
    "time,expected_error",
    [
        (
            "2023-10-25T17:09:19.736166Z",
            {
                "time": [
                    str(
                        InvalidAttributeTypeError(
                            "Attribute 'time' must be a datetime object"
                        )
                    )
                ]
            },
        ),
        (
            datetime(2023, 10, 25, 17, 9, 19, 736166),
            {
                "time": [
                    str(
                        InvalidAttributeTypeError(
                            "Attribute 'time' must be timezone aware"
                        )
                    )
                ]
            },
        ),
        (
            1,
            {
                "time": [
                    str(
                        InvalidAttributeTypeError(
                            "Attribute 'time' must be a datetime object"
                        )
                    )
                ]
            },
        ),
    ],
)
def test_time_validation(time: Any, expected_error: dict) -> None:
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
    actual_errors = {
        key: [str(e) for e in value] for key, value in e.value.errors.items()
    }
    assert actual_errors == expected_error


@pytest.mark.parametrize(
    "subject,expected_error",
    [
        (
            1234,
            {
                "subject": [
                    str(
                        InvalidAttributeTypeError(
                            "Attribute 'subject' must be a string"
                        )
                    )
                ]
            },
        ),
        (
            "",
            {
                "subject": [
                    str(
                        InvalidAttributeTypeError(
                            "Attribute 'subject' must not be empty"
                        )
                    )
                ]
            },
        ),
    ],
)
def test_subject_validation(subject: Any, expected_error: dict) -> None:
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

    actual_errors = {
        key: [str(e) for e in value] for key, value in e.value.errors.items()
    }
    assert actual_errors == expected_error


@pytest.mark.parametrize(
    "datacontenttype,expected_error",
    [
        (
            1234,
            {
                "datacontenttype": [
                    str(
                        InvalidAttributeTypeError(
                            "Attribute 'datacontenttype' must be a string"
                        )
                    )
                ]
            },
        ),
        (
            "",
            {
                "datacontenttype": [
                    str(
                        InvalidAttributeTypeError(
                            "Attribute 'datacontenttype' must not be empty"
                        )
                    )
                ]
            },
        ),
    ],
)
def test_datacontenttype_validation(datacontenttype: Any, expected_error: dict) -> None:
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

    actual_errors = {
        key: [str(e) for e in value] for key, value in e.value.errors.items()
    }
    assert actual_errors == expected_error


@pytest.mark.parametrize(
    "dataschema,expected_error",
    [
        (
            1234,
            {
                "dataschema": [
                    str(
                        InvalidAttributeTypeError(
                            "Attribute 'dataschema' must be a string"
                        )
                    )
                ]
            },
        ),
        (
            "",
            {
                "dataschema": [
                    str(
                        InvalidAttributeTypeError(
                            "Attribute 'dataschema' must not be empty"
                        )
                    )
                ]
            },
        ),
    ],
)
def test_dataschema_validation(dataschema: Any, expected_error: dict) -> None:
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

    actual_errors = {
        key: [str(e) for e in value] for key, value in e.value.errors.items()
    }
    assert actual_errors == expected_error


@pytest.mark.parametrize(
    "extension_name,expected_error",
    [
        (
            "",
            {
                "": [
                    str(
                        CustomExtensionAttributeError(
                            "Extension attribute '' should be between 1 and 20 characters long"
                        )
                    ),
                    str(
                        CustomExtensionAttributeError(
                            "Extension attribute '' should only contain lowercase letters and numbers"
                        )
                    ),
                ]
            },
        ),
        (
            "thisisaverylongextension",
            {
                "thisisaverylongextension": [
                    str(
                        CustomExtensionAttributeError(
                            "Extension attribute 'thisisaverylongextension' should be between 1 and 20 characters long"
                        )
                    )
                ]
            },
        ),
        (
            "data",
            {
                "data": [
                    str(
                        CustomExtensionAttributeError(
                            "Extension attribute 'data' is reserved and must not be used"
                        )
                    )
                ]
            },
        ),
    ],
)
def test_custom_extension(extension_name: str, expected_error: dict) -> None:
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

    actual_errors = {
        key: [str(e) for e in value] for key, value in e.value.errors.items()
    }
    assert actual_errors == expected_error


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
