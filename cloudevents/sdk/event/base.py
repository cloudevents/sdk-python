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

import base64
import io
import json
import typing

# Use consistent types for marshal and unmarshal functions across
# both JSON and Binary format.
MarshallerType = typing.Optional[
    typing.Callable[[typing.Any], typing.Union[bytes, str]]]
UnmarshallerType = typing.Optional[typing.Callable[[typing.IO], typing.Any]]


# TODO(slinkydeveloper) is this really needed?
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

    def MarshalJSON(self, data_marshaller: MarshallerType) -> str:
        if data_marshaller is None:
            def noop(x):
                return x
            data_marshaller = noop
        props = self.Properties()
        if "data" in props:
            data = data_marshaller(props.pop("data"))
            if isinstance(data, bytes):
                props["data_base64"] = base64.b64encode(data).decode("ascii")
            else:
                props["data"] = data
        return json.dumps(props)

    def UnmarshalJSON(
        self,
        b: typing.IO,
        data_unmarshaller: UnmarshallerType
    ):
        raw_ce = json.load(b)
        for name, value in raw_ce.items():
            if name == "data":
                value = data_unmarshaller(io.StringIO(value))
            if name == "data_base64":
                value = data_unmarshaller(io.BytesIO(base64.b64decode(value)))
                name = "data"
            self.Set(name, value)

    def UnmarshalBinary(
        self,
        headers: dict,
        body: typing.IO,
        data_unmarshaller: UnmarshallerType
    ):
        for header, value in headers.items():
            header = header.lower()
            if header == "content-type":
                self.SetContentType(value)
            elif header.startswith("ce-"):
                self.Set(header[3:], value)

        self.Set("data", data_unmarshaller(body))

    def MarshalBinary(
            self,
            data_marshaller: MarshallerType
    ) -> (dict, bytes):
        if data_marshaller is None:
            data_marshaller = json.dumps
        headers = {}
        if self.ContentType():
            headers["content-type"] = self.ContentType()
        props = self.Properties()
        for key, value in props.items():
            if key not in ["data", "extensions", "contenttype"]:
                if value is not None:
                    headers["ce-{0}".format(key)] = value

        for key, value in props.get("extensions").items():
            headers["ce-{0}".format(key)] = value

        data, _ = self.Get("data")
        data = data_marshaller(data)
        if isinstance(data, str):  # Convenience method for json.dumps
            data = data.encode("utf-8")
        return headers, data
