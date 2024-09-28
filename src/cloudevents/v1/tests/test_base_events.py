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

import cloudevents_v1.exceptions as cloud_exceptions
from cloudevents_v1.sdk.event import v1, v03


@pytest.mark.parametrize("event_class", [v1.Event, v03.Event])
def test_unmarshall_binary_missing_fields(event_class):
    event = event_class()
    with pytest.raises(cloud_exceptions.MissingRequiredFields) as e:
        event.UnmarshalBinary({}, "", lambda x: x)
    assert "Missing required attributes: " in str(e.value)


@pytest.mark.parametrize("event_class", [v1.Event, v03.Event])
def test_get_nonexistent_optional(event_class):
    event = event_class()
    event.SetExtensions({"ext1": "val"})
    res = event.Get("ext1")
    assert res[0] == "val" and res[1] is True
