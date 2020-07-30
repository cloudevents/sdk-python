# All Rights Reserved.
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
import json

import pytest

from cloudevents.http import CloudEvent, from_json, to_json

test_data = json.dumps({"data-key": "val"})
test_attributes = {
    "type": "com.example.string",
    "source": "https://example.com/event-producer",
}


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_to_json(specversion):
    event = CloudEvent(test_attributes, test_data)
    event_json = to_json(event)
    event_dict = json.loads(event_json)

    for key, val in test_attributes.items():
        assert event_dict[key] == val

    assert event_dict["data"] == test_data


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_to_json_base64(specversion):
    data = b"test123"

    event = CloudEvent(test_attributes, data)
    event_json = to_json(event)
    event_dict = json.loads(event_json)

    for key, val in test_attributes.items():
        assert event_dict[key] == val

    # test data was properly marshalled into data_base64
    data_base64 = event_dict["data_base64"].encode()
    test_data_base64 = base64.b64encode(data)

    assert data_base64 == test_data_base64


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_from_json(specversion):
    payload = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
        "id": "1234",
        "specversion": specversion,
        "data": {"data-key": "val"},
    }
    event = from_json(json.dumps(payload))

    for key, val in payload.items():
        if key == "data":
            assert event.data == payload["data"]
        else:
            assert event[key] == val


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_from_json_base64(specversion):
    # Create base64 encoded data
    raw_data = {"data-key": "val"}
    data = json.dumps(raw_data).encode()
    data_base64_str = base64.b64encode(data).decode()

    # Create json payload
    payload = {
        "type": "com.example.string",
        "source": "https://example.com/event-producer",
        "id": "1234",
        "specversion": specversion,
        "data_base64": data_base64_str,
    }
    payload_json = json.dumps(payload)

    # Create event
    event = from_json(payload_json)

    # Test fields were marshalled properly
    for key, val in payload.items():
        if key == "data_base64":
            # Check data_base64 was unmarshalled properly
            assert event.data == raw_data
        else:
            assert event[key] == val


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_json_can_talk_to_itself(specversion):
    event = CloudEvent(test_attributes, test_data)
    event_json = to_json(event)

    event = from_json(event_json)

    for key, val in test_attributes.items():
        assert event[key] == val
    assert event.data == test_data


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_json_can_talk_to_itself_base64(specversion):
    data = b"test123"

    event = CloudEvent(test_attributes, data)
    event_json = to_json(event)

    event = from_json(event_json)

    for key, val in test_attributes.items():
        assert event[key] == val
    assert event.data == data
