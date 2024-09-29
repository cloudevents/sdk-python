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
from cloudevents_v1.sdk.event.opt import Option


def test_set_raise_error():
    with pytest.raises(ValueError):
        o = Option("test", "value", True)
        o.set(None)


def test_options_eq_override():
    o = Option("test", "value", True)
    assert o.required()

    o2 = Option("test", "value", True)
    assert o2.required()

    assert o == o2
    o.set("setting to new value")

    assert o != o2
