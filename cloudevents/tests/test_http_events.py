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

import bz2
import copy
import io
import json

import pytest
from sanic import Sanic, response

from cloudevents.http import (
    CloudEvent,
    from_http,
    to_binary_http,
    to_structured_http,
)
from cloudevents.sdk import converters

invalid_test_headers = [
    {
        "ce-source": "<event-source>",
        "ce-type": "cloudevent.event.type",
        "ce-specversion": "1.0",
    },
    {
        "ce-id": "my-id",
        "ce-type": "cloudevent.event.type",
        "ce-specversion": "1.0",
    },
    {"ce-id": "my-id", "ce-source": "<event-source>", "ce-specversion": "1.0"},
    {
        "ce-id": "my-id",
        "ce-source": "<event-source>",
        "ce-type": "cloudevent.event.type",
    },
]

invalid_cloudevent_request_bodie = [
    {
        "source": "<event-source>",
        "type": "cloudevent.event.type",
        "specversion": "1.0",
    },
    {"id": "my-id", "type": "cloudevent.event.type", "specversion": "1.0"},
    {"id": "my-id", "source": "<event-source>", "specversion": "1.0"},
    {
        "id": "my-id",
        "source": "<event-source>",
        "type": "cloudevent.event.type",
    },
]

test_data = {"payload-content": "Hello World!"}

app = Sanic(__name__)


def post(url, headers, data):
    return app.test_client.post(url, headers=headers, data=data)


@app.route("/event", ["POST"])
async def echo(request):
    decoder = None
    if "binary-payload" in request.headers:
        decoder = lambda x: x
    event = from_http(
        request.body, headers=dict(request.headers), data_unmarshaller=decoder
    )
    data = (
        event.data
        if isinstance(event.data, (bytes, bytearray, memoryview))
        else json.dumps(event.data).encode()
    )
    return response.raw(data, headers={k: event[k] for k in event})


@pytest.mark.parametrize("body", invalid_cloudevent_request_bodie)
def test_missing_required_fields_structured(body):
    with pytest.raises((TypeError, NotImplementedError)):
        # CloudEvent constructor throws TypeError if missing required field
        # and NotImplementedError because structured calls aren't
        # implemented. In this instance one of the required keys should have
        # prefix e-id instead of ce-id therefore it should throw
        _ = from_http(
            json.dumps(body), attributes={"Content-Type": "application/json"}
        )


@pytest.mark.parametrize("headers", invalid_test_headers)
def test_missing_required_fields_binary(headers):
    with pytest.raises((ValueError)):
        # CloudEvent constructor throws TypeError if missing required field
        # and NotImplementedError because structured calls aren't
        # implemented. In this instance one of the required keys should have
        # prefix e-id instead of ce-id therefore it should throw
        _ = from_http(json.dumps(test_data), headers=headers)


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_emit_binary_event(specversion):
    headers = {
        "ce-id": "my-id",
        "ce-source": "<event-source>",
        "ce-type": "cloudevent.event.type",
        "ce-specversion": specversion,
        "Content-Type": "text/plain",
    }
    data = json.dumps(test_data)
    _, r = app.test_client.post("/event", headers=headers, data=data)

    # Convert byte array to dict
    # e.g. r.body = b'{"payload-content": "Hello World!"}'
    body = json.loads(r.body.decode("utf-8"))

    # Check response fields
    for key in test_data:
        assert body[key] == test_data[key], body
    for key in headers:
        if key != "Content-Type":
            attribute_key = key[3:]
            assert r.headers[attribute_key] == headers[key]
    assert r.status_code == 200


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_emit_structured_event(specversion):
    headers = {"Content-Type": "application/cloudevents+json"}
    body = {
        "id": "my-id",
        "source": "<event-source>",
        "type": "cloudevent.event.type",
        "specversion": specversion,
        "data": test_data,
    }
    _, r = app.test_client.post(
        "/event", headers=headers, data=json.dumps(body)
    )

    # Convert byte array to dict
    # e.g. r.body = b'{"payload-content": "Hello World!"}'
    body = json.loads(r.body.decode("utf-8"))

    # Check response fields
    for key in test_data:
        assert body[key] == test_data[key]
    assert r.status_code == 200


@pytest.mark.parametrize(
    "converter", [converters.TypeBinary, converters.TypeStructured]
)
@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_roundtrip_non_json_event(converter, specversion):
    input_data = io.BytesIO()
    for i in range(100):
        for j in range(20):
            assert 1 == input_data.write(j.to_bytes(1, byteorder="big"))
    compressed_data = bz2.compress(input_data.getvalue())
    attrs = {"source": "test", "type": "t"}

    event = CloudEvent(attrs, compressed_data)

    if converter == converters.TypeStructured:
        headers, data = to_structured_http(event, data_marshaller=lambda x: x)
    elif converter == converters.TypeBinary:
        headers, data = to_binary_http(event, data_marshaller=lambda x: x)

    headers["binary-payload"] = "true"  # Decoding hint for server
    _, r = app.test_client.post("/event", headers=headers, data=data)

    assert r.status_code == 200
    for key in attrs:
        assert r.headers[key] == attrs[key]
    assert compressed_data == r.body, r.body


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_missing_ce_prefix_binary_event(specversion):
    prefixed_headers = {}
    headers = {
        "ce-id": "my-id",
        "ce-source": "<event-source>",
        "ce-type": "cloudevent.event.type",
        "ce-specversion": specversion,
    }
    for key in headers:

        # breaking prefix e.g. e-id instead of ce-id
        prefixed_headers[key[1:]] = headers[key]

        with pytest.raises(ValueError):
            # CloudEvent constructor throws TypeError if missing required field
            # and NotImplementedError because structured calls aren't
            # implemented. In this instance one of the required keys should have
            # prefix e-id instead of ce-id therefore it should throw
            _ = from_http(json.dumps(test_data), headers=prefixed_headers)


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_valid_binary_events(specversion):
    # Test creating multiple cloud events
    events_queue = []
    headers = {}
    num_cloudevents = 30
    for i in range(num_cloudevents):
        headers = {
            "ce-id": f"id{i}",
            "ce-source": f"source{i}.com.test",
            "ce-type": f"cloudevent.test.type",
            "ce-specversion": specversion,
        }
        data = {"payload": f"payload-{i}"}
        events_queue.append(from_http(json.dumps(data), headers=headers))

    for i, event in enumerate(events_queue):
        data = event.data
        assert event["id"] == f"id{i}"
        assert event["source"] == f"source{i}.com.test"
        assert event["specversion"] == specversion
        assert event.data["payload"] == f"payload-{i}"


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_structured_to_request(specversion):
    attributes = {
        "specversion": specversion,
        "type": "word.found.name",
        "id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "source": "pytest",
    }
    data = {"message": "Hello World!"}

    event = CloudEvent(attributes, data)
    headers, body_bytes = to_structured_http(event)
    assert isinstance(body_bytes, bytes)
    body = json.loads(body_bytes)

    assert headers["content-type"] == "application/cloudevents+json"
    for key in attributes:
        assert body[key] == attributes[key]
    assert body["data"] == data, f"|{body_bytes}|| {body}"


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_binary_to_request(specversion):
    attributes = {
        "specversion": specversion,
        "type": "word.found.name",
        "id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "source": "pytest",
    }
    data = {"message": "Hello World!"}
    event = CloudEvent(attributes, data)
    headers, body_bytes = to_binary_http(event)
    body = json.loads(body_bytes)

    for key in data:
        assert body[key] == data[key]
    for key in attributes:
        assert attributes[key] == headers["ce-" + key]


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_empty_data_structured_event(specversion):
    # Testing if cloudevent breaks when no structured data field present
    attributes = {
        "specversion": specversion,
        "datacontenttype": "application/json",
        "type": "word.found.name",
        "id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "time": "2018-10-23T12:28:22.4579346Z",
        "source": "<source-url>",
    }

    _ = from_http(
        json.dumps(attributes), {"content-type": "application/cloudevents+json"}
    )


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_empty_data_binary_event(specversion):
    # Testing if cloudevent breaks when no structured data field present
    headers = {
        "Content-Type": "application/octet-stream",
        "ce-specversion": specversion,
        "ce-type": "word.found.name",
        "ce-id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "ce-time": "2018-10-23T12:28:22.4579346Z",
        "ce-source": "<source-url>",
    }
    _ = from_http("", headers)


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_valid_structured_events(specversion):
    # Test creating multiple cloud events
    events_queue = []
    headers = {}
    num_cloudevents = 30
    for i in range(num_cloudevents):
        event = {
            "id": f"id{i}",
            "source": f"source{i}.com.test",
            "type": f"cloudevent.test.type",
            "specversion": specversion,
            "data": {"payload": f"payload-{i}"},
        }
        events_queue.append(
            from_http(
                json.dumps(event),
                {"content-type": "application/cloudevents+json"},
            )
        )

    for i, event in enumerate(events_queue):
        assert event["id"] == f"id{i}"
        assert event["source"] == f"source{i}.com.test"
        assert event["specversion"] == specversion
        assert event.data["payload"] == f"payload-{i}"


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_structured_no_content_type(specversion):
    # Test creating multiple cloud events
    events_queue = []
    headers = {}
    num_cloudevents = 30
    data = {
        "id": "id",
        "source": "source.com.test",
        "type": "cloudevent.test.type",
        "specversion": specversion,
        "data": test_data,
    }
    event = from_http(json.dumps(data), {},)

    assert event["id"] == "id"
    assert event["source"] == "source.com.test"
    assert event["specversion"] == specversion
    for key, val in test_data.items():
        assert event.data[key] == val


def test_is_binary():
    headers = {
        "ce-id": "my-id",
        "ce-source": "<event-source>",
        "ce-type": "cloudevent.event.type",
        "ce-specversion": "1.0",
        "Content-Type": "text/plain",
    }
    assert converters.is_binary(headers)

    headers = {
        "Content-Type": "application/cloudevents+json",
    }
    assert not converters.is_binary(headers)

    headers = {}
    assert not converters.is_binary(headers)


def test_is_structured():
    headers = {
        "Content-Type": "application/cloudevents+json",
    }
    assert converters.is_structured(headers)

    headers = {}
    assert converters.is_structured(headers)

    headers = {"ce-specversion": "1.0"}
    assert not converters.is_structured(headers)


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_cloudevent_repr(specversion):
    headers = {
        "Content-Type": "application/octet-stream",
        "ce-specversion": specversion,
        "ce-type": "word.found.name",
        "ce-id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "ce-time": "2018-10-23T12:28:22.4579346Z",
        "ce-source": "<source-url>",
    }
    event = from_http("", headers)
    # Testing to make sure event is printable. I could runevent. __repr__() but
    # we had issues in the past where event.__repr__() could run but
    # print(event) would fail.
    print(event)


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_none_data_cloudevent(specversion):
    event = CloudEvent(
        {
            "source": "<my-url>",
            "type": "issue.example",
            "specversion": specversion,
        }
    )
    to_binary_http(event)
    to_structured_http(event)
