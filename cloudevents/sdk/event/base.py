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

import io
import json
import typing


class EventGetterSetter(object):
    def CloudEventVersion(self) -> str:
        raise Exception("not implemented")

    # CloudEvent attribute getters
    def EventType(self) -> str:
        raise Exception("not implemented")

    def Source(self) -> str:
        raise Exception("not implemented")

    def EventID(self) -> str:
        raise Exception("not implemented")

    def EventTime(self) -> str:
        raise Exception("not implemented")

    def SchemaURL(self) -> str:
        raise Exception("not implemented")

    def Data(self) -> object:
        raise Exception("not implemented")

    def Extensions(self) -> dict:
        raise Exception("not implemented")

    def ContentType(self) -> str:
        raise Exception("not implemented")

    # CloudEvent attribute constructors
    # Each setter return an instance of its class
    #      in order to build a pipeline of setter
    def SetEventType(self, eventType: str) -> object:
        raise Exception("not implemented")

    def SetSource(self, source: str) -> object:
        raise Exception("not implemented")

    def SetEventID(self, eventID: str) -> object:
        raise Exception("not implemented")

    def SetEventTime(self, eventTime: str) -> object:
        raise Exception("not implemented")

    def SetSchemaURL(self, schemaURL: str) -> object:
        raise Exception("not implemented")

    def SetData(self, data: object) -> object:
        raise Exception("not implemented")

    def SetExtensions(self, extensions: dict) -> object:
        raise Exception("not implemented")

    def SetContentType(self, contentType: str) -> object:
        raise Exception("not implemented")


class BaseEvent(EventGetterSetter):
    def Properties(self, with_nullable=False) -> dict:
        props = dict()
        for name, value in self.__dict__.items():
            if str(name).startswith("ce__"):
                v = value.get()
                if v is not None or with_nullable:
                    props.update({str(name).replace("ce__", ""): value.get()})

        return props

    def Get(self, key: str) -> (object, bool):
        formatted_key = "ce__{0}".format(key.lower())
        ok = hasattr(self, formatted_key)
        value = getattr(self, formatted_key, None)
        if not ok:
            exts = self.Extensions()
            return exts.get(key), key in exts

        return value.get(), ok

    def Set(self, key: str, value: object):
        formatted_key = "ce__{0}".format(key)
        key_exists = hasattr(self, formatted_key)
        if key_exists:
            attr = getattr(self, formatted_key)
            attr.set(value)
            setattr(self, formatted_key, attr)
            return

        exts = self.Extensions()
        exts.update({key: value})
        self.Set("extensions", exts)

    def MarshalJSON(self, data_marshaller: typing.Callable) -> typing.IO:
        props = self.Properties()
        props["data"] = data_marshaller(props.get("data"))
        return io.BytesIO(json.dumps(props).encode("utf-8"))

    def UnmarshalJSON(self, b: typing.IO, data_unmarshaller: typing.Callable):
        raw_ce = json.load(b)
        for name, value in raw_ce.items():
            if name == "data":
                value = data_unmarshaller(value)
            self.Set(name, value)

    def UnmarshalBinary(
        self,
        headers: dict,
        body: typing.IO,
        data_unmarshaller: typing.Callable
    ):
        binary_mapping = {
            "content-type": "contenttype",
            # TODO(someone): add Distributed Tracing. It's not clear
            # if this is one extension or two.
            # https://github.com/cloudevents/spec/blob/master/extensions/distributed-tracing.md
        }
        for header, value in headers.items():
            header = header.lower()
            if header in binary_mapping:
                self.Set(binary_mapping[header], value)
            elif header.startswith("ce-"):
                self.Set(header[3:], value)

        self.Set("data", data_unmarshaller(body))

    def MarshalBinary(
            self,
            data_marshaller: typing.Callable
    ) -> (dict, object):
        headers = {}
        if self.ContentType():
            headers["content-type"] = self.ContentType()
        props = self.Properties()
        for key, value in props.items():
            if key not in ["data", "extensions", "contenttype"]:
                if value is not None:
                    headers["ce-{0}".format(key)] = value

        for key, value in props.get("extensions"):
            headers["ce-{0}".format(key)] = value

        data, _ = self.Get("data")
        return headers, data_marshaller(data)
