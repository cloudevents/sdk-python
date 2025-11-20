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


from datetime import datetime
from typing import Any, Optional, Protocol, Union


class BaseCloudEvent(Protocol):
    """
    The CloudEvent Python wrapper contract exposing generically-available
    properties and APIs.

    Implementations might handle fields and have other APIs exposed but are
    obliged to follow this contract.
    """

    def __init__(
        self,
        attributes: dict[str, Any],
        data: Optional[Union[dict[str, Any], str, bytes]] = None,
    ) -> None:
        """
        Create a new CloudEvent instance.

        :param attributes: The attributes of the CloudEvent instance.
        :param data: The payload of the CloudEvent instance.

        :raises ValueError: If any of the required attributes are missing or have invalid values.
        :raises TypeError: If any of the attributes have invalid types.
        """
        ...

    def get_id(self) -> str:
        """
        Retrieve the ID of the event.

        :return: The ID of the event.
        """
        ...

    def get_source(self) -> str:
        """
        Retrieve the source of the event.

        :return: The source of the event.
        """
        ...

    def get_type(self) -> str:
        """
        Retrieve the type of the event.

        :return: The type of the event.
        """
        ...

    def get_specversion(self) -> str:
        """
        Retrieve the specversion of the event.

        :return: The specversion of the event.
        """
        ...

    def get_datacontenttype(self) -> Optional[str]:
        """
        Retrieve the datacontenttype of the event.

        :return: The datacontenttype of the event.
        """
        ...

    def get_dataschema(self) -> Optional[str]:
        """
        Retrieve the dataschema of the event.

        :return: The dataschema of the event.
        """
        ...

    def get_subject(self) -> Optional[str]:
        """
        Retrieve the subject of the event.

        :return: The subject of the event.
        """
        ...

    def get_time(self) -> Optional[datetime]:
        """
        Retrieve the time of the event.

        :return: The time of the event.
        """
        ...

    def get_extension(self, extension_name: str) -> Any:
        """
        Retrieve an extension attribute of the event.

        :param extension_name: The name of the extension attribute.
        :return: The value of the extension attribute.
        """
        ...

    def get_data(self) -> Optional[Union[dict[str, Any], str, bytes]]:
        """
        Retrieve data of the event.

        :return: The data of the event.
        """
        ...

    def get_attributes(self) -> dict[str, Any]:
        """
        Retrieve all attributes of the event.

        :return: The attributes of the event.
        """
        ...
