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

from cloudevents.core.exceptions import (
    CloudEventValidationError,
    CustomExtensionAttributeError,
    InvalidAttributeTypeError,
    InvalidAttributeValueError,
    MissingRequiredAttributeError,
)
from cloudevents.core.v03.event import CloudEvent


def test_missing_required_attributes() -> None:
    with pytest.raises(CloudEventValidationError) as e:
        CloudEvent({})

    expected_errors = {
        "source": [
            str(MissingRequiredAttributeError("source")),
            str(
                InvalidAttributeValueError(
                    attribute_name="source",
                    msg="Attribute 'source' must not be None or empty",
                )
            ),
            str(InvalidAttributeTypeError("source", str)),
        ],
        "type": [
            str(MissingRequiredAttributeError("type")),
            str(
                InvalidAttributeValueError(
                    attribute_name="type",
                    msg="Attribute 'type' must not be None or empty",
                )
            ),
            str(InvalidAttributeTypeError("type", str)),
        ],
    }

    actual_errors = {
        key: [str(e) for e in value] for key, value in e.value.errors.items()
    }
    assert actual_errors == expected_errors


def test_invalid_specversion() -> None:
    """Test that v0.3 CloudEvent rejects non-0.3 specversion"""
    with pytest.raises(CloudEventValidationError) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "1.0",  # Wrong version!
            }
        )

    assert "specversion" in e.value.errors
    assert any("must be '0.3'" in str(err) for err in e.value.errors["specversion"])


@pytest.mark.parametrize(
    "time,expected_error",
    [
        (
            "2023-10-25T17:09:19.736166Z",
            {"time": [str(InvalidAttributeTypeError("time", datetime))]},
        ),
        (
            datetime(2023, 10, 25, 17, 9, 19, 736166),
            {
                "time": [
                    str(
                        InvalidAttributeValueError(
                            "time", "Attribute 'time' must be timezone aware"
                        )
                    )
                ]
            },
        ),
        (
            1,
            {"time": [str(InvalidAttributeTypeError("time", datetime))]},
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
                "specversion": "0.3",
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
            {"subject": [str(InvalidAttributeTypeError("subject", str))]},
        ),
        (
            "",
            {
                "subject": [
                    str(
                        InvalidAttributeValueError(
                            "subject", "Attribute 'subject' must not be empty"
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
                "specversion": "0.3",
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
                    str(InvalidAttributeTypeError("datacontenttype", str))
                ]
            },
        ),
        (
            "",
            {
                "datacontenttype": [
                    str(
                        InvalidAttributeValueError(
                            "datacontenttype",
                            "Attribute 'datacontenttype' must not be empty",
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
                "specversion": "0.3",
                "datacontenttype": datacontenttype,
            }
        )

    actual_errors = {
        key: [str(e) for e in value] for key, value in e.value.errors.items()
    }
    assert actual_errors == expected_error


@pytest.mark.parametrize(
    "datacontentencoding,expected_error",
    [
        (
            1234,
            {
                "datacontentencoding": [
                    str(InvalidAttributeTypeError("datacontentencoding", str))
                ]
            },
        ),
        (
            "",
            {
                "datacontentencoding": [
                    str(
                        InvalidAttributeValueError(
                            "datacontentencoding",
                            "Attribute 'datacontentencoding' must not be empty",
                        )
                    )
                ]
            },
        ),
    ],
)
def test_datacontentencoding_validation(
    datacontentencoding: Any, expected_error: dict
) -> None:
    """Test v0.3 specific datacontentencoding attribute validation"""
    with pytest.raises(CloudEventValidationError) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "0.3",
                "datacontentencoding": datacontentencoding,
            }
        )

    actual_errors = {
        key: [str(e) for e in value] for key, value in e.value.errors.items()
    }
    assert actual_errors == expected_error


@pytest.mark.parametrize(
    "schemaurl,expected_error",
    [
        (
            1234,
            {"schemaurl": [str(InvalidAttributeTypeError("schemaurl", str))]},
        ),
        (
            "",
            {
                "schemaurl": [
                    str(
                        InvalidAttributeValueError(
                            "schemaurl", "Attribute 'schemaurl' must not be empty"
                        )
                    )
                ]
            },
        ),
    ],
)
def test_schemaurl_validation(schemaurl: Any, expected_error: dict) -> None:
    """Test v0.3 specific schemaurl attribute validation"""
    with pytest.raises(CloudEventValidationError) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "0.3",
                "schemaurl": schemaurl,
            }
        )

    actual_errors = {
        key: [str(e) for e in value] for key, value in e.value.errors.items()
    }
    assert actual_errors == expected_error


@pytest.mark.parametrize(
    "attributes,expected_errors",
    [
        (
            {"id": "", "source": "/", "type": "test"},
            {
                "id": [
                    str(
                        InvalidAttributeValueError(
                            attribute_name="id",
                            msg="Attribute 'id' must not be None or empty",
                        )
                    )
                ]
            },
        ),
        (
            {"id": None, "source": "/", "type": "test"},
            {
                "id": [
                    str(
                        InvalidAttributeValueError(
                            attribute_name="id",
                            msg="Attribute 'id' must not be None or empty",
                        )
                    ),
                    str(
                        InvalidAttributeTypeError(
                            attribute_name="id", expected_type=str
                        )
                    ),
                ]
            },
        ),
        (
            {"id": "1", "source": "", "type": "test"},
            {
                "source": [
                    str(
                        InvalidAttributeValueError(
                            attribute_name="source",
                            msg="Attribute 'source' must not be None or empty",
                        )
                    )
                ]
            },
        ),
        (
            {"id": "1", "source": None, "type": "test"},
            {
                "source": [
                    str(
                        InvalidAttributeValueError(
                            attribute_name="source",
                            msg="Attribute 'source' must not be None or empty",
                        )
                    ),
                    str(
                        InvalidAttributeTypeError(
                            attribute_name="source", expected_type=str
                        )
                    ),
                ]
            },
        ),
        (
            {"id": "1", "source": "/", "type": ""},
            {
                "type": [
                    str(
                        InvalidAttributeValueError(
                            attribute_name="type",
                            msg="Attribute 'type' must not be None or empty",
                        )
                    )
                ]
            },
        ),
        (
            {"id": "1", "source": "/", "type": None},
            {
                "type": [
                    str(
                        InvalidAttributeValueError(
                            attribute_name="type",
                            msg="Attribute 'type' must not be None or empty",
                        )
                    ),
                    str(
                        InvalidAttributeTypeError(
                            attribute_name="type", expected_type=str
                        )
                    ),
                ]
            },
        ),
    ],
)
def test_required_attributes_null_or_empty(
    attributes: dict[str, Any], expected_errors: dict
) -> None:
    with pytest.raises(CloudEventValidationError) as e:
        CloudEvent(attributes=attributes)

    actual_errors = {
        key: [str(e) for e in value] for key, value in e.value.errors.items()
    }
    for key, expected_msgs in expected_errors.items():
        assert key in actual_errors
        assert actual_errors[key] == expected_msgs


@pytest.mark.parametrize(
    "extension_name,expected_error",
    [
        (
            "",
            {
                "": [
                    str(
                        CustomExtensionAttributeError(
                            "",
                            "Extension attribute name must be at least 1 character long but was ''",
                        )
                    ),
                    str(
                        CustomExtensionAttributeError(
                            "",
                            "Extension attribute '' should only contain lowercase letters and numbers",
                        )
                    ),
                ]
            },
        ),
        (
            "data",
            {
                "data": [
                    str(
                        CustomExtensionAttributeError(
                            "data",
                            "Extension attribute 'data' is reserved and must not be used",
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
                "specversion": "0.3",
                extension_name: "value",
            }
        )

    actual_errors = {
        key: [str(e) for e in value] for key, value in e.value.errors.items()
    }
    assert actual_errors == expected_error


def test_long_extension_attribute_name() -> None:
    # Verify that extension attribute names longer than 20 characters are allowed
    long_name = "a" * 21
    event = CloudEvent(
        {
            "id": "1",
            "source": "/",
            "type": "test",
            "specversion": "0.3",
            long_name: "value",
        }
    )
    assert event.get_extension(long_name) == "value"


def test_default_specversion() -> None:
    event = CloudEvent(
        attributes={"source": "/source", "type": "test", "id": "1"},
    )
    assert event.get_specversion() == "0.3"


def test_default_id() -> None:
    event = CloudEvent(
        attributes={"source": "/source", "type": "test", "specversion": "0.3"},
    )
    assert isinstance(event.get_id(), str)
    assert len(event.get_id()) == 36  # UUID4 format


def test_default_id_is_unique() -> None:
    event1 = CloudEvent(attributes={"source": "/s", "type": "t"})
    event2 = CloudEvent(attributes={"source": "/s", "type": "t"})
    assert event1.get_id() != event2.get_id()


def test_default_time() -> None:
    before = datetime.now(tz=timezone.utc)
    event = CloudEvent(
        attributes={"source": "/source", "type": "test", "specversion": "0.3"},
    )
    after = datetime.now(tz=timezone.utc)
    assert event.get_time() is not None
    assert before <= event.get_time() <= after
    assert event.get_time().tzinfo is not None


def test_explicit_values_override_defaults() -> None:
    custom_time = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    event = CloudEvent(
        attributes={
            "source": "/source",
            "type": "test",
            "specversion": "0.3",
            "id": "my-custom-id",
            "time": custom_time,
        },
    )
    assert event.get_id() == "my-custom-id"
    assert event.get_time() == custom_time
    assert event.get_specversion() == "0.3"


def test_minimal_event_with_defaults() -> None:
    event = CloudEvent(
        attributes={"source": "/source", "type": "test"},
    )
    assert event.get_source() == "/source"
    assert event.get_type() == "test"
    assert event.get_specversion() == "0.3"
    assert event.get_id() is not None
    assert event.get_time() is not None


def test_cloud_event_v03_constructor() -> None:
    """Test creating a v0.3 CloudEvent with all attributes"""
    id = "1"
    source = "/source"
    type = "com.test.type"
    specversion = "0.3"
    datacontenttype = "application/json"
    datacontentencoding = "base64"
    schemaurl = "http://example.com/schema.json"
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
            "datacontentencoding": datacontentencoding,
            "schemaurl": schemaurl,
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
    assert event.get_datacontentencoding() == datacontentencoding
    assert event.get_schemaurl() == schemaurl
    assert event.get_subject() == subject
    assert event.get_time() == time
    assert event.get_extension("customextension") == customextension
    assert event.get_data() == data


def test_get_dataschema_returns_schemaurl() -> None:
    """Test that get_dataschema() returns schemaurl for v0.3 compatibility"""
    event = CloudEvent(
        attributes={
            "id": "1",
            "source": "/source",
            "type": "com.test.type",
            "specversion": "0.3",
            "schemaurl": "http://example.com/schema.json",
        }
    )

    # get_dataschema should return the schemaurl value for compatibility
    assert event.get_dataschema() == "http://example.com/schema.json"
    assert event.get_schemaurl() == "http://example.com/schema.json"


def test_v03_minimal_event() -> None:
    """Test creating a minimal v0.3 CloudEvent"""
    event = CloudEvent(
        attributes={
            "id": "test-123",
            "source": "https://example.com/source",
            "type": "com.example.test",
            "specversion": "0.3",
        }
    )

    assert event.get_id() == "test-123"
    assert event.get_source() == "https://example.com/source"
    assert event.get_type() == "com.example.test"
    assert event.get_specversion() == "0.3"
    assert event.get_data() is None
    assert event.get_datacontentencoding() is None
    assert event.get_schemaurl() is None
