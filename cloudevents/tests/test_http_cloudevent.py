import pytest

import cloudevents.exceptions as cloud_exceptions
from cloudevents.http import CloudEvent


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_http_cloudevent_equality(specversion):
    attributes = {
        "source": "<source>",
        "specversion": specversion,
        "id": "my-id",
        "time": "tomorrow",
        "type": "tests.cloudevents.override",
        "datacontenttype": "application/json",
        "subject": "my-subject",
    }
    data = '{"name":"john"}'
    event1 = CloudEvent(attributes, data)
    event2 = CloudEvent(attributes, data)
    assert event1 == event2
    # Test different attributes
    for key in attributes:
        if key == "specversion":
            continue
        else:
            attributes[key] = f"noise-{key}"
        event3 = CloudEvent(attributes, data)
        event2 = CloudEvent(attributes, data)
        assert event2 == event3
        assert event1 != event2 and event3 != event1

    # Test different data
    data = '{"name":"paul"}'
    event3 = CloudEvent(attributes, data)
    event2 = CloudEvent(attributes, data)
    assert event2 == event3
    assert event1 != event2 and event3 != event1


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_http_cloudevent_mutates_equality(specversion):
    attributes = {
        "source": "<source>",
        "specversion": specversion,
        "id": "my-id",
        "time": "tomorrow",
        "type": "tests.cloudevents.override",
        "datacontenttype": "application/json",
        "subject": "my-subject",
    }
    data = '{"name":"john"}'
    event1 = CloudEvent(attributes, data)
    event2 = CloudEvent(attributes, data)
    event3 = CloudEvent(attributes, data)

    assert event1 == event2
    # Test different attributes
    for key in attributes:
        if key == "specversion":
            continue
        else:
            event2[key] = f"noise-{key}"
            event3[key] = f"noise-{key}"
        assert event2 == event3
        assert event1 != event2 and event3 != event1

    # Test different data
    event2.data = '{"name":"paul"}'
    event3.data = '{"name":"paul"}'
    assert event2 == event3
    assert event1 != event2 and event3 != event1


def test_cloudevent_missing_specversion():
    attributes = {"specversion": "0.2", "source": "s", "type": "t"}
    with pytest.raises(cloud_exceptions.MissingRequiredFields) as e:
        event = CloudEvent(attributes, None)
    assert "Invalid specversion: 0.2" in str(e.value)


def test_cloudevent_missing_minimal_required_fields():
    attributes = {"type": "t"}
    with pytest.raises(cloud_exceptions.MissingRequiredFields) as e:
        event = CloudEvent(attributes, None)
    assert f"Missing required keys: {set(['source'])}" in str(e.value)

    attributes = {"source": "s"}
    with pytest.raises(cloud_exceptions.MissingRequiredFields) as e:
        event = CloudEvent(attributes, None)
    assert f"Missing required keys: {set(['type'])}" in str(e.value)


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
    ]

    assert len(event) == 6
    for attribute in expected_attributes:
        assert attribute in event
        del event[attribute]
    assert len(event) == 0
