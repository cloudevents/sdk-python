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
import ujson
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
    def WithEventType(self, eventType: str) -> object:
        raise Exception("not implemented")

    def WithSource(self, source: str) -> object:
        raise Exception("not implemented")

    def WithEventID(self, eventID: str) -> object:
        raise Exception("not implemented")

    def WithEventTime(self, eventTime: str) -> object:
        raise Exception("not implemented")

    def WithSchemaURL(self, schemaURL: str) -> object:
        raise Exception("not implemented")

    def WithData(self, data: object) -> object:
        raise Exception("not implemented")

    def WithExtensions(self, extensions: dict) -> object:
        raise Exception("not implemented")

    def WithContentType(self, contentType: str) -> object:
        raise Exception("not implemented")


class BaseEvent(EventGetterSetter):

    def Properties(self, with_nullable=False) -> dict:
        props = dict()
        for name, value in self.__dict__.items():
            if str(name).startswith("ce__"):
                v = value.get()
                if v is not None or with_nullable:
                    props.update(
                        {
                            str(name).replace("ce__", ""): value.get()
                        }
                    )

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
        return io.StringIO(ujson.dumps(props))

    def UnmarshalJSON(self, b: typing.IO,
                      data_unmarshaller: typing.Callable):
        raw_ce = ujson.load(b)
        for name, value in raw_ce.items():
            if name == "data":
                value = data_unmarshaller(value)
            self.Set(name, value)

    def UnmarshalBinary(self, headers: dict, body: typing.IO,
                        data_unmarshaller: typing.Callable):
        props = self.Properties(with_nullable=True)
        exts = props.get("extensions")
        for key in props:
            formatted_key = "ce-{0}".format(key)
            if key != "extensions":
                self.Set(key, headers.get("ce-{0}".format(key)))
                if formatted_key in headers:
                    del headers[formatted_key]

        # rest of headers suppose to an extension?
        exts.update(**headers)
        self.Set("extensions", exts)
        self.Set("data", data_unmarshaller(body))

    def MarshalBinary(self) -> (dict, object):
        headers = {}
        props = self.Properties()
        for key, value in props.items():
            if key not in ["data", "extensions"]:
                if value is not None:
                    headers["ce-{0}".format(key)] = value

        exts = props.get("extensions")
        if len(exts) > 0:
            headers.update(**exts)

        data, _ = self.Get("data")
        return headers, data
