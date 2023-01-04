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

try:
    import pydantic
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
    """Perforns Pydantic-specific deserialization of the event.

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


class CloudEvent(abstract.CloudEvent, pydantic.BaseModel):  # type: ignore
    """
    A Python-friendly CloudEvent representation backed by Pydantic-modeled fields.

    Supports both binary and structured modes of the CloudEvents v1 specification.
    """

    @classmethod
    def create(
        cls, attributes: typing.Dict[str, typing.Any], data: typing.Optional[typing.Any]
    ) -> "CloudEvent":
        return cls(attributes, data)

    data: typing.Optional[typing.Any] = pydantic.Field(
        title="Event Data",
        description=(
            "CloudEvents MAY include domain-specific information about the occurrence."
            " When present, this information will be encapsulated within data.It is"
            " encoded into a media format which is specified by the datacontenttype"
            " attribute (e.g. application/json), and adheres to the dataschema format"
            " when those respective attributes are present."
        ),
    )
    source: str = pydantic.Field(
        title="Event Source",
        description=(
            "Identifies the context in which an event happened. Often this will include"
            " information such as the type of the event source, the organization"
            " publishing the event or the process that produced the event. The exact"
            " syntax and semantics behind the data encoded in the URI is defined by the"
            " event producer.\n"
            "\n"
            "Producers MUST ensure that source + id is unique for"
            " each distinct event.\n"
            "\n"
            "An application MAY assign a unique source to each"
            " distinct producer, which makes it easy to produce unique IDs since no"
            " other producer will have the same source. The application MAY use UUIDs,"
            " URNs, DNS authorities or an application-specific scheme to create unique"
            " source identifiers.\n"
            "\n"
            "A source MAY include more than one producer. In"
            " that case the producers MUST collaborate to ensure that source + id is"
            " unique for each distinct event."
        ),
        example="https://github.com/cloudevents",
    )

    id: str = pydantic.Field(
        default_factory=attribute.default_id_selection_algorithm,
        title="Event ID",
        description=(
            "Identifies the event. Producers MUST ensure that source + id is unique for"
            " each distinct event. If a duplicate event is re-sent (e.g. due to a"
            " network error) it MAY have the same id. Consumers MAY assume that Events"
            " with identical source and id are duplicates. MUST be unique within the"
            " scope of the producer"
        ),
        example="A234-1234-1234",
    )
    type: str = pydantic.Field(
        title="Event Type",
        description=(
            "This attribute contains a value describing the type of event related to"
            " the originating occurrence. Often this attribute is used for routing,"
            " observability, policy enforcement, etc. The format of this is producer"
            " defined and might include information such as the version of the type"
        ),
        example="com.github.pull_request.opened",
    )
    specversion: attribute.SpecVersion = pydantic.Field(
        default=attribute.DEFAULT_SPECVERSION,
        title="Specification Version",
        description=(
            "The version of the CloudEvents specification which the event uses. This"
            " enables the interpretation of the context.\n"
            "\n"
            "Currently, this attribute will only have the 'major'"
            " and 'minor' version numbers included in it. This allows for 'patch'"
            " changes to the specification to be made without changing this property's"
            " value in the serialization."
        ),
        example=attribute.DEFAULT_SPECVERSION,
    )
    time: typing.Optional[datetime.datetime] = pydantic.Field(
        default_factory=attribute.default_time_selection_algorithm,
        title="Occurrence Time",
        description=(
            " Timestamp of when the occurrence happened. If the time of the occurrence"
            " cannot be determined then this attribute MAY be set to some other time"
            " (such as the current time) by the CloudEvents producer, however all"
            " producers for the same source MUST be consistent in this respect. In"
            " other words, either they all use the actual time of the occurrence or"
            " they all use the same algorithm to determine the value used."
        ),
        example="2018-04-05T17:31:00Z",
    )

    subject: typing.Optional[str] = pydantic.Field(
        title="Event Subject",
        description=(
            "This describes the subject of the event in the context of the event"
            " producer (identified by source). In publish-subscribe scenarios, a"
            " subscriber will typically subscribe to events emitted by a source, but"
            " the source identifier alone might not be sufficient as a qualifier for"
            " any specific event if the source context has internal"
            " sub-structure.\n"
            "\n"
            "Identifying the subject of the event in context"
            " metadata (opposed to only in the data payload) is particularly helpful in"
            " generic subscription filtering scenarios where middleware is unable to"
            " interpret the data content. In the above example, the subscriber might"
            " only be interested in blobs with names ending with '.jpg' or '.jpeg' and"
            " the subject attribute allows for constructing a simple and efficient"
            " string-suffix filter for that subset of events."
        ),
        example="123",
    )
    datacontenttype: typing.Optional[str] = pydantic.Field(
        title="Event Data Content Type",
        description=(
            "Content type of data value. This attribute enables data to carry any type"
            " of content, whereby format and encoding might differ from that of the"
            " chosen event format."
        ),
        example="text/xml",
    )
    dataschema: typing.Optional[str] = pydantic.Field(
        title="Event Data Schema",
        description=(
            "Identifies the schema that data adheres to. "
            "Incompatible changes to the schema SHOULD be reflected by a different URI"
        ),
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
