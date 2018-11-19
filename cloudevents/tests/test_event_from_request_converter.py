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

import pytest
import io
import ujson

from cloudevents.sdk import exceptions
from cloudevents.sdk import marshaller

from cloudevents.sdk.event import v01
from cloudevents.sdk.event import upstream

from cloudevents.sdk.converters import binary
from cloudevents.sdk.converters import structured

from cloudevents.tests import data


def test_binary_converter_upstream():
    m = marshaller.NewHTTPMarshaller(
        [
            binary.NewBinaryHTTPCloudEventConverter(upstream.Event)
        ]
    )
    event = m.FromRequest(data.headers, None, lambda x: x)
    assert event is not None
    assert event.Get("type") == (data.ce_type, True)
    assert event.Get("id") == (data.ce_id, True)


def test_structured_converter_upstream():
    m = marshaller.NewHTTPMarshaller(
        [
            structured.NewJSONHTTPCloudEventConverter(upstream.Event)
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


# todo: clarify whether spec 0.1 doesn't support binary format
def test_binary_converter_v01():
    pytest.raises(
        exceptions.UnsupportedEvent,
        binary.NewBinaryHTTPCloudEventConverter,
        v01.Event)


def test_structured_converter_v01():
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


def test_default_http_marshaller():
    m = marshaller.NewDefaultHTTPMarshaller(upstream.Event)

    event = m.FromRequest(
        {"Content-Type": "application/cloudevents+json"},
        io.StringIO(ujson.dumps(data.ce)),
        lambda x: x.read()
    )
    assert event is not None
    assert event.Get("type") == (data.ce_type, True)
    assert event.Get("id") == (data.ce_id, True)
