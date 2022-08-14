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

import base64
import datetime
import json

import pytest

from cloudevents.conversion import to_json
from cloudevents.pydantic import CloudEvent, from_dict, from_json
from cloudevents.sdk.event.attribute import SpecVersion

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


def test_from_dict():
    given = {
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
    assert from_dict(given).dict() == given


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_pydantic_json_function_parameters_must_affect_output(specversion):
    event = CloudEvent(test_attributes, test_data)
    v1 = event.json(indent=2, sort_keys=True)
    v2 = event.json(indent=4, sort_keys=True)
    assert v1 != v2
