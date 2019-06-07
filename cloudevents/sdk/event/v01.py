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

from cloudevents.sdk.event import base
from cloudevents.sdk.event import opt


class Event(base.BaseEvent):
    def __init__(self):
        self.ce__cloudEventsVersion = opt.Option(
            "cloudEventsVersion",
            "0.1",
            True
        )
        self.ce__eventType = opt.Option(
            "eventType",
            None,
            True
        )
        self.ce__eventTypeVersion = opt.Option(
            "eventTypeVersion",
            None,
            False
        )
        self.ce__source = opt.Option(
            "source",
            None,
            True
        )
        self.ce__eventID = opt.Option(
            "eventID",
            None,
            True
        )
        self.ce__eventTime = opt.Option(
            "eventTime",
            None,
            True
        )
        self.ce__schemaURL = opt.Option(
            "schemaURL",
            None,
            False
        )
        self.ce__contentType = opt.Option(
            "contentType",
            None,
            False
        )
        self.ce__data = opt.Option(
            "data",
            None,
            False
        )
        self.ce__extensions = opt.Option(
            "extensions",
            dict(),
            False
        )

    def CloudEventVersion(self) -> str:
        return self.ce__cloudEventsVersion.get()

    def EventType(self) -> str:
        return self.ce__eventType.get()

    def Source(self) -> str:
        return self.ce__source.get()

    def EventID(self) -> str:
        return self.ce__eventID.get()

    def EventTime(self) -> str:
        return self.ce__eventTime.get()

    def SchemaURL(self) -> str:
        return self.ce__schemaURL.get()

    def Data(self) -> object:
        return self.ce__data.get()

    def Extensions(self) -> dict:
        return self.ce__extensions.get()

    def ContentType(self) -> str:
        return self.ce__contentType.get()

    def SetEventType(self, eventType: str) -> base.BaseEvent:
        self.Set("eventType", eventType)
        return self

    def SetSource(self, source: str) -> base.BaseEvent:
        self.Set("source", source)
        return self

    def SetEventID(self, eventID: str) -> base.BaseEvent:
        self.Set("eventID", eventID)
        return self

    def SetEventTime(self, eventTime: str) -> base.BaseEvent:
        self.Set("eventTime", eventTime)
        return self

    def SetSchemaURL(self, schemaURL: str) -> base.BaseEvent:
        self.Set("schemaURL", schemaURL)
        return self

    def SetData(self, data: object) -> base.BaseEvent:
        self.Set("data", data)
        return self

    def SetExtensions(self, extensions: dict) -> base.BaseEvent:
        self.Set("extensions", extensions)
        return self

    def SetContentType(self, contentType: str) -> base.BaseEvent:
        self.Set("contentType", contentType)
        return self

    # additional getter/setter
    def EventTypeVersion(self) -> str:
        return self.ce__eventTypeVersion.get()

    def WithEventTypeVersion(self, eventTypeVersion: str) -> base.BaseEvent:
        self.Set("eventTypeVersion", eventTypeVersion)
        return self
