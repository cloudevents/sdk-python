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
    def __init__(
        self, attributes: dict[str, Any], data: Optional[Union[dict, str, bytes]] = None
    ) -> None: ...

    def get_id(self) -> str: ...

    def get_source(self) -> str: ...

    def get_type(self) -> str: ...

    def get_specversion(self) -> str: ...

    def get_datacontenttype(self) -> Optional[str]: ...

    def get_dataschema(self) -> Optional[str]: ...

    def get_subject(self) -> Optional[str]: ...

    def get_time(self) -> Optional[datetime]: ...

    def get_extension(self, extension_name: str) -> Any: ...

    def get_data(self) -> Optional[Union[dict, str, bytes]]: ...

    def get_attributes(self) -> dict[str, Any]: ...
