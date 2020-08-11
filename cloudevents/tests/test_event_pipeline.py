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

import io
import json

import pytest

from cloudevents.sdk import converters, marshaller
from cloudevents.sdk.converters import structured
from cloudevents.sdk.event import v1, v03
from cloudevents.tests import data


@pytest.mark.parametrize("event_class", [v03.Event, v1.Event])
def test_event_pipeline_upstream(event_class):
    event = (
        event_class()
        .SetContentType(data.contentType)
        .SetData(data.body)
        .SetEventID(data.ce_id)
        .SetSource(data.source)
        .SetEventTime(data.eventTime)
        .SetEventType(data.ce_type)
    )
    m = marshaller.NewDefaultHTTPMarshaller()
    new_headers, body = m.ToRequest(event, converters.TypeBinary, lambda x: x)

    assert new_headers is not None
    assert "ce-specversion" in new_headers
    assert "ce-type" in new_headers
    assert "ce-source" in new_headers
    assert "ce-id" in new_headers
    assert "ce-time" in new_headers
    assert "content-type" in new_headers
    assert isinstance(body, bytes)
    assert data.body == body.decode("utf-8")


def test_extensions_are_set_upstream():
    extensions = {"extension-key": "extension-value"}
    event = v1.Event().SetExtensions(extensions)

    m = marshaller.NewDefaultHTTPMarshaller()
    new_headers, _ = m.ToRequest(event, converters.TypeBinary, lambda x: x)

    assert event.Extensions() == extensions
    assert "ce-extension-key" in new_headers


def test_binary_event_v1():
    event = (
        v1.Event()
        .SetContentType("application/octet-stream")
        .SetData(b"\x00\x01")
    )
    m = marshaller.NewHTTPMarshaller(
        [structured.NewJSONHTTPCloudEventConverter()]
    )

    _, body = m.ToRequest(event, converters.TypeStructured, lambda x: x)
    assert isinstance(body, bytes)
    content = json.loads(body)
    assert "data" not in content
    assert content["data_base64"] == "AAE=", f"Content is: {content}"


def test_object_event_v1():
    event = (
        v1.Event().SetContentType("application/json").SetData({"name": "john"})
    )

    m = marshaller.NewDefaultHTTPMarshaller()

    _, structuredBody = m.ToRequest(event)
    assert isinstance(structuredBody, bytes)
    structuredObj = json.loads(structuredBody)
    errorMsg = f"Body was {structuredBody}, obj is {structuredObj}"
    assert isinstance(structuredObj, dict), errorMsg
    assert isinstance(structuredObj["data"], dict), errorMsg
    assert len(structuredObj["data"]) == 1, errorMsg
    assert structuredObj["data"]["name"] == "john", errorMsg

    headers, binaryBody = m.ToRequest(event, converters.TypeBinary)
    assert isinstance(headers, dict)
    assert isinstance(binaryBody, bytes)
    assert headers["content-type"] == "application/json"
    assert binaryBody == b'{"name": "john"}', f"Binary is {binaryBody!r}"
