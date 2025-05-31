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
import pytest
from cloudevents.conversion import _best_effort_serialize_to_json
from cloudevents.http import CloudEvent


@pytest.fixture()
def dummy_event():
    return CloudEvent({"type": "dummy", "source": "dummy"})


def test_json_methods(dummy_event):
    from cloudevents.conversion import to_json
    from cloudevents.http.conversion import from_json
    from cloudevents.http.json_methods import from_json as deprecated_from_json
    from cloudevents.http.json_methods import to_json as deprecated_to_json

    assert from_json(to_json(dummy_event)) == deprecated_from_json(
        deprecated_to_json(dummy_event)
    )


def test_http_methods(dummy_event):
    from cloudevents.http import from_http, to_binary, to_structured
    from cloudevents.http.http_methods import from_http as deprecated_from_http
    from cloudevents.http.http_methods import to_binary as deprecated_to_binary
    from cloudevents.http.http_methods import to_structured as deprecated_to_structured

    assert from_http(*to_binary(dummy_event)) == deprecated_from_http(
        *deprecated_to_binary(dummy_event)
    )
    assert from_http(*to_structured(dummy_event)) == deprecated_from_http(
        *deprecated_to_structured(dummy_event)
    )


def test_util():
    from cloudevents.http.util import default_marshaller  # noqa

    assert _best_effort_serialize_to_json(None) == default_marshaller(None)


def test_event_type():
    from cloudevents.http.event_type import is_binary, is_structured  # noqa


def test_http_module_imports():
    from cloudevents.http import (  # noqa
        CloudEvent,
        from_dict,
        from_http,
        from_json,
        is_binary,
        is_structured,
        to_binary,
        to_binary_http,
        to_json,
        to_structured,
        to_structured_http,
    )
