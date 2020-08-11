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
import json

import pytest

from cloudevents.http import (
    CloudEvent,
    from_http,
    to_binary_http,
    to_structured_http,
)

test_data = json.dumps({"data-key": "val"})
test_attributes = {
    "type": "com.example.string",
    "source": "https://example.com/event-producer",
    "ext1": "testval",
}


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_cloudevent_access_extensions(specversion):
    event = CloudEvent(test_attributes, test_data)
    assert event["ext1"] == "testval"


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_to_binary_extensions(specversion):
    event = CloudEvent(test_attributes, test_data)
    headers, body = to_binary_http(event)

    assert "ce-ext1" in headers
    assert headers.get("ce-ext1") == test_attributes["ext1"]


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_from_binary_extensions(specversion):
    headers = {
        "ce-id": "1234",
        "ce-source": "<my url>",
        "ce-type": "sample",
        "ce-specversion": specversion,
        "ce-ext1": "test1",
        "ce-ext2": "test2",
    }
    body = json.dumps({"data-key": "val"})
    event = from_http(body, headers)

    assert headers["ce-ext1"] == event["ext1"]
    assert headers["ce-ext2"] == event["ext2"]


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_to_structured_extensions(specversion):
    event = CloudEvent(test_attributes, test_data)
    headers, body = to_structured_http(event)

    body = json.loads(body)

    assert "ext1" in body
    assert "extensions" not in body


@pytest.mark.parametrize("specversion", ["0.3", "1.0"])
def test_from_structured_extensions(specversion):
    headers = {"Content-Type": "application/cloudevents+json"}
    body = {
        "id": "1234",
        "source": "<my url>",
        "type": "sample",
        "specversion": specversion,
        "ext1": "test1",
        "ext2": "test2",
    }

    data = json.dumps(body)
    event = from_http(data, headers)

    assert body["ext1"] == event["ext1"]
    assert body["ext2"] == event["ext2"]
