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

import json

import pytest

import cloudevents.exceptions as cloud_exceptions
from cloudevents.http import CloudEvent, from_http, to_binary, to_structured
from cloudevents.sdk import exceptions, marshaller
from cloudevents.sdk.converters import binary, structured
from cloudevents.sdk.event import v1


@pytest.fixture
def binary_headers():
    return {
        "ce-specversion": "1.0",
        "ce-source": "1.0",
        "ce-type": "com.marshaller.test",
        "ce-id": "1234-1234-1234",
    }


@pytest.fixture
def structured_data():
    return json.dumps(
        {
            "specversion": "1.0",
            "source": "pytest",
            "type": "com.pytest.test",
            "id": "1234-1234-1234",
            "data": "test",
        }
    )


def test_from_request_wrong_unmarshaller():
    with pytest.raises(exceptions.InvalidDataUnmarshaller):
        m = marshaller.NewDefaultHTTPMarshaller()
        _ = m.FromRequest(
            event=v1.Event(), headers={}, body="", data_unmarshaller=object()  # type: ignore[arg-type] # intentionally wrong type # noqa: E501
        )


def test_to_request_wrong_marshaller():
    with pytest.raises(exceptions.InvalidDataMarshaller):
        m = marshaller.NewDefaultHTTPMarshaller()
        _ = m.ToRequest(v1.Event(), data_marshaller="")  # type: ignore[arg-type] # intentionally wrong type # noqa: E501


def test_from_request_cannot_read(binary_headers):
    with pytest.raises(exceptions.UnsupportedEventConverter):
        m = marshaller.HTTPMarshaller([binary.NewBinaryHTTPCloudEventConverter()])
        m.FromRequest(v1.Event(), {}, "")

    with pytest.raises(exceptions.UnsupportedEventConverter):
        m = marshaller.HTTPMarshaller([structured.NewJSONHTTPCloudEventConverter()])
        m.FromRequest(v1.Event(), binary_headers, "")


def test_to_request_invalid_converter():
    with pytest.raises(exceptions.NoSuchConverter):
        m = marshaller.HTTPMarshaller([structured.NewJSONHTTPCloudEventConverter()])
        m.ToRequest(v1.Event(), "")


def test_http_data_unmarshaller_exceptions(binary_headers, structured_data):
    # binary
    with pytest.raises(cloud_exceptions.DataUnmarshallerError) as e:
        from_http(binary_headers, None, data_unmarshaller=lambda x: 1 / 0)
    assert (
        "Failed to unmarshall data with error: "
        "ZeroDivisionError('division by zero')" in str(e.value)
    )

    # structured
    headers = {"Content-Type": "application/cloudevents+json"}
    with pytest.raises(cloud_exceptions.DataUnmarshallerError) as e:
        from_http(headers, structured_data, data_unmarshaller=lambda x: 1 / 0)
    assert (
        "Failed to unmarshall data with error: "
        "ZeroDivisionError('division by zero')" in str(e.value)
    )


def test_http_data_marshaller_exception(binary_headers, structured_data):
    # binary
    event = from_http(binary_headers, None)
    with pytest.raises(cloud_exceptions.DataMarshallerError) as e:
        to_binary(event, data_marshaller=lambda x: 1 / 0)
    assert (
        "Failed to marshall data with error: "
        "ZeroDivisionError('division by zero')" in str(e.value)
    )

    # structured
    headers = {"Content-Type": "application/cloudevents+json"}

    event = from_http(headers, structured_data)
    with pytest.raises(cloud_exceptions.DataMarshallerError) as e:
        to_structured(event, data_marshaller=lambda x: 1 / 0)
    assert (
        "Failed to marshall data with error: "
        "ZeroDivisionError('division by zero')" in str(e.value)
    )


@pytest.mark.parametrize("test_data", [[], {}, (), "", b"", None])
def test_known_empty_edge_cases(binary_headers, test_data):
    expect_data = test_data
    if test_data in ["", b""]:
        expect_data = None
    elif test_data == ():
        # json.dumps(()) outputs '[]' hence list not tuple check
        expect_data = []

    # Remove ce- prefix
    headers = {key[3:]: value for key, value in binary_headers.items()}

    # binary
    event = from_http(*to_binary(CloudEvent(headers, test_data)))
    assert event.data == expect_data

    # structured
    event = from_http(*to_structured(CloudEvent(headers, test_data)))
    assert event.data == expect_data
