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

from cloudevents.sdk.event import base, opt


class Event(base.BaseEvent):
    _ce_required_fields = {"id", "source", "type", "specversion"}

    _ce_optional_fields = {
        "datacontentencoding",
        "datacontenttype",
        "schemaurl",
        "subject",
        "time",
    }

    def __init__(self):
        self.ce__specversion = opt.Option("specversion", "0.3", True)
        self.ce__id = opt.Option("id", None, True)
        self.ce__source = opt.Option("source", None, True)
        self.ce__type = opt.Option("type", None, True)

        self.ce__datacontenttype = opt.Option("datacontenttype", None, False)
        self.ce__datacontentencoding = opt.Option(
            "datacontentencoding", None, False
        )
        self.ce__subject = opt.Option("subject", None, False)
        self.ce__time = opt.Option("time", None, False)
        self.ce__schemaurl = opt.Option("schemaurl", None, False)
        self.ce__data = opt.Option("data", None, False)
        self.ce__extensions = opt.Option("extensions", dict(), False)

    def CloudEventVersion(self) -> str:
        return self.ce__specversion.get()

    def EventType(self) -> str:
        return self.ce__type.get()

    def Source(self) -> str:
        return self.ce__source.get()

    def EventID(self) -> str:
        return self.ce__id.get()

    def EventTime(self) -> str:
        return self.ce__time.get()

    def Subject(self) -> str:
        return self.ce__subject.get()

    def SchemaURL(self) -> str:
        return self.ce__schemaurl.get()

    def Data(self) -> object:
        return self.ce__data.get()

    def Extensions(self) -> dict:
        return self.ce__extensions.get()

    def ContentType(self) -> str:
        return self.ce__datacontenttype.get()

    def ContentEncoding(self) -> str:
        return self.ce__datacontentencoding.get()

    def SetEventType(self, eventType: str) -> base.BaseEvent:
        self.Set("type", eventType)
        return self

    def SetSource(self, source: str) -> base.BaseEvent:
        self.Set("source", source)
        return self

    def SetEventID(self, eventID: str) -> base.BaseEvent:
        self.Set("id", eventID)
        return self

    def SetEventTime(self, eventTime: str) -> base.BaseEvent:
        self.Set("time", eventTime)
        return self

    def SetSubject(self, subject: str) -> base.BaseEvent:
        self.Set("subject", subject)
        return self

    def SetSchemaURL(self, schemaURL: str) -> base.BaseEvent:
        self.Set("schemaurl", schemaURL)
        return self

    def SetData(self, data: object) -> base.BaseEvent:
        self.Set("data", data)
        return self

    def SetExtensions(self, extensions: dict) -> base.BaseEvent:
        self.Set("extensions", extensions)
        return self

    def SetContentType(self, contentType: str) -> base.BaseEvent:
        self.Set("datacontenttype", contentType)
        return self

    def SetContentEncoding(self, contentEncoding: str) -> base.BaseEvent:
        self.Set("datacontentencoding", contentEncoding)
        return self

    @property
    def datacontentencoding(self):
        return self.ContentEncoding()

    @datacontentencoding.setter
    def datacontentencoding(self, value: str):
        self.SetContentEncoding(value)

    @property
    def subject(self) -> str:
        return self.Subject()

    @subject.setter
    def subject(self, value: str):
        self.SetSubject(value)

    @property
    def schema_url(self) -> str:
        return self.SchemaURL()

    @schema_url.setter
    def schema_url(self, value: str):
        self.SetSchemaURL(value)
