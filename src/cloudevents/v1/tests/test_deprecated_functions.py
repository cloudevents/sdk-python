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
from cloudevents_v1.http import (
    CloudEvent,
    to_binary,
    to_binary_http,
    to_structured,
    to_structured_http,
)


@pytest.fixture
def event():
    return CloudEvent({"source": "s", "type": "t"}, None)


def test_to_binary_http_deprecated(event):
    with pytest.deprecated_call():
        assert to_binary(event) == to_binary_http(event)


def test_to_structured_http_deprecated(event):
    with pytest.deprecated_call():
        assert to_structured(event) == to_structured_http(event)
