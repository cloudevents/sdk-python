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
import json
import typing

import cloudevents.exceptions as cloud_exceptions
from cloudevents.sdk import types

# TODO(slinkydeveloper) is this really needed?


class EventGetterSetter(object):  # pragma: no cover

    # ce-specversion
    def CloudEventVersion(self) -> str:
        raise Exception("not implemented")

    @property
    def specversion(self):
        return self.CloudEventVersion()

    def SetCloudEventVersion(self, specversion: str) -> object:
        raise Exception("not implemented")

    @specversion.setter
    def specversion(self, value: str):
        self.SetCloudEventVersion(value)

    # ce-type
    def EventType(self) -> str:
        raise Exception("not implemented")

    @property
    def type(self):
        return self.EventType()

    def SetEventType(self, eventType: str) -> object:
        raise Exception("not implemented")

    @type.setter
    def type(self, value: str):
        self.SetEventType(value)

    # ce-source
    def Source(self) -> str:
        raise Exception("not implemented")

    @property
    def source(self):
        return self.Source()

    def SetSource(self, source: str) -> object:
        raise Exception("not implemented")

    @source.setter
    def source(self, value: str):
        self.SetSource(value)

    # ce-id
    def EventID(self) -> str:
        raise Exception("not implemented")

    @property
    def id(self):
        return self.EventID()

    def SetEventID(self, eventID: str) -> object:
        raise Exception("not implemented")

    @id.setter
    def id(self, value: str):
        self.SetEventID(value)

    # ce-time
    def EventTime(self) -> str:
        raise Exception("not implemented")

    @property
    def time(self):
        return self.EventTime()

    def SetEventTime(self, eventTime: str) -> object:
        raise Exception("not implemented")

    @time.setter
    def time(self, value: str):
        self.SetEventTime(value)

    # ce-schema
    def SchemaURL(self) -> str:
        raise Exception("not implemented")

    @property
    def schema(self) -> str:
        return self.SchemaURL()

    def SetSchemaURL(self, schemaURL: str) -> object:
        raise Exception("not implemented")

    @schema.setter
    def schema(self, value: str):
        self.SetSchemaURL(value)

    # data
    def Data(self) -> object:
        raise Exception("not implemented")

    @property
    def data(self) -> object:
        return self.Data()

    def SetData(self, data: object) -> object:
        raise Exception("not implemented")

    @data.setter
    def data(self, value: object):
        self.SetData(value)

    # ce-extensions
    def Extensions(self) -> dict:
        raise Exception("not implemented")

    @property
    def extensions(self) -> dict:
        return self.Extensions()

    def SetExtensions(self, extensions: dict) -> object:
        raise Exception("not implemented")

    @extensions.setter
    def extensions(self, value: dict):
        self.SetExtensions(value)

    # Content-Type
    def ContentType(self) -> str:
        raise Exception("not implemented")

    @property
    def content_type(self) -> str:
        return self.ContentType()

    def SetContentType(self, contentType: str) -> object:
        raise Exception("not implemented")

    @content_type.setter
    def content_type(self, value: str):
        self.SetContentType(value)


class BaseEvent(EventGetterSetter):
    _ce_required_fields = set()
    _ce_optional_fields = set()

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

    def MarshalJSON(self, data_marshaller: types.MarshallerType) -> str:
        if data_marshaller is None:
            data_marshaller = lambda x: x  # noqa: E731
        props = self.Properties()
        if "data" in props:
            data = props.pop("data")
            try:
                data = data_marshaller(data)
            except Exception as e:
                raise cloud_exceptions.DataMarshallerError(
                    "Failed to marshall data with error: "
                    f"{type(e).__name__}('{e}')"
                )
            if isinstance(data, (bytes, bytes, memoryview)):
                props["data_base64"] = base64.b64encode(data).decode("ascii")
            else:
                props["data"] = data
        if "extensions" in props:
            extensions = props.pop("extensions")
            props.update(extensions)
        return json.dumps(props)

    def UnmarshalJSON(
        self,
        b: typing.Union[str, bytes],
        data_unmarshaller: types.UnmarshallerType,
    ):
        raw_ce = json.loads(b)

        missing_fields = self._ce_required_fields - raw_ce.keys()
        if len(missing_fields) > 0:
            raise cloud_exceptions.MissingRequiredFields(
                f"Missing required attributes: {missing_fields}"
            )

        for name, value in raw_ce.items():
            decoder = lambda x: x
            if name == "data":
                # Use the user-provided serializer, which may have customized
                # JSON decoding
                decoder = lambda v: data_unmarshaller(json.dumps(v))
            if name == "data_base64":
                decoder = lambda v: data_unmarshaller(base64.b64decode(v))
                name = "data"

            try:
                set_value = decoder(value)
            except Exception as e:
                raise cloud_exceptions.DataUnmarshallerError(
                    "Failed to unmarshall data with error: "
                    f"{type(e).__name__}('{e}')"
                )
            self.Set(name, set_value)

    def UnmarshalBinary(
        self,
        headers: dict,
        body: typing.Union[bytes, str],
        data_unmarshaller: types.UnmarshallerType,
    ):
        required_binary_fields = {
            f"ce-{field}" for field in self._ce_required_fields
        }
        missing_fields = required_binary_fields - headers.keys()

        if len(missing_fields) > 0:
            raise cloud_exceptions.MissingRequiredFields(
                f"Missing required attributes: {missing_fields}"
            )

        for header, value in headers.items():
            header = header.lower()
            if header == "content-type":
                self.SetContentType(value)
            elif header.startswith("ce-"):
                self.Set(header[3:], value)

        try:
            raw_ce = data_unmarshaller(body)
        except Exception as e:
            raise cloud_exceptions.DataUnmarshallerError(
                "Failed to unmarshall data with error: "
                f"{type(e).__name__}('{e}')"
            )
        self.Set("data", raw_ce)

    def MarshalBinary(
        self, data_marshaller: types.MarshallerType
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
        try:
            data = data_marshaller(data)
        except Exception as e:
            raise cloud_exceptions.DataMarshallerError(
                "Failed to marshall data with error: "
                f"{type(e).__name__}('{e}')"
            )
        if isinstance(data, str):  # Convenience method for json.dumps
            data = data.encode("utf-8")
        return headers, data
