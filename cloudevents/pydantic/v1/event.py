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

from cloudevents.exceptions import PydanticFeatureNotInstalled
from cloudevents.pydantic.fields_docs import FIELD_DESCRIPTIONS

try:
    from pydantic import VERSION as PYDANTIC_VERSION

    pydantic_major_version = PYDANTIC_VERSION.split(".")[0]
    if pydantic_major_version == "2":
        from pydantic.v1 import BaseModel, Field
    else:
        from pydantic import BaseModel, Field  # type: ignore
except ImportError:  # pragma: no cover # hard to test
    raise PydanticFeatureNotInstalled(
        "CloudEvents pydantic feature is not installed. "
        "Install it using pip install cloudevents[pydantic]"
    )

from cloudevents import abstract, conversion, http
from cloudevents.exceptions import IncompatibleArgumentsError
from cloudevents.sdk.event import attribute


def _ce_json_dumps(  # type: ignore[no-untyped-def]
    obj: typing.Dict[str, typing.Any],
    *args,
    **kwargs,
) -> str:
    """Performs Pydantic-specific serialization of the event.

    Needed by the pydantic base-model to serialize the event correctly to json.
    Without this function the data will be incorrectly serialized.

    :param obj: CloudEvent represented as a dict.
    :param args: User arguments which will be passed to json.dumps function.
    :param kwargs: User arguments which will be passed to json.dumps function.

    :return: Event serialized as a standard JSON CloudEvent with user specific
    parameters.
    """
    # Using HTTP from dict due to performance issues.
    event = http.from_dict(obj)
    event_json = conversion.to_json(event)
    # Pydantic is known for initialization time lagging.
    return json.dumps(
        # We SHOULD de-serialize the value, to serialize it back with
        # the correct json args and kwargs passed by the user.
        # This MAY cause performance issues in the future.
        # When that issue will cause real problem you MAY add a special keyword
        # argument that disabled this conversion
        json.loads(event_json),
        *args,
        **kwargs,
    )


def _ce_json_loads(  # type: ignore[no-untyped-def]
    data: typing.AnyStr, *args, **kwargs  # noqa
) -> typing.Dict[typing.Any, typing.Any]:
    """Performs Pydantic-specific deserialization of the event.

    Needed by the pydantic base-model to de-serialize the event correctly from json.
    Without this function the data will be incorrectly de-serialized.

    :param obj: CloudEvent encoded as a json string.
    :param args: These arguments SHOULD NOT be passed by pydantic.
        Located here for fail-safe reasons, in-case it does.
    :param kwargs: These arguments SHOULD NOT be passed by pydantic.
        Located here for fail-safe reasons, in-case it does.

    :return: CloudEvent in a dict representation.
    """
    # Using HTTP from dict due to performance issues.
    # Pydantic is known for initialization time lagging.
    return conversion.to_dict(http.from_json(data))


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
    )
    datacontenttype: typing.Optional[str] = Field(
        title=FIELD_DESCRIPTIONS["datacontenttype"].get("title"),
        description=FIELD_DESCRIPTIONS["datacontenttype"].get("description"),
        example=FIELD_DESCRIPTIONS["datacontenttype"].get("example"),
    )
    dataschema: typing.Optional[str] = Field(
        title=FIELD_DESCRIPTIONS["dataschema"].get("title"),
        description=FIELD_DESCRIPTIONS["dataschema"].get("description"),
        example=FIELD_DESCRIPTIONS["dataschema"].get("example"),
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

    class Config:
        extra: str = "allow"  # this is the way we implement extensions
        schema_extra = {
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
        }
        json_dumps = _ce_json_dumps
        json_loads = _ce_json_loads

    def _get_attributes(self) -> typing.Dict[str, typing.Any]:
        return {
            key: conversion.best_effort_encode_attribute_value(value)
            for key, value in self.__dict__.items()
            if key != "data"
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
