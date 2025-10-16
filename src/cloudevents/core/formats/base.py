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


from typing import Callable, Optional, Protocol, Union

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
            [dict, Optional[Union[dict, str, bytes]]], BaseCloudEvent
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
