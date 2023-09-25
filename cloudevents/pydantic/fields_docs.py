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

from cloudevents.sdk.event import attribute

FIELD_DESCRIPTIONS = {
    "data": {
        "title": "Event Data",
        "description": (
            "CloudEvents MAY include domain-specific information about the occurrence."
            " When present, this information will be encapsulated within data.It is"
            " encoded into a media format which is specified by the datacontenttype"
            " attribute (e.g. application/json), and adheres to the dataschema format"
            " when those respective attributes are present."
        ),
    },
    "source": {
        "title": "Event Source",
        "description": (
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
        "example": "https://github.com/cloudevents",
    },
    "id": {
        "title": "Event ID",
        "description": (
            "Identifies the event. Producers MUST ensure that source + id is unique for"
            " each distinct event. If a duplicate event is re-sent (e.g. due to a"
            " network error) it MAY have the same id. Consumers MAY assume that Events"
            " with identical source and id are duplicates. MUST be unique within the"
            " scope of the producer"
        ),
        "example": "A234-1234-1234",
    },
    "type": {
        "title": "Event Type",
        "description": (
            "This attribute contains a value describing the type of event related to"
            " the originating occurrence. Often this attribute is used for routing,"
            " observability, policy enforcement, etc. The format of this is producer"
            " defined and might include information such as the version of the type"
        ),
        "example": "com.github.pull_request.opened",
    },
    "specversion": {
        "title": "Specification Version",
        "description": (
            "The version of the CloudEvents specification which the event uses. This"
            " enables the interpretation of the context.\n"
            "\n"
            "Currently, this attribute will only have the 'major'"
            " and 'minor' version numbers included in it. This allows for 'patch'"
            " changes to the specification to be made without changing this property's"
            " value in the serialization."
        ),
        "example": attribute.DEFAULT_SPECVERSION,
    },
    "time": {
        "title": "Occurrence Time",
        "description": (
            " Timestamp of when the occurrence happened. If the time of the occurrence"
            " cannot be determined then this attribute MAY be set to some other time"
            " (such as the current time) by the CloudEvents producer, however all"
            " producers for the same source MUST be consistent in this respect. In"
            " other words, either they all use the actual time of the occurrence or"
            " they all use the same algorithm to determine the value used."
        ),
        "example": "2018-04-05T17:31:00Z",
    },
    "subject": {
        "title": "Event Subject",
        "description": (
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
        "example": "123",
    },
    "datacontenttype": {
        "title": "Event Data Content Type",
        "description": (
            "Content type of data value. This attribute enables data to carry any type"
            " of content, whereby format and encoding might differ from that of the"
            " chosen event format."
        ),
        "example": "text/xml",
    },
    "dataschema": {
        "title": "Event Data Schema",
        "description": (
            "Identifies the schema that data adheres to. "
            "Incompatible changes to the schema SHOULD be reflected by a different URI"
        ),
    },
}

"""
The dictionary above contains title, description, example and other
NON-FUNCTIONAL data for pydantic fields. It could be potentially.
used across all the SDK.
Functional field configurations (e.g. defaults) are still defined
in the pydantic model classes.
"""
