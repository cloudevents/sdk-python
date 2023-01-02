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

import base64
import json
import typing
from typing import Set

import cloudevents.exceptions as cloud_exceptions
from cloudevents.sdk import types

# TODO(slinkydeveloper) is this really needed?


class EventGetterSetter(object):  # pragma: no cover

    # ce-specversion
    def CloudEventVersion(self) -> str:
        raise Exception("not implemented")

    @property
    def specversion(self) -> str:
        return self.CloudEventVersion()

    @specversion.setter
    def specversion(self, value: str) -> None:
        self.SetCloudEventVersion(value)

    def SetCloudEventVersion(self, specversion: str) -> object:
        raise Exception("not implemented")

    # ce-type
    def EventType(self) -> str:
        raise Exception("not implemented")

    @property
    def type(self) -> str:
        return self.EventType()

    @type.setter
    def type(self, value: str) -> None:
        self.SetEventType(value)

    def SetEventType(self, eventType: str) -> object:
        raise Exception("not implemented")

    # ce-source
    def Source(self) -> str:
        raise Exception("not implemented")

    @property
    def source(self) -> str:
        return self.Source()

    @source.setter
    def source(self, value: str) -> None:
        self.SetSource(value)

    def SetSource(self, source: str) -> object:
        raise Exception("not implemented")

    # ce-id
    def EventID(self) -> str:
        raise Exception("not implemented")

    @property
    def id(self) -> str:
        return self.EventID()

    @id.setter
    def id(self, value: str) -> None:
        self.SetEventID(value)

    def SetEventID(self, eventID: str) -> object:
        raise Exception("not implemented")

    # ce-time
    def EventTime(self) -> typing.Optional[str]:
        raise Exception("not implemented")

    @property
    def time(self) -> typing.Optional[str]:
        return self.EventTime()

    @time.setter
    def time(self, value: typing.Optional[str]) -> None:
        self.SetEventTime(value)

    def SetEventTime(self, eventTime: typing.Optional[str]) -> object:
        raise Exception("not implemented")

    # ce-schema
    def SchemaURL(self) -> typing.Optional[str]:
        raise Exception("not implemented")

    @property
    def schema(self) -> typing.Optional[str]:
        return self.SchemaURL()

    @schema.setter
    def schema(self, value: typing.Optional[str]) -> None:
        self.SetSchemaURL(value)

    def SetSchemaURL(self, schemaURL: typing.Optional[str]) -> object:
        raise Exception("not implemented")

    # data
    def Data(self) -> typing.Optional[object]:
        raise Exception("not implemented")

    @property
    def data(self) -> typing.Optional[object]:
        return self.Data()

    @data.setter
    def data(self, value: typing.Optional[object]) -> None:
        self.SetData(value)

    def SetData(self, data: typing.Optional[object]) -> object:
        raise Exception("not implemented")

    # ce-extensions
    def Extensions(self) -> dict:
        raise Exception("not implemented")

    @property
    def extensions(self) -> dict:
        return self.Extensions()

    @extensions.setter
    def extensions(self, value: dict) -> None:
        self.SetExtensions(value)

    def SetExtensions(self, extensions: dict) -> object:
        raise Exception("not implemented")

    # Content-Type
    def ContentType(self) -> typing.Optional[str]:
        raise Exception("not implemented")

    @property
    def content_type(self) -> typing.Optional[str]:
        return self.ContentType()

    @content_type.setter
    def content_type(self, value: typing.Optional[str]) -> None:
        self.SetContentType(value)

    def SetContentType(self, contentType: typing.Optional[str]) -> object:
        raise Exception("not implemented")


class BaseEvent(EventGetterSetter):
    """Base implementation of the CloudEvent."""

    _ce_required_fields: Set[str] = set()
    """A set of required CloudEvent field names."""
    _ce_optional_fields: Set[str] = set()
    """A set of optional CloudEvent field names."""

    def Properties(self, with_nullable: bool = False) -> dict:
        props = dict()
        for name, value in self.__dict__.items():
            if str(name).startswith("ce__"):
                v = value.get()
                if v is not None or with_nullable:
                    props.update({str(name).replace("ce__", ""): value.get()})

        return props

    def Get(self, key: str) -> typing.Tuple[typing.Optional[object], bool]:
        formatted_key: str = "ce__{0}".format(key.lower())
        key_exists: bool = hasattr(self, formatted_key)
        if not key_exists:
            exts = self.Extensions()
            return exts.get(key), key in exts
        value: typing.Any = getattr(self, formatted_key)
        return value.get(), key_exists

    def Set(self, key: str, value: typing.Optional[object]) -> None:
        formatted_key: str = "ce__{0}".format(key)
        key_exists: bool = hasattr(self, formatted_key)
        if key_exists:
            attr = getattr(self, formatted_key)
            attr.set(value)
            setattr(self, formatted_key, attr)
            return
        exts = self.Extensions()
        exts.update({key: value})
        self.Set("extensions", exts)

    def MarshalJSON(
        self, data_marshaller: typing.Optional[types.MarshallerType]
    ) -> str:
        props = self.Properties()
        if "data" in props:
            data = props.pop("data")
            try:
                if data_marshaller:
                    data = data_marshaller(data)
            except Exception as e:
                raise cloud_exceptions.DataMarshallerError(
                    f"Failed to marshall data with error: {type(e).__name__}('{e}')"
                )
            if isinstance(data, (bytes, bytearray, memoryview)):
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
    ) -> None:
        raw_ce = json.loads(b)

        missing_fields = self._ce_required_fields - raw_ce.keys()
        if len(missing_fields) > 0:
            raise cloud_exceptions.MissingRequiredFields(
                f"Missing required attributes: {missing_fields}"
            )

        for name, value in raw_ce.items():
            try:
                if name == "data":
                    decoded_value = data_unmarshaller(json.dumps(value))
                elif name == "data_base64":
                    decoded_value = data_unmarshaller(base64.b64decode(value))
                    name = "data"
                else:
                    decoded_value = value
            except Exception as e:
                raise cloud_exceptions.DataUnmarshallerError(
                    "Failed to unmarshall data with error: "
                    f"{type(e).__name__}('{e}')"
                )
            self.Set(name, decoded_value)

    def UnmarshalBinary(
        self,
        headers: typing.Mapping[str, str],
        body: typing.Union[str, bytes],
        data_unmarshaller: types.UnmarshallerType,
    ) -> None:
        required_binary_fields = {f"ce-{field}" for field in self._ce_required_fields}
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
                f"Failed to unmarshall data with error: {type(e).__name__}('{e}')"
            )
        self.Set("data", raw_ce)

    def MarshalBinary(
        self, data_marshaller: typing.Optional[types.MarshallerType]
    ) -> typing.Tuple[typing.Dict[str, str], bytes]:
        if not data_marshaller:
            data_marshaller = json.dumps
        headers: typing.Dict[str, str] = {}
        content_type = self.ContentType()
        if content_type:
            headers["content-type"] = content_type
        props: typing.Dict = self.Properties()
        for key, value in props.items():
            if key not in ["data", "extensions", "datacontenttype"]:
                if value is not None:
                    headers["ce-{0}".format(key)] = value
        extensions = props.get("extensions")
        if extensions is None or not isinstance(extensions, typing.Mapping):
            raise cloud_exceptions.DataMarshallerError(
                "No extensions are available in the binary event."
            )
        for key, value in extensions.items():
            headers["ce-{0}".format(key)] = value

        data, _ = self.Get("data")
        try:
            data = data_marshaller(data)
        except Exception as e:
            raise cloud_exceptions.DataMarshallerError(
                f"Failed to marshall data with error: {type(e).__name__}('{e}')"
            )
        if isinstance(data, str):  # Convenience method for json.dumps
            data = data.encode("utf-8")
        return headers, data
