from cloudevents.core.v1.event import CloudEvent

import pytest
from datetime import datetime
from typing import Any, Optional


@pytest.mark.parametrize(
    "attributes, missing_attribute",
    [
        ({"source": "/", "type": "test", "specversion": "1.0"}, "id"),
        ({"id": "1", "type": "test", "specversion": "1.0"}, "source"),
        ({"id": "1", "source": "/", "specversion": "1.0"}, "type"),
        ({"id": "1", "source": "/", "type": "test"}, "specversion"),
    ],
)
def test_missing_required_attribute(attributes: dict, missing_attribute: str) -> None:
    with pytest.raises(ValueError) as e:
        CloudEvent(attributes)

    assert str(e.value) == f"Missing required attribute(s): {missing_attribute}"


@pytest.mark.parametrize(
    "id,error",
    [
        (None, "Attribute 'id' must not be None"),
        (12, "Attribute 'id' must be a string"),
    ],
)
def test_id_validation(id: Optional[Any], error: str) -> None:
    with pytest.raises((ValueError, TypeError)) as e:
        CloudEvent({"id": id, "source": "/", "type": "test", "specversion": "1.0"})

    assert str(e.value) == error


@pytest.mark.parametrize("source,error", [(123, "Attribute 'source' must be a string")])
def test_source_validation(source: Any, error: str) -> None:
    with pytest.raises((ValueError, TypeError)) as e:
        CloudEvent({"id": "1", "source": source, "type": "test", "specversion": "1.0"})

    assert str(e.value) == error


@pytest.mark.parametrize(
    "specversion,error",
    [
        (1.0, "Attribute 'specversion' must be a string"),
        ("1.4", "Attribute 'specversion' must be '1.0'"),
    ],
)
def test_specversion_validation(specversion: Any, error: str) -> None:
    with pytest.raises((ValueError, TypeError)) as e:
        CloudEvent(
            {"id": "1", "source": "/", "type": "test", "specversion": specversion}
        )

    assert str(e.value) == error


@pytest.mark.parametrize(
    "time,error",
    [
        ("2023-10-25T17:09:19.736166Z", "Attribute 'time' must be a datetime object"),
        (
            datetime(2023, 10, 25, 17, 9, 19, 736166),
            "Attribute 'time' must be timezone aware",
        ),
    ],
)
def test_time_validation(time: Any, error: str) -> None:
    with pytest.raises((ValueError, TypeError)) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "1.0",
                "time": time,
            }
        )

    assert str(e.value) == error


@pytest.mark.parametrize(
    "subject,error",
    [
        (1234, "Attribute 'subject' must be a string"),
        (
            "",
            "Attribute 'subject' must not be empty",
        ),
    ],
)
def test_subject_validation(subject: Any, error: str) -> None:
    with pytest.raises((ValueError, TypeError)) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "1.0",
                "subject": subject,
            }
        )

    assert str(e.value) == error


@pytest.mark.parametrize(
    "datacontenttype,error",
    [
        (1234, "Attribute 'datacontenttype' must be a string"),
        (
            "",
            "Attribute 'datacontenttype' must not be empty",
        ),
    ],
)
def test_datacontenttype_validation(datacontenttype: Any, error: str) -> None:
    with pytest.raises((ValueError, TypeError)) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "1.0",
                "datacontenttype": datacontenttype,
            }
        )

    assert str(e.value) == error


@pytest.mark.parametrize(
    "dataschema,error",
    [
        (1234, "Attribute 'dataschema' must be a string"),
        (
            "",
            "Attribute 'dataschema' must not be empty",
        ),
    ],
)
def test_dataschema_validation(dataschema: Any, error: str) -> None:
    with pytest.raises((ValueError, TypeError)) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "1.0",
                "dataschema": dataschema,
            }
        )

    assert str(e.value) == error


@pytest.mark.parametrize(
    "extension_name,error",
    [
        ("123", "Extension attribute '123' should start with a letter"),
        (
            "shrt",
            "Extension attribute 'shrt' should be between 5 and 20 characters long",
        ),
        (
            "thisisaverylongextension",
            "Extension attribute 'thisisaverylongextension' should be between 5 and 20 characters long",
        ),
        (
            "ThisIsNotValid",
            "Extension attribute 'ThisIsNotValid' should only contain lowercase letters and numbers",
        ),
        (
            "data",
            "Extension attribute 'data' is reserved and must not be used",
        ),
    ],
)
def test_custom_extension(extension_name: str, error: str) -> None:
    with pytest.raises(ValueError) as e:
        CloudEvent(
            {
                "id": "1",
                "source": "/",
                "type": "test",
                "specversion": "1.0",
                extension_name: "value",
            }
        )

    assert str(e.value) == error
