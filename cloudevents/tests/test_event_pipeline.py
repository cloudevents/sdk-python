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

from cloudevents.sdk.event import v01
from cloudevents.sdk.event import v02

from cloudevents.sdk import converters
from cloudevents.sdk import marshaller
from cloudevents.sdk.converters import structured

from cloudevents.tests import data


def test_event_pipeline_upstream():
    event = (
        v02.Event()
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
    assert isinstance(body, str)
    assert data.body == body


def test_event_pipeline_v01():
    event = (
        v01.Event()
        .SetContentType(data.contentType)
        .SetData(data.body)
        .SetEventID(data.ce_id)
        .SetSource(data.source)
        .SetEventTime(data.eventTime)
        .SetEventType(data.ce_type)
    )
    m = marshaller.NewHTTPMarshaller([structured.NewJSONHTTPCloudEventConverter()])

    _, body = m.ToRequest(event, converters.TypeStructured, lambda x: x)
    assert isinstance(body, io.BytesIO)
    new_headers = json.load(io.TextIOWrapper(body, encoding="utf-8"))
    assert new_headers is not None
    assert "cloudEventsVersion" in new_headers
    assert "eventType" in new_headers
    assert "source" in new_headers
    assert "eventID" in new_headers
    assert "eventTime" in new_headers
    assert "contentType" in new_headers
    assert data.body == new_headers["data"]
