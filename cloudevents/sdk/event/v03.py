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
import typing

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
        self.ce__datacontentencoding = opt.Option("datacontentencoding", None, False)
        self.ce__subject = opt.Option("subject", None, False)
        self.ce__time = opt.Option("time", None, False)
        self.ce__schemaurl = opt.Option("schemaurl", None, False)
        self.ce__data = opt.Option("data", None, False)
        self.ce__extensions = opt.Option("extensions", dict(), False)

    def CloudEventVersion(self) -> str:
        return str(self.ce__specversion.get())

    def EventType(self) -> str:
        return str(self.ce__type.get())

    def Source(self) -> str:
        return str(self.ce__source.get())

    def EventID(self) -> str:
        return str(self.ce__id.get())

    def EventTime(self) -> typing.Optional[str]:
        result = self.ce__time.get()
        if result is None:
            return None
        return str(result)

    def Subject(self) -> typing.Optional[str]:
        result = self.ce__subject.get()
        if result is None:
            return None
        return str(result)

    def SchemaURL(self) -> typing.Optional[str]:
        result = self.ce__schemaurl.get()
        if result is None:
            return None
        return str(result)

    def Data(self) -> typing.Optional[object]:
        return self.ce__data.get()

    def Extensions(self) -> dict:
        result = self.ce__extensions.get()
        if result is None:
            return {}
        return dict(result)

    def ContentType(self) -> typing.Optional[str]:
        result = self.ce__datacontenttype.get()
        if result is None:
            return None
        return str(result)

    def ContentEncoding(self) -> typing.Optional[str]:
        result = self.ce__datacontentencoding.get()
        if result is None:
            return None
        return str(result)

    def SetEventType(self, eventType: str) -> base.BaseEvent:
        self.Set("type", eventType)
        return self

    def SetSource(self, source: str) -> base.BaseEvent:
        self.Set("source", source)
        return self

    def SetEventID(self, eventID: str) -> base.BaseEvent:
        self.Set("id", eventID)
        return self

    def SetEventTime(self, eventTime: typing.Optional[str]) -> base.BaseEvent:
        self.Set("time", eventTime)
        return self

    def SetSubject(self, subject: typing.Optional[str]) -> base.BaseEvent:
        self.Set("subject", subject)
        return self

    def SetSchemaURL(self, schemaURL: typing.Optional[str]) -> base.BaseEvent:
        self.Set("schemaurl", schemaURL)
        return self

    def SetData(self, data: typing.Optional[object]) -> base.BaseEvent:
        self.Set("data", data)
        return self

    def SetExtensions(self, extensions: typing.Optional[dict]) -> base.BaseEvent:
        self.Set("extensions", extensions)
        return self

    def SetContentType(self, contentType: typing.Optional[str]) -> base.BaseEvent:
        self.Set("datacontenttype", contentType)
        return self

    def SetContentEncoding(
        self, contentEncoding: typing.Optional[str]
    ) -> base.BaseEvent:
        self.Set("datacontentencoding", contentEncoding)
        return self

    @property
    def datacontentencoding(self) -> typing.Optional[str]:
        return self.ContentEncoding()

    @datacontentencoding.setter
    def datacontentencoding(self, value: typing.Optional[str]) -> None:
        self.SetContentEncoding(value)

    @property
    def subject(self) -> typing.Optional[str]:
        return self.Subject()

    @subject.setter
    def subject(self, value: typing.Optional[str]) -> None:
        self.SetSubject(value)

    @property
    def schema_url(self) -> typing.Optional[str]:
        return self.SchemaURL()

    @schema_url.setter
    def schema_url(self, value: typing.Optional[str]) -> None:
        self.SetSchemaURL(value)
