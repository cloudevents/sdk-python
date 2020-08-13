from cloudevents.http import CloudEvent

import pytest


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_http_cloudevent_equality(specversion):
    attributes = {
        "source": "<source>",
        "specversion": specversion,
        "id": "my-id",
        "time": "tomorrow",
        "type": "tests.cloudevents.override",
        "datacontenttype": "application/json",
        "subject": "my-subject"
    }
    data = '{"name":"john"}'
    event1 = CloudEvent(attributes, data)
    event2 = CloudEvent(attributes, data)
    assert event1 == event2
    # Test different attributes
    for key in attributes:
        if key == 'specversion':
            continue
        else:
            attributes[key] = f'noise-{key}'
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
        "subject": "my-subject"
    }
    data = '{"name":"john"}'
    event1 = CloudEvent(attributes, data)
    event2 = CloudEvent(attributes, data)
    event3 = CloudEvent(attributes, data)

    assert event1 == event2
    # Test different attributes
    for key in attributes:
        if key == 'specversion':
            continue
        else:
            event2[key] = f'noise-{key}'
            event3[key] = f'noise-{key}'
        assert event2 == event3
        assert event1 != event2 and event3 != event1

    # Test different data
    event2.data = '{"name":"paul"}'
    event3.data = '{"name":"paul"}'
    assert event2 == event3
    assert event1 != event2 and event3 != event1
