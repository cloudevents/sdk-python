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

from cloudevents.sdk.event import v1


def test_v1_time_property():
    event = v1.Event()

    time1 = "1234"
    event.time = time1
    assert event.EventTime() == time1

    time2 = "4321"
    event.SetEventTime(time2)
    assert event.time == time2


def test_v1_subject_property():
    event = v1.Event()

    subject1 = "<my-subject>"
    event.subject = subject1
    assert event.Subject() == subject1

    subject2 = "<my-subject2>"
    event.SetSubject(subject2)
    assert event.subject == subject2


def test_v1_schema_property():
    event = v1.Event()

    schema1 = "<my-schema>"
    event.schema = schema1
    assert event.Schema() == schema1

    schema2 = "<my-schema2>"
    event.SetSchema(schema2)
    assert event.schema == schema2
