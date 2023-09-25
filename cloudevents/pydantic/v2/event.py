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

import datetime
import json
import typing
from typing import Any

from pydantic.deprecated import parse as _deprecated_parse

from cloudevents.exceptions import PydanticFeatureNotInstalled
from cloudevents.pydantic.fields_docs import FIELD_DESCRIPTIONS

try:
    from pydantic import BaseModel, ConfigDict, Field, model_serializer
except ImportError:  # pragma: no cover # hard to test
    raise PydanticFeatureNotInstalled(
        "CloudEvents pydantic feature is not installed. "
        "Install it using pip install cloudevents[pydantic]"
    )

from cloudevents import abstract, conversion
from cloudevents.exceptions import IncompatibleArgumentsError
from cloudevents.sdk.event import attribute


class CloudEvent(abstract.CloudEvent, BaseModel):  # type: ignore
    """
    A Python-friendly CloudEvent representation backed by Pydantic-modeled fields.

    Supports both binary and structured modes of the CloudEvents v1 specification.
    """

    @classmethod
    def create(
        cls, attributes: typing.Dict[str, typing.Any], data: typing.Optional[typing.Any]
    ) -> "CloudEvent":
        return cls(attributes, data)

    data: typing.Optional[typing.Any] = Field(
        title=FIELD_DESCRIPTIONS["data"].get("title"),
        description=FIELD_DESCRIPTIONS["data"].get("description"),
        example=FIELD_DESCRIPTIONS["data"].get("example"),
        default=None,
    )
    source: str = Field(
        title=FIELD_DESCRIPTIONS["source"].get("title"),
        description=FIELD_DESCRIPTIONS["source"].get("description"),
        example=FIELD_DESCRIPTIONS["source"].get("example"),
    )
    id: str = Field(
        title=FIELD_DESCRIPTIONS["id"].get("title"),
        description=FIELD_DESCRIPTIONS["id"].get("description"),
        example=FIELD_DESCRIPTIONS["id"].get("example"),
        default_factory=attribute.default_id_selection_algorithm,
    )
    type: str = Field(
        title=FIELD_DESCRIPTIONS["type"].get("title"),
        description=FIELD_DESCRIPTIONS["type"].get("description"),
        example=FIELD_DESCRIPTIONS["type"].get("example"),
    )
    specversion: attribute.SpecVersion = Field(
        title=FIELD_DESCRIPTIONS["specversion"].get("title"),
        description=FIELD_DESCRIPTIONS["specversion"].get("description"),
        example=FIELD_DESCRIPTIONS["specversion"].get("example"),
        default=attribute.DEFAULT_SPECVERSION,
    )
    time: typing.Optional[datetime.datetime] = Field(
        title=FIELD_DESCRIPTIONS["time"].get("title"),
        description=FIELD_DESCRIPTIONS["time"].get("description"),
        example=FIELD_DESCRIPTIONS["time"].get("example"),
        default_factory=attribute.default_time_selection_algorithm,
    )
    subject: typing.Optional[str] = Field(
        title=FIELD_DESCRIPTIONS["subject"].get("title"),
        description=FIELD_DESCRIPTIONS["subject"].get("description"),
        example=FIELD_DESCRIPTIONS["subject"].get("example"),
        default=None,
    )
    datacontenttype: typing.Optional[str] = Field(
        title=FIELD_DESCRIPTIONS["datacontenttype"].get("title"),
        description=FIELD_DESCRIPTIONS["datacontenttype"].get("description"),
        example=FIELD_DESCRIPTIONS["datacontenttype"].get("example"),
        default=None,
    )
    dataschema: typing.Optional[str] = Field(
        title=FIELD_DESCRIPTIONS["dataschema"].get("title"),
        description=FIELD_DESCRIPTIONS["dataschema"].get("description"),
        example=FIELD_DESCRIPTIONS["dataschema"].get("example"),
        default=None,
    )

    def __init__(  # type: ignore[no-untyped-def]
        self,
        attributes: typing.Optional[typing.Dict[str, typing.Any]] = None,
        data: typing.Optional[typing.Any] = None,
        **kwargs,
    ):
        """
        :param attributes: A dict with CloudEvent attributes.
            Minimally expects the attributes 'type' and 'source'. If not given the
            attributes 'specversion', 'id' or 'time', this will create
            those attributes with default values.

            If no attribute is given the class MUST use the kwargs as the attributes.

            Example Attributes:
            {
                "specversion": "1.0",
                "type": "com.github.pull_request.opened",
                "source": "https://github.com/cloudevents/spec/pull",
                "id": "A234-1234-1234",
                "time": "2018-04-05T17:31:00Z",
            }

        :param data: Domain-specific information about the occurrence.
        """
        if attributes:
            if len(kwargs) != 0:
                # To prevent API complexity and confusion.
                raise IncompatibleArgumentsError(
                    "Attributes dict and kwargs are incompatible."
                )
            attributes = {k.lower(): v for k, v in attributes.items()}
            kwargs.update(attributes)
        super(CloudEvent, self).__init__(data=data, **kwargs)

    model_config = ConfigDict(
        extra="allow",  # this is the way we implement extensions
        json_schema_extra={
            "example": {
                "specversion": "1.0",
                "type": "com.github.pull_request.opened",
                "source": "https://github.com/cloudevents/spec/pull",
                "subject": "123",
                "id": "A234-1234-1234",
                "time": "2018-04-05T17:31:00Z",
                "comexampleextension1": "value",
                "comexampleothervalue": 5,
                "datacontenttype": "text/xml",
                "data": '<much wow="xml"/>',
            }
        },
    )

    """
    We should use a @model_validator decorator to handle JSON deserialisation,
    however it's not possible to completely bypass the internal pydantic logic
    and still use the CloudEvents shared conversion logic.

    Same issue applies to the multiple from/to JSON conversion logic in the
    @model_serializer implemented after

    To remove the need for the multiple from/to JSON transformation we need
    major refactor in the SDK conversion logic.
    """

    @classmethod
    def model_validate_json(
        cls,
        json_data: typing.Union[str, bytes, bytearray],
        *,
        strict: typing.Optional[bool] = None,
        context: typing.Optional[typing.Dict[str, Any]] = None,
    ) -> "CloudEvent":
        return conversion.from_json(cls, json_data)

    @classmethod
    def parse_raw(
        cls,
        b: typing.Union[str, bytes],
        *,
        content_type: typing.Optional[str] = None,
        encoding: str = "utf8",
        proto: typing.Optional[_deprecated_parse.Protocol] = None,
        allow_pickle: bool = False,
    ) -> "CloudEvent":
        return conversion.from_json(cls, b)

    @model_serializer(when_used="json")
    def _ce_json_dumps(self) -> typing.Dict[str, typing.Any]:
        """Performs Pydantic-specific serialization of the event when
        serializing the model using `.model_dump_json()` method.

        Needed by the pydantic base-model to serialize the event correctly to json.
        Without this function the data will be incorrectly serialized.

        :param self: CloudEvent.

        :return: Event serialized as a standard CloudEvent dict with user specific
        parameters.
        """
        # Here mypy complains about json.loads returning Any
        # which is incompatible with this method return type
        # but we know it's always a dictionary in this case
        return json.loads(conversion.to_json(self))  # type: ignore

    def _get_attributes(self) -> typing.Dict[str, typing.Any]:
        return {
            key: conversion.best_effort_encode_attribute_value(value)
            for key, value in self.__dict__.items()
            if key not in ["data"]
        }

    def get_data(self) -> typing.Optional[typing.Any]:
        return self.data

    def __setitem__(self, key: str, value: typing.Any) -> None:
        """
        Set event attribute value

        MUST NOT set event data with this method, use `.data` member instead

        Method SHOULD mimic `cloudevents.http.event.CloudEvent` interface

        :param key: Event attribute name
        :param value: New event attribute value
        """
        if key != "data":  # to mirror the behaviour of the http event
            setattr(self, key, value)
        else:
            pass  # It is de-facto ignored by the http event

    def __delitem__(self, key: str) -> None:
        """
        SHOULD raise `KeyError` if no event attribute for the given key exists.

        Method SHOULD mimic `cloudevents.http.event.CloudEvent` interface
        :param key:  The event attribute name.
        """
        if key == "data":
            raise KeyError(key)  # to mirror the behaviour of the http event
        delattr(self, key)
