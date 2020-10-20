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
from cloudevents.sdk.event import v03


def test_v03_time_property():
    event = v03.Event()

    time1 = "1234"
    event.time = time1
    assert event.EventTime() == time1

    time2 = "4321"
    event.SetEventTime(time2)
    assert event.time == time2


def test_v03_subject_property():
    event = v03.Event()

    subject1 = "<my-subject>"
    event.subject = subject1
    assert event.Subject() == subject1

    subject2 = "<my-subject2>"
    event.SetSubject(subject2)
    assert event.subject == subject2


def test_v03_schema_url_property():
    event = v03.Event()

    schema_url1 = "<my-schema>"
    event.schema_url = schema_url1
    assert event.SchemaURL() == schema_url1

    schema_url2 = "<my-schema2>"
    event.SetSchemaURL(schema_url2)
    assert event.schema_url == schema_url2


def test_v03_datacontentencoding_property():
    event = v03.Event()

    datacontentencoding1 = "<my-datacontentencoding>"
    event.datacontentencoding = datacontentencoding1
    assert event.ContentEncoding() == datacontentencoding1

    datacontentencoding2 = "<my-datacontentencoding2>"
    event.SetContentEncoding(datacontentencoding2)
    assert event.datacontentencoding == datacontentencoding2
