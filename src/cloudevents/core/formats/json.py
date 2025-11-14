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
from json import JSONEncoder, dumps, loads
from typing import Any, Callable, Dict, Final, Optional, Pattern, Union

from dateutil.parser import isoparse  # type: ignore[import-untyped]

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
        r"^(application|text)/([a-zA-Z0-9\-\.]+\+)?json(;.*)?$"
    )

    def read(
        self,
        event_factory: Callable[
            [Dict[str, Any], Optional[Union[Dict[str, Any], str, bytes]]],
            BaseCloudEvent,
        ],
        data: Union[str, bytes],
    ) -> BaseCloudEvent:
        """
        Read a CloudEvent from a JSON formatted byte string.

        :param event_factory: A factory function to create CloudEvent instances.
        :param data: The JSON formatted byte array.
        :return: The CloudEvent instance.
        """
        decoded_data: str
        if isinstance(data, bytes):
            decoded_data = data.decode("utf-8")
        else:
            decoded_data = data

        event_attributes = loads(decoded_data)

        if "time" in event_attributes:
            event_attributes["time"] = isoparse(event_attributes["time"])

        event_data: Union[Dict[str, Any], str, bytes, None] = event_attributes.pop(
            "data", None
        )
        if event_data is None:
            event_data_base64 = event_attributes.pop("data_base64", None)
            if event_data_base64 is not None:
                event_data = base64.b64decode(event_data_base64)

        return event_factory(event_attributes, event_data)

    def write(self, event: BaseCloudEvent) -> bytes:
        """
        Write a CloudEvent to a JSON formatted byte string.

        :param event: The CloudEvent to write.
        :return: The CloudEvent as a JSON formatted byte array.
        """
        event_data = event.get_data()
        event_dict: dict[str, Any] = dict(event.get_attributes())

        if event_data is not None:
            if isinstance(event_data, (bytes, bytearray)):
                event_dict["data_base64"] = base64.b64encode(event_data).decode("utf-8")
            else:
                datacontenttype = event_dict.get("datacontenttype", "application/json")
                if re.match(JSONFormat.JSON_CONTENT_TYPE_PATTERN, datacontenttype):
                    event_dict["data"] = event_data
                else:
                    event_dict["data"] = str(event_data)

        return dumps(event_dict, cls=_JSONEncoderWithDatetime).encode("utf-8")

    def write_data(
        self,
        data: Optional[Union[Dict[str, Any], str, bytes]],
        datacontenttype: Optional[str],
    ) -> bytes:
        """
        Serialize just the data payload for HTTP binary mode.

        This method is used by HTTP binary content mode to serialize only the event
        data (not the attributes) into the HTTP body.

        :param data: Event data to serialize (dict, str, bytes, or None)
        :param datacontenttype: Content type of the data
        :return: Serialized data as bytes
        """
        if data is None:
            return b""

        # If data is already bytes, return as-is
        if isinstance(data, (bytes, bytearray)):
            return bytes(data)

        # If data is a string, encode as UTF-8
        if isinstance(data, str):
            return data.encode("utf-8")

        # If data is a dict and content type is JSON, serialize as JSON
        if isinstance(data, dict):
            if datacontenttype and re.match(
                JSONFormat.JSON_CONTENT_TYPE_PATTERN, datacontenttype
            ):
                return dumps(data, cls=_JSONEncoderWithDatetime).encode("utf-8")

        # Default: convert to string and encode
        return str(data).encode("utf-8")

    def read_data(
        self, body: bytes, datacontenttype: Optional[str]
    ) -> Optional[Union[Dict[str, Any], str, bytes]]:
        """
        Deserialize data payload from HTTP binary mode body.

        This method is used by HTTP binary content mode to deserialize the HTTP body
        into event data based on the content type.

        :param body: HTTP body as bytes
        :param datacontenttype: Content type of the data
        :return: Deserialized data (dict for JSON, str for text, bytes for binary)
        """
        if not body or len(body) == 0:
            return None

        # If content type indicates JSON, try to parse as JSON
        if datacontenttype and re.match(
            JSONFormat.JSON_CONTENT_TYPE_PATTERN, datacontenttype
        ):
            try:
                decoded = body.decode("utf-8")
                parsed: Dict[str, Any] = loads(decoded)
                return parsed
            except (ValueError, UnicodeDecodeError):
                # If JSON parsing fails, fall through to other handling
                pass

        # Try to decode as UTF-8 string
        try:
            return body.decode("utf-8")
        except UnicodeDecodeError:
            # If UTF-8 decoding fails, return as bytes
            return body

    def get_content_type(self) -> str:
        """
        Get the Content-Type header value for structured mode.

        :return: Content type string for CloudEvents structured content mode
        """
        return self.CONTENT_TYPE
