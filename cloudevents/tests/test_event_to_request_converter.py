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
import copy
import pytest

from cloudevents.sdk import converters
from cloudevents.sdk import marshaller

from cloudevents.sdk.converters import structured
from cloudevents.sdk.event import v01, v02, v03, v1
from cloudevents.sdk.event import v02


from cloudevents.tests import data


@pytest.mark.parametrize("event_class", [v02.Event, v03.Event, v1.Event])
def test_binary_event_to_request_upstream(event_class):
    m = marshaller.NewDefaultHTTPMarshaller()
    event = m.FromRequest(
        event_class(),
        {"Content-Type": "application/cloudevents+json"},
        io.StringIO(json.dumps(data.json_ce[event_class])),
        lambda x: x.read(),
    )

    assert event is not None
    assert event.EventType() == data.ce_type
    assert event.EventID() == data.ce_id
    assert event.ContentType() == data.contentType

    new_headers, _ = m.ToRequest(event, converters.TypeBinary, lambda x: x)
    assert new_headers is not None
    assert "ce-specversion" in new_headers


@pytest.mark.parametrize("event_class", [v02.Event, v03.Event, v1.Event])
def test_structured_event_to_request_upstream(event_class):
    copy_of_ce = copy.deepcopy(data.json_ce[event_class])
    m = marshaller.NewDefaultHTTPMarshaller()
    http_headers = {"content-type": "application/cloudevents+json"}
    event = m.FromRequest(
        event_class(), http_headers, io.StringIO(json.dumps(data.json_ce[event_class])), lambda x: x.read()
    )
    assert event is not None
    assert event.EventType() == data.ce_type
    assert event.EventID() == data.ce_id
    assert event.ContentType() == data.contentType

    new_headers, _ = m.ToRequest(event, converters.TypeStructured, lambda x: x)
    for key in new_headers:
        if key == "content-type":
            assert new_headers[key] == http_headers[key]
            continue
        assert key in copy_of_ce


def test_structured_event_to_request_v01():
    copy_of_ce = copy.deepcopy(data.json_ce[v02.Event])
    m = marshaller.NewHTTPMarshaller([structured.NewJSONHTTPCloudEventConverter()])
    http_headers = {"content-type": "application/cloudevents+json"}
    event = m.FromRequest(
        v01.Event(), http_headers, io.StringIO(json.dumps(data.json_ce[v02.Event])), lambda x: x.read()
    )
    assert event is not None
    assert event.Get("type") == (data.ce_type, True)
    assert event.Get("id") == (data.ce_id, True)

    new_headers, _ = m.ToRequest(event, converters.TypeStructured, lambda x: x)
    for key in new_headers:
        if key == "content-type":
            assert new_headers[key] == http_headers[key]
            continue
        assert key in copy_of_ce
