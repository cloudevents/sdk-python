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

import copy

from cloudevents.sdk.http_events import CloudEvent

from sanic import response
from sanic import Sanic

import pytest


invalid_test_headers = [
    {
        "ce-source": "<event-source>",
        "ce-type": "cloudevent.event.type",
        "ce-specversion": "1.0"
    }, {
        "ce-id": "my-id",
        "ce-type": "cloudevent.event.type",
        "ce-specversion": "1.0"
    }, {
        "ce-id": "my-id",
        "ce-source": "<event-source>",
        "ce-specversion": "1.0"
    }, {
        "ce-id": "my-id",
        "ce-source": "<event-source>",
        "ce-type": "cloudevent.event.type",
    }
]

test_data = {
    "payload-content": "Hello World!"
}

app = Sanic(__name__)


def post(url, headers, json):
    return app.test_client.post(url, headers=headers, data=json)


@app.route("/event", ["POST"])
async def echo(request):
    assert isinstance(request.json, dict)
    event = CloudEvent(dict(request.headers), request.json)
    return response.text(json.dumps(event.data), headers=event.headers)


@pytest.mark.parametrize("headers", invalid_test_headers)
def test_invalid_binary_headers(headers):
    with pytest.raises((TypeError, NotImplementedError)):
        # CloudEvent constructor throws TypeError if missing required field
        # and NotImplementedError because structured calls aren't
        # implemented. In this instance one of the required keys should have
        # prefix e-id instead of ce-id therefore it should throw
        _ = CloudEvent(headers, test_data)


@pytest.mark.parametrize("specversion", ['1.0', '0.3'])
def test_emit_binary_event(specversion):
    headers = {
        "ce-id": "my-id",
        "ce-source": "<event-source>",
        "ce-type": "cloudevent.event.type",
        "ce-specversion": specversion,
        "Content-Type": "application/json"
    }
    event = CloudEvent(headers, test_data)
    _, r = app.test_client.post(
        "/event",
        headers=event.headers,
        data=json.dumps(event.data)
    )
    
    # Convert byte array to dict
    # e.g. r.body = b'{"payload-content": "Hello World!"}'
    body = json.loads(r.body.decode('utf-8'))

    # Check response fields
    for key in test_data:
        assert body[key] == test_data[key]
    for key in headers:
        assert r.headers[key] == headers[key]
    assert r.status_code == 200


@pytest.mark.parametrize("specversion", ['1.0', '0.3'])
def test_missing_ce_prefix_binary_event(specversion):
    headers = {
        "ce-id": "my-id",
        "ce-source": "<event-source>",
        "ce-type": "cloudevent.event.type",
        "ce-specversion": specversion
    }
    for key in headers:
        val = headers.pop(key)

        # breaking prefix e.g. e-id instead of ce-id
        headers[key[1:]] = val
        with pytest.raises((TypeError, NotImplementedError)):
            # CloudEvent constructor throws TypeError if missing required field
            # and NotImplementedError because structured calls aren't
            # implemented. In this instance one of the required keys should have
            # prefix e-id instead of ce-id therefore it should throw
            _ = CloudEvent(headers, test_data)


@pytest.mark.parametrize("specversion", ['1.0', '0.3'])
def test_valid_cloud_events(specversion):
    # Test creating multiple cloud events
    events_queue = []
    headers = {}
    num_cloudevents = 30
    for i in range(num_cloudevents):
        headers = {
            "ce-id": f"id{i}",
            "ce-source": f"source{i}.com.test",
            "ce-type": f"cloudevent.test.type",
            "ce-specversion": specversion
        }
        data = {'payload': f"payload-{i}"}
        events_queue.append(CloudEvent(headers, data))

    for i, event in enumerate(events_queue):
        headers = event.headers
        data = event.data

        assert headers['ce-id'] == f"id{i}"
        assert headers['ce-source'] == f"source{i}.com.test"
        assert headers['ce-specversion'] == specversion
        assert data['payload'] == f"payload-{i}"
