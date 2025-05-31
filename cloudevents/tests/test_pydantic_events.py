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
from __future__ import annotations

import bz2
import io
import json
import typing

import cloudevents.exceptions as cloud_exceptions
import pytest
from cloudevents.conversion import to_binary, to_structured
from cloudevents.pydantic.v1.conversion import from_http as pydantic_v1_from_http
from cloudevents.pydantic.v1.event import CloudEvent as PydanticV1CloudEvent
from cloudevents.pydantic.v2.conversion import from_http as pydantic_v2_from_http
from cloudevents.pydantic.v2.event import CloudEvent as PydanticV2CloudEvent
from cloudevents.sdk import converters, types
from cloudevents.sdk.converters.binary import is_binary
from cloudevents.sdk.converters.structured import is_structured
from pydantic import ValidationError as PydanticV2ValidationError
from pydantic.v1 import ValidationError as PydanticV1ValidationError
from sanic import Sanic, response

if typing.TYPE_CHECKING:
    from typing_extensions import TypeAlias

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

invalid_cloudevent_request_body = [
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

app = Sanic("test_pydantic_http_events")


AnyPydanticCloudEvent: TypeAlias = typing.Union[
    PydanticV1CloudEvent, PydanticV2CloudEvent
]


class FromHttpFn(typing.Protocol):
    def __call__(
        self,
        headers: typing.Dict[str, str],
        data: typing.Optional[typing.AnyStr],
        data_unmarshaller: typing.Optional[types.UnmarshallerType] = None,
    ) -> AnyPydanticCloudEvent:
        pass


class PydanticImplementation(typing.TypedDict):
    event: typing.Type[AnyPydanticCloudEvent]
    validation_error: typing.Type[Exception]
    from_http: FromHttpFn
    pydantic_version: typing.Literal["v1", "v2"]


_pydantic_implementation: typing.Mapping[str, PydanticImplementation] = {
    "v1": {
        "event": PydanticV1CloudEvent,
        "validation_error": PydanticV1ValidationError,
        "from_http": pydantic_v1_from_http,
        "pydantic_version": "v1",
    },
    "v2": {
        "event": PydanticV2CloudEvent,
        "validation_error": PydanticV2ValidationError,
        "from_http": pydantic_v2_from_http,
        "pydantic_version": "v2",
    },
}


@pytest.fixture(params=["v1", "v2"])
def cloudevents_implementation(
    request: pytest.FixtureRequest,
) -> PydanticImplementation:
    return _pydantic_implementation[request.param]


@app.route("/event/<pydantic_version>", ["POST"])
async def echo(request, pydantic_version):
    decoder = None
    if "binary-payload" in request.headers:
        decoder = lambda x: x
    event = _pydantic_implementation[pydantic_version]["from_http"](
        dict(request.headers), request.body, data_unmarshaller=decoder
    )
    data = (
        event.data
        if isinstance(event.data, (bytes, bytearray, memoryview))
        else json.dumps(event.data).encode()
    )
    return response.raw(data, headers={k: event[k] for k in event})


@pytest.mark.parametrize("body", invalid_cloudevent_request_body)
def test_missing_required_fields_structured(
    body: dict, cloudevents_implementation: PydanticImplementation
) -> None:
    with pytest.raises(cloud_exceptions.MissingRequiredFields):
        _ = cloudevents_implementation["from_http"](
            {"Content-Type": "application/cloudevents+json"}, json.dumps(body)
        )


@pytest.mark.parametrize("headers", invalid_test_headers)
def test_missing_required_fields_binary(
    headers: dict, cloudevents_implementation: PydanticImplementation
) -> None:
    with pytest.raises(cloud_exceptions.MissingRequiredFields):
        _ = cloudevents_implementation["from_http"](headers, json.dumps(test_data))


@pytest.mark.parametrize("headers", invalid_test_headers)
def test_missing_required_fields_empty_data_binary(
    headers: dict, cloudevents_implementation: PydanticImplementation
) -> None:
    # Test for issue #115
    with pytest.raises(cloud_exceptions.MissingRequiredFields):
        _ = cloudevents_implementation["from_http"](headers, None)


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_emit_binary_event(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
    headers = {
        "ce-id": "my-id",
        "ce-source": "<event-source>",
        "ce-type": "cloudevent.event.type",
        "ce-specversion": specversion,
        "Content-Type": "text/plain",
    }
    data = json.dumps(test_data)
    _, r = app.test_client.post(
        f"/event/{cloudevents_implementation['pydantic_version']}",
        headers=headers,
        data=data,
    )

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
def test_emit_structured_event(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
    headers = {"Content-Type": "application/cloudevents+json"}
    body = {
        "id": "my-id",
        "source": "<event-source>",
        "type": "cloudevent.event.type",
        "specversion": specversion,
        "data": test_data,
    }
    _, r = app.test_client.post(
        f"/event/{cloudevents_implementation['pydantic_version']}",
        headers=headers,
        data=json.dumps(body),
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
def test_roundtrip_non_json_event(
    converter: str,
    specversion: str,
    cloudevents_implementation: PydanticImplementation,
) -> None:
    input_data = io.BytesIO()
    for _ in range(100):
        for j in range(20):
            assert 1 == input_data.write(j.to_bytes(1, byteorder="big"))
    compressed_data = bz2.compress(input_data.getvalue())
    attrs = {"source": "test", "type": "t"}

    event = cloudevents_implementation["event"](attrs, compressed_data)

    if converter == converters.TypeStructured:
        headers, data = to_structured(event, data_marshaller=lambda x: x)
    elif converter == converters.TypeBinary:
        headers, data = to_binary(event, data_marshaller=lambda x: x)

    headers["binary-payload"] = "true"  # Decoding hint for server
    _, r = app.test_client.post(
        f"/event/{cloudevents_implementation['pydantic_version']}",
        headers=headers,
        data=data,
    )

    assert r.status_code == 200
    for key in attrs:
        assert r.headers[key] == attrs[key]
    assert compressed_data == r.body, r.body


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_missing_ce_prefix_binary_event(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
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

        with pytest.raises(cloud_exceptions.MissingRequiredFields):
            # CloudEvent constructor throws TypeError if missing required field
            # and NotImplementedError because structured calls aren't
            # implemented. In this instance one of the required keys should have
            # prefix e-id instead of ce-id therefore it should throw
            _ = cloudevents_implementation["from_http"](
                prefixed_headers, json.dumps(test_data)
            )


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_valid_binary_events(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
    # Test creating multiple cloud events
    events_queue: list[AnyPydanticCloudEvent] = []
    headers = {}
    num_cloudevents = 30
    for i in range(num_cloudevents):
        headers = {
            "ce-id": f"id{i}",
            "ce-source": f"source{i}.com.test",
            "ce-type": "cloudevent.test.type",
            "ce-specversion": specversion,
        }
        data = {"payload": f"payload-{i}"}
        events_queue.append(
            cloudevents_implementation["from_http"](headers, json.dumps(data))
        )

    for i, event in enumerate(events_queue):
        assert isinstance(event.data, dict)
        assert event["id"] == f"id{i}"
        assert event["source"] == f"source{i}.com.test"
        assert event["specversion"] == specversion
        assert event.data["payload"] == f"payload-{i}"


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_structured_to_request(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
    attributes = {
        "specversion": specversion,
        "type": "word.found.name",
        "id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "source": "pytest",
    }
    data = {"message": "Hello World!"}

    event = cloudevents_implementation["event"](attributes, data)
    headers, body_bytes = to_structured(event)
    assert isinstance(body_bytes, bytes)
    body = json.loads(body_bytes)

    assert headers["content-type"] == "application/cloudevents+json"
    for key in attributes:
        assert body[key] == attributes[key]
    assert body["data"] == data, f"|{body_bytes!r}|| {body}"


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_attributes_view_accessor(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
    attributes: dict[str, typing.Any] = {
        "specversion": specversion,
        "type": "word.found.name",
        "id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "source": "pytest",
    }
    data = {"message": "Hello World!"}

    event = cloudevents_implementation["event"](attributes, data)
    event_attributes: typing.Mapping[str, typing.Any] = event.get_attributes()
    assert event_attributes["specversion"] == attributes["specversion"]
    assert event_attributes["type"] == attributes["type"]
    assert event_attributes["id"] == attributes["id"]
    assert event_attributes["source"] == attributes["source"]
    assert event_attributes["time"]


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_binary_to_request(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
    attributes = {
        "specversion": specversion,
        "type": "word.found.name",
        "id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "source": "pytest",
    }
    data = {"message": "Hello World!"}
    event = cloudevents_implementation["event"](attributes, data)
    headers, body_bytes = to_binary(event)
    body = json.loads(body_bytes)

    for key in data:
        assert body[key] == data[key]
    for key in attributes:
        assert attributes[key] == headers["ce-" + key]


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_empty_data_structured_event(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
    # Testing if cloudevent breaks when no structured data field present
    attributes = {
        "specversion": specversion,
        "datacontenttype": "application/cloudevents+json",
        "type": "word.found.name",
        "id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "time": "2018-10-23T12:28:22.4579346Z",
        "source": "<source-url>",
    }

    event = cloudevents_implementation["from_http"](
        {"content-type": "application/cloudevents+json"}, json.dumps(attributes)
    )
    assert event.data is None

    attributes["data"] = ""
    # Data of empty string will be marshalled into None
    event = cloudevents_implementation["from_http"](
        {"content-type": "application/cloudevents+json"}, json.dumps(attributes)
    )
    assert event.data is None


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_empty_data_binary_event(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
    # Testing if cloudevent breaks when no structured data field present
    headers = {
        "Content-Type": "application/octet-stream",
        "ce-specversion": specversion,
        "ce-type": "word.found.name",
        "ce-id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "ce-time": "2018-10-23T12:28:22.4579346Z",
        "ce-source": "<source-url>",
    }
    event = cloudevents_implementation["from_http"](headers, None)
    assert event.data is None

    data = ""
    # Data of empty string will be marshalled into None
    event = cloudevents_implementation["from_http"](headers, data)
    assert event.data is None


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_valid_structured_events(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
    # Test creating multiple cloud events
    events_queue: list[AnyPydanticCloudEvent] = []
    num_cloudevents = 30
    for i in range(num_cloudevents):
        raw_event = {
            "id": f"id{i}",
            "source": f"source{i}.com.test",
            "type": "cloudevent.test.type",
            "specversion": specversion,
            "data": {"payload": f"payload-{i}"},
        }
        events_queue.append(
            cloudevents_implementation["from_http"](
                {"content-type": "application/cloudevents+json"},
                json.dumps(raw_event),
            )
        )

    for i, event in enumerate(events_queue):
        assert isinstance(event.data, dict)
        assert event["id"] == f"id{i}"
        assert event["source"] == f"source{i}.com.test"
        assert event["specversion"] == specversion
        assert event.data["payload"] == f"payload-{i}"


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_structured_no_content_type(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
    # Test creating multiple cloud events
    data = {
        "id": "id",
        "source": "source.com.test",
        "type": "cloudevent.test.type",
        "specversion": specversion,
        "data": test_data,
    }
    event = cloudevents_implementation["from_http"]({}, json.dumps(data))

    assert isinstance(event.data, dict)
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
    assert is_binary(headers)

    headers = {
        "Content-Type": "application/cloudevents+json",
    }
    assert not is_binary(headers)

    headers = {}
    assert not is_binary(headers)


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_cloudevent_repr(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
    headers = {
        "Content-Type": "application/octet-stream",
        "ce-specversion": specversion,
        "ce-type": "word.found.name",
        "ce-id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
        "ce-time": "2018-10-23T12:28:22.4579346Z",
        "ce-source": "<source-url>",
    }
    event = cloudevents_implementation["from_http"](headers, "")
    # Testing to make sure event is printable. I could run event. __repr__() but
    # we had issues in the past where event.__repr__() could run but
    # print(event) would fail.
    print(event)  # noqa T201


@pytest.mark.parametrize("specversion", ["1.0", "0.3"])
def test_none_data_cloudevent(
    specversion: str, cloudevents_implementation: PydanticImplementation
) -> None:
    event = cloudevents_implementation["event"](
        {
            "source": "<my-url>",
            "type": "issue.example",
            "specversion": specversion,
        }
    )
    to_binary(event)
    to_structured(event)


def test_wrong_specversion(cloudevents_implementation: PydanticImplementation) -> None:
    headers = {"Content-Type": "application/cloudevents+json"}
    data = json.dumps(
        {
            "specversion": "0.2",
            "type": "word.found.name",
            "id": "96fb5f0b-001e-0108-6dfe-da6e2806f124",
            "source": "<my-source>",
        }
    )
    with pytest.raises(cloud_exceptions.InvalidRequiredFields) as e:
        cloudevents_implementation["from_http"](headers, data)
    assert "Found invalid specversion 0.2" in str(e.value)


def test_invalid_data_format_structured_from_http(
    cloudevents_implementation: PydanticImplementation,
) -> None:
    headers = {"Content-Type": "application/cloudevents+json"}
    data = 20
    with pytest.raises(cloud_exceptions.InvalidStructuredJSON) as e:
        cloudevents_implementation["from_http"](headers, data)  # type: ignore[type-var] # intentionally wrong type # noqa: E501
    assert "Expected json of type (str, bytes, bytearray)" in str(e.value)


def test_wrong_specversion_to_request(
    cloudevents_implementation: PydanticImplementation,
) -> None:
    event = cloudevents_implementation["event"]({"source": "s", "type": "t"}, None)
    with pytest.raises(cloud_exceptions.InvalidRequiredFields) as e:
        event["specversion"] = "0.2"
        to_binary(event)
    assert "Unsupported specversion: 0.2" in str(e.value)


def test_is_structured():
    headers = {
        "Content-Type": "application/cloudevents+json",
    }
    assert is_structured(headers)

    headers = {
        "ce-id": "my-id",
        "ce-source": "<event-source>",
        "ce-type": "cloudevent.event.type",
        "ce-specversion": "1.0",
        "Content-Type": "text/plain",
    }
    assert not is_structured(headers)


def test_empty_json_structured(
    cloudevents_implementation: PydanticImplementation,
) -> None:
    headers = {"Content-Type": "application/cloudevents+json"}
    data = ""
    with pytest.raises(cloud_exceptions.MissingRequiredFields) as e:
        cloudevents_implementation["from_http"](headers, data)
    assert "Failed to read specversion from both headers and data" in str(e.value)


def test_uppercase_headers_with_none_data_binary(
    cloudevents_implementation: PydanticImplementation,
) -> None:
    headers = {
        "Ce-Id": "my-id",
        "Ce-Source": "<event-source>",
        "Ce-Type": "cloudevent.event.type",
        "Ce-Specversion": "1.0",
    }
    event = cloudevents_implementation["from_http"](headers, None)

    for key in headers:
        assert event[key.lower()[3:]] == headers[key]
    assert event.data is None

    _, new_data = to_binary(event)
    assert new_data is None


def test_generic_exception(cloudevents_implementation: PydanticImplementation) -> None:
    headers = {"Content-Type": "application/cloudevents+json"}
    data = json.dumps(
        {
            "specversion": "1.0",
            "source": "s",
            "type": "t",
            "id": "1234-1234-1234",
            "data": "",
        }
    )
    with pytest.raises(cloud_exceptions.GenericException) as e:
        cloudevents_implementation["from_http"]({}, None)
    e.errisinstance(cloud_exceptions.MissingRequiredFields)

    with pytest.raises(cloud_exceptions.GenericException) as e:
        cloudevents_implementation["from_http"]({}, 123)  # type: ignore[type-var] # intentionally wrong type # noqa: E501
    e.errisinstance(cloud_exceptions.InvalidStructuredJSON)

    with pytest.raises(cloud_exceptions.GenericException) as e:
        cloudevents_implementation["from_http"](
            headers, data, data_unmarshaller=lambda x: 1 / 0
        )
    e.errisinstance(cloud_exceptions.DataUnmarshallerError)

    with pytest.raises(cloud_exceptions.GenericException) as e:
        event = cloudevents_implementation["from_http"](headers, data)
        to_binary(event, data_marshaller=lambda x: 1 / 0)
    e.errisinstance(cloud_exceptions.DataMarshallerError)


def test_non_dict_data_no_headers_bug(
    cloudevents_implementation: PydanticImplementation,
) -> None:
    # Test for issue #116
    headers = {"Content-Type": "application/cloudevents+json"}
    data = "123"
    with pytest.raises(cloud_exceptions.MissingRequiredFields) as e:
        cloudevents_implementation["from_http"](headers, data)
    assert "Failed to read specversion from both headers and data" in str(e.value)
    assert "The following deserialized data has no 'get' method" in str(e.value)
