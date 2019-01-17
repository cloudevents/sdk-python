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
import pytest
import io

from cloudevents.sdk import exceptions
from cloudevents.sdk import marshaller

from cloudevents.sdk.event import v01
from cloudevents.sdk.event import v02

from cloudevents.sdk.converters import binary
from cloudevents.sdk.converters import structured

from cloudevents.tests import data


def test_binary_converter_upstream():
    m = marshaller.NewHTTPMarshaller(
        [binary.NewBinaryHTTPCloudEventConverter()])
    event = m.FromRequest(v02.Event(), data.headers, None, lambda x: x)
    assert event is not None
    assert event.Get("type") == (data.ce_type, True)
    assert event.Get("id") == (data.ce_id, True)


def test_structured_converter_upstream():
    m = marshaller.NewHTTPMarshaller(
        [structured.NewJSONHTTPCloudEventConverter()])
    event = m.FromRequest(
        v02.Event(),
        {"Content-Type": "application/cloudevents+json"},
        io.StringIO(json.dumps(data.ce)),
        lambda x: x.read(),
    )

    assert event is not None
    assert event.Get("type") == (data.ce_type, True)
    assert event.Get("id") == (data.ce_id, True)


def test_binary_converter_v01():
    m = marshaller.NewHTTPMarshaller(
        [binary.NewBinaryHTTPCloudEventConverter()])

    pytest.raises(
        exceptions.UnsupportedEventConverter,
        m.FromRequest,
        v01.Event,
        {},
        None,
        lambda x: x,
    )


def test_unsupported_converter_v01():
    m = marshaller.NewHTTPMarshaller(
        [structured.NewJSONHTTPCloudEventConverter()])

    pytest.raises(
        exceptions.UnsupportedEventConverter,
        m.FromRequest,
        v01.Event,
        {},
        None,
        lambda x: x,
    )


def test_structured_converter_v01():
    m = marshaller.NewHTTPMarshaller(
        [structured.NewJSONHTTPCloudEventConverter()])
    event = m.FromRequest(
        v01.Event(),
        {"Content-Type": "application/cloudevents+json"},
        io.StringIO(json.dumps(data.ce)),
        lambda x: x.read(),
    )

    assert event is not None
    assert event.Get("type") == (data.ce_type, True)
    assert event.Get("id") == (data.ce_id, True)


def test_default_http_marshaller_with_structured():
    m = marshaller.NewDefaultHTTPMarshaller()

    event = m.FromRequest(
        v02.Event(),
        {"Content-Type": "application/cloudevents+json"},
        io.StringIO(json.dumps(data.ce)),
        lambda x: x.read(),
    )
    assert event is not None
    assert event.Get("type") == (data.ce_type, True)
    assert event.Get("id") == (data.ce_id, True)


def test_default_http_marshaller_with_binary():
    m = marshaller.NewDefaultHTTPMarshaller()

    event = m.FromRequest(
        v02.Event(), data.headers,
        io.StringIO(json.dumps(data.body)),
        json.load
    )
    assert event is not None
    assert event.Get("type") == (data.ce_type, True)
    assert event.Get("data") == (data.body, True)
    assert event.Get("id") == (data.ce_id, True)


def test_unsupported_event_configuration():
    m = marshaller.NewHTTPMarshaller(
        [binary.NewBinaryHTTPCloudEventConverter()])
    pytest.raises(
        exceptions.UnsupportedEventConverter,
        m.FromRequest,
        v01.Event(),
        {"Content-Type": "application/cloudevents+json"},
        io.StringIO(json.dumps(data.ce)),
        lambda x: x.read(),
    )


def test_invalid_data_unmarshaller():
    m = marshaller.NewDefaultHTTPMarshaller()
    pytest.raises(
        exceptions.InvalidDataUnmarshaller,
        m.FromRequest,
        v01.Event(), {}, None, None
    )


def test_invalid_data_marshaller():
    m = marshaller.NewDefaultHTTPMarshaller()
    pytest.raises(
        exceptions.InvalidDataMarshaller, m.ToRequest, v01.Event(), "blah", None
    )
