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
import ujson
import copy

from cloudevents.sdk import converters
from cloudevents.sdk import marshaller

from cloudevents.sdk.converters import structured
from cloudevents.sdk.event import v01
from cloudevents.sdk.event import upstream


from cloudevents.tests import data


def test_binary_event_to_request_upstream():
    m = marshaller.NewDefaultHTTPMarshaller(upstream.Event)
    event = m.FromRequest(
        {"Content-Type": "application/cloudevents+json"},
        io.StringIO(ujson.dumps(data.ce)),
        lambda x: x.read()
    )

    assert event is not None
    assert event.Get("type") == (data.ce_type, True)
    assert event.Get("id") == (data.ce_id, True)

    new_headers, _ = m.ToRequest(event, converters.TypeBinary, lambda x: x)
    assert new_headers is not None
    assert "ce-specversion" in new_headers


def test_structured_event_to_request_upstream():
    copy_of_ce = copy.deepcopy(data.ce)
    m = marshaller.NewDefaultHTTPMarshaller(upstream.Event)
    event = m.FromRequest(
        {"Content-Type": "application/cloudevents+json"},
        io.StringIO(ujson.dumps(data.ce)),
        lambda x: x.read()
    )
    assert event is not None
    assert event.Get("type") == (data.ce_type, True)
    assert event.Get("id") == (data.ce_id, True)

    new_headers, _ = m.ToRequest(event, converters.TypeStructured, lambda x: x)
    for key in new_headers:
        assert key in copy_of_ce


def test_structured_event_to_request_v01():
    copy_of_ce = copy.deepcopy(data.ce)
    m = marshaller.NewHTTPMarshaller(
        [
            structured.NewJSONHTTPCloudEventConverter(v01.Event)
        ]
    )
    event = m.FromRequest(
        {"Content-Type": "application/cloudevents+json"},
        io.StringIO(ujson.dumps(data.ce)),
        lambda x: x.read()
    )
    assert event is not None
    assert event.Get("type") == (data.ce_type, True)
    assert event.Get("id") == (data.ce_id, True)

    new_headers, _ = m.ToRequest(event, converters.TypeStructured, lambda x: x)
    for key in new_headers:
        assert key in copy_of_ce
