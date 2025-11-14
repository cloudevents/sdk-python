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


from typing import Any, Callable, Dict, Optional, Protocol, Union

from cloudevents.core.base import BaseCloudEvent


class Format(Protocol):
    """
    Protocol defining the contract for CloudEvent format implementations.

    Format implementations are responsible for serializing and deserializing CloudEvents
    to and from specific wire formats (e.g., JSON, Avro, Protobuf). Each format must
    implement both read and write operations to convert between CloudEvent objects and
    their byte representations according to the CloudEvents specification.
    """

    def read(
        self,
        event_factory: Callable[
            [Dict[str, Any], Optional[Union[Dict[str, Any], str, bytes]]],
            BaseCloudEvent,
        ],
        data: Union[str, bytes],
    ) -> BaseCloudEvent:
        """
        Deserialize a CloudEvent from its wire format representation.

        :param event_factory: A factory function that creates CloudEvent instances from
            attributes and data. The factory should accept a dictionary of attributes and
            optional event data (dict, str, or bytes).
        :param data: The serialized CloudEvent data as a string or bytes.
        :return: A CloudEvent instance constructed from the deserialized data.
        :raises ValueError: If the data cannot be parsed or is invalid according to the format.
        """
        ...

    def write(self, event: BaseCloudEvent) -> bytes:
        """
        Serialize a CloudEvent to its wire format representation.

        :param event: The CloudEvent instance to serialize.
        :return: The CloudEvent serialized as bytes in the format's wire representation.
        :raises ValueError: If the event cannot be serialized according to the format.
        """
        ...

    def write_data(
        self,
        data: Optional[Union[Dict[str, Any], str, bytes]],
        datacontenttype: Optional[str],
    ) -> bytes:
        """
        Serialize just the data payload for protocol bindings (e.g., HTTP binary mode).

        :param data: Event data to serialize (dict, str, bytes, or None)
        :param datacontenttype: Content type of the data
        :return: Serialized data as bytes
        """
        ...

    def read_data(
        self, body: bytes, datacontenttype: Optional[str]
    ) -> Optional[Union[Dict[str, Any], str, bytes]]:
        """
        Deserialize data payload from protocol bindings (e.g., HTTP binary mode).

        :param body: HTTP body as bytes
        :param datacontenttype: Content type of the data
        :return: Deserialized data (dict for JSON, str for text, bytes for binary)
        """
        ...

    def get_content_type(self) -> str:
        """
        Get the Content-Type header value for structured mode.

        :return: Content type string for CloudEvents structured content mode
        """
        ...
