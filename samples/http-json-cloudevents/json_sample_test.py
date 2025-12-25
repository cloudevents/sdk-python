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

import pytest
from json_sample_server import app

from cloudevents.core.bindings.http import (
    CloudEvent,
    to_binary_event,
    to_structured_event,
)


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_binary_request(client):
    # This data defines a binary cloudevent
    attributes = {
        "id": "123",
        "specversion": "1.0",
        "type": "com.example.sampletype1",
        "source": "https://example.com/event-producer",
    }
    data = {"message": "Hello World!"}

    event = CloudEvent(attributes, data)
    http_message = to_binary_event(event)

    r = client.post("/", headers=http_message.headers, data=http_message.body)
    assert r.status_code == 204


def test_structured_request(client):
    # This data defines a structured cloudevent
    attributes = {
        "id": "123",
        "specversion": "1.0",
        "type": "com.example.sampletype2",
        "source": "https://example.com/event-producer",
    }
    data = {"message": "Hello World!"}

    event = CloudEvent(attributes, data)
    http_message = to_structured_event(event)

    r = client.post("/", headers=http_message.headers, data=http_message.body)
    assert r.status_code == 204
