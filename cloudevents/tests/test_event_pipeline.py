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

import ujson

from cloudevents.sdk.event import v01
from cloudevents.sdk.event import upstream

from cloudevents.sdk import converters
from cloudevents.sdk import marshaller
from cloudevents.sdk.converters import structured

from cloudevents.tests import data


def test_event_pipeline_upstream():
    event = (
        upstream.Event().
        WithContentType(data.contentType).
        WithData(data.body).
        WithEventID(data.ce_id).
        WithSource(data.source).
        WithEventTime(data.eventTime).
        WithEventType(data.ce_type)
    )
    m = marshaller.NewDefaultHTTPMarshaller(type(event))
    new_headers, body = m.ToRequest(event, converters.TypeBinary, lambda x: x)
    assert new_headers is not None
    assert "ce-specversion" in new_headers
    assert "ce-type" in new_headers
    assert "ce-source" in new_headers
    assert "ce-id" in new_headers
    assert "ce-time" in new_headers
    assert "ce-contenttype" in new_headers
    assert data.body == body


def test_event_pipeline_v01():
    event = (
        v01.Event().
        WithContentType(data.contentType).
        WithData(data.body).
        WithEventID(data.ce_id).
        WithSource(data.source).
        WithEventTime(data.eventTime).
        WithEventType(data.ce_type)
    )
    m = marshaller.NewHTTPMarshaller(
        [
            structured.NewJSONHTTPCloudEventConverter(type(event))
        ]
    )

    _, body = m.ToRequest(event, converters.TypeStructured, lambda x: x)
    new_headers = ujson.load(body)
    assert new_headers is not None
    assert "cloudEventsVersion" in new_headers
    assert "eventType" in new_headers
    assert "source" in new_headers
    assert "eventID" in new_headers
    assert "eventTime" in new_headers
    assert "contentType" in new_headers
    assert data.body == new_headers["data"]
