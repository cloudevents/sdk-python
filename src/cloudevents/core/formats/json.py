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
import re
from datetime import datetime
from json import JSONEncoder, dumps
from typing import Any, Final, Pattern, Union

from cloudevents.core.base import BaseCloudEvent
from cloudevents.core.formats.base import Format


class _JSONEncoderWithDatetime(JSONEncoder):
    """
    Custom JSON encoder to handle datetime objects in the format required by the CloudEvents spec.
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            dt = obj.isoformat()
            # 'Z' denotes a UTC offset of 00:00 see
            # https://www.rfc-editor.org/rfc/rfc3339#section-2
            if dt.endswith("+00:00"):
                dt = dt.removesuffix("+00:00") + "Z"
            return dt

        return super().default(obj)


class JSONFormat(Format):
    CONTENT_TYPE: Final[str] = "application/cloudevents+json"
    JSON_CONTENT_TYPE_PATTERN: Pattern[str] = re.compile(
        r"^(application|text)\\/([a-zA-Z]+\\+)?json(;.*)*$"
    )

    def read(self, data: Union[str, bytes]) -> BaseCloudEvent:
        pass

    def write(self, event: BaseCloudEvent) -> bytes:
        """
        Write a CloudEvent to a JSON formatted byte string.

        :param event: The CloudEvent to write.
        :return: The CloudEvent as a JSON formatted byte array.
        """
        event_data = event.get_data()
        event_dict: dict[str, Any] = {**event.get_attributes()}

        if event_data is not None:
            if isinstance(event_data, (bytes, bytearray)):
                event_dict["data_base64"] = base64.b64encode(event_data).decode("utf-8")
            else:
                datacontenttype = event_dict.get(
                    "datacontenttype", JSONFormat.CONTENT_TYPE
                )
                if re.match(JSONFormat.JSON_CONTENT_TYPE_PATTERN, datacontenttype):
                    event_dict["data"] = dumps(event_data)
                else:
                    event_dict["data"] = str(event_data)

        return dumps(event_dict, cls=_JSONEncoderWithDatetime).encode("utf-8")
