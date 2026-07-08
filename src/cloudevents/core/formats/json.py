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
from typing import Any, Final, Pattern

from dateutil.parser import isoparse

from cloudevents.core.base import BaseCloudEvent, EventFactory
from cloudevents.core.formats.base import BatchFormat
from cloudevents.core.spec import SPECVERSION_V0_3, SPECVERSION_V1_0


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


class JSONFormat(BatchFormat):
    CONTENT_TYPE: Final[str] = "application/cloudevents+json"
    DEFAULT_CONTENT_TYPE: Final[str] = "application/json"
    BATCH_CONTENT_TYPE: Final[str] = "application/cloudevents-batch+json"
    JSON_CONTENT_TYPE_PATTERN: Pattern[str] = re.compile(
        r"^(application|text)/([a-zA-Z0-9\-\.]+\+)?json(;.*)?$"
    )

    def _event_to_dict(self, event: BaseCloudEvent) -> dict[str, Any]:
        """
        Build the JSON-serializable dict for a single CloudEvent.

        Shared by single-event ``write`` and batch ``write_batch`` so the two
        paths cannot drift.
        """
        event_data = event.get_data()
        event_dict: dict[str, Any] = dict(event.get_attributes())
        specversion = event_dict.get("specversion", SPECVERSION_V1_0)

        if event_data is not None:
            if isinstance(event_data, (bytes, bytearray)):
                if specversion == SPECVERSION_V0_3:
                    event_dict["datacontentencoding"] = "base64"
                    event_dict["data"] = base64.b64encode(event_data).decode("utf-8")
                else:
                    event_dict["data_base64"] = base64.b64encode(event_data).decode(
                        "utf-8"
                    )
            else:
                datacontenttype = event_dict.get(
                    "datacontenttype", self.DEFAULT_CONTENT_TYPE
                )
                if re.match(JSONFormat.JSON_CONTENT_TYPE_PATTERN, datacontenttype):
                    event_dict["data"] = event_data
                else:
                    event_dict["data"] = str(event_data)
        return event_dict

    def write(self, event: BaseCloudEvent) -> bytes:
        """
        Write a CloudEvent to a JSON formatted byte string.

        Supports both v0.3 and v1.0 CloudEvents:
        - v0.3: Uses 'datacontentencoding: base64' with base64-encoded 'data' field
        - v1.0: Uses 'data_base64' field (no datacontentencoding)

        :param event: The CloudEvent to write.
        :return: The CloudEvent as a JSON formatted byte array.
        """
        return dumps(self._event_to_dict(event), cls=_JSONEncoderWithDatetime).encode(
            "utf-8"
        )

    def write_batch(self, events: list[BaseCloudEvent]) -> bytes:
        """
        Write a list of CloudEvents to a JSON Batch formatted byte string.

        The output is a JSON array whose elements are CloudEvents rendered per the
        JSON event format. An empty list serializes to ``b"[]"``.

        :param events: The CloudEvents to write.
        :return: The batch as a JSON formatted byte array.
        """
        return dumps(
            [self._event_to_dict(event) for event in events],
            cls=_JSONEncoderWithDatetime,
        ).encode("utf-8")

    def _dict_to_event(
        self,
        event_factory: EventFactory | None,
        event_attributes: dict[str, Any],
    ) -> BaseCloudEvent:
        """
        Build a CloudEvent from an already-parsed attributes dict.

        Shared by single-event ``read`` and batch ``read_batch``. Handles version
        auto-detection, 'time' parsing, v0.3 'datacontentencoding', and v1.0
        'data_base64'.
        """
        if event_factory is None:
            from cloudevents.core.bindings.common import get_event_factory_for_version

            specversion = event_attributes.get("specversion", SPECVERSION_V1_0)
            event_factory = get_event_factory_for_version(specversion)

        if "time" in event_attributes:
            event_attributes["time"] = isoparse(event_attributes["time"])

        specversion = event_attributes.get("specversion", SPECVERSION_V1_0)
        event_data: dict[str, Any] | str | bytes | None = event_attributes.pop(
            "data", None
        )

        if (
            specversion == SPECVERSION_V0_3
            and "datacontentencoding" in event_attributes
        ):
            encoding = event_attributes.get("datacontentencoding", "").lower()
            if encoding == "base64" and isinstance(event_data, str):
                event_data = base64.b64decode(event_data)

        if event_data is None:
            event_data_base64 = event_attributes.pop("data_base64", None)
            if event_data_base64 is not None:
                event_data = base64.b64decode(event_data_base64)

        return event_factory(event_attributes, event_data)

    def read(
        self,
        event_factory: EventFactory | None,
        data: str | bytes,
    ) -> BaseCloudEvent:
        """
        Read a CloudEvent from a JSON formatted byte string.

        Supports both v0.3 and v1.0 CloudEvents:
        - v0.3: Uses 'datacontentencoding' attribute with 'data' field
        - v1.0: Uses 'data_base64' field (no datacontentencoding)

        :param event_factory: A factory function to create CloudEvent instances.
                             If None, automatically detects version from 'specversion' field.
        :param data: The JSON formatted byte array.
        :return: The CloudEvent instance.
        """
        decoded_data: str
        if isinstance(data, bytes):
            decoded_data = data.decode("utf-8")
        else:
            decoded_data = data

        return self._dict_to_event(event_factory, loads(decoded_data))

    def read_batch(
        self,
        event_factory: EventFactory | None,
        data: str | bytes,
    ) -> list[BaseCloudEvent]:
        """
        Read a list of CloudEvents from a JSON Batch formatted byte string.

        The input MUST be a JSON array; each element is parsed per the JSON event
        format. When ``event_factory`` is None the version is auto-detected per
        element, so a batch may mix v0.3 and v1.0 events. An empty array returns an
        empty list. An invalid element propagates its exception and aborts the call.

        :param event_factory: Factory to create CloudEvent instances, or None to
                              auto-detect each element's version.
        :param data: The JSON Batch formatted byte array.
        :return: The list of CloudEvent instances.
        :raises ValueError: If the body is not a JSON array.
        """
        decoded_data: str
        if isinstance(data, bytes):
            decoded_data = data.decode("utf-8")
        else:
            decoded_data = data

        parsed = loads(decoded_data)
        if not isinstance(parsed, list):
            raise ValueError(
                "JSON batch payload must be a JSON array of CloudEvents, "
                f"got {type(parsed).__name__}"
            )

        events: list[BaseCloudEvent] = []
        for index, item in enumerate(parsed):
            if not isinstance(item, dict):
                raise ValueError(
                    f"JSON batch element at index {index} must be a JSON object "
                    f"representing a CloudEvent, got {type(item).__name__}"
                )
            try:
                events.append(self._dict_to_event(event_factory, item))
            except Exception as exc:
                raise ValueError(
                    f"Failed to parse CloudEvent at index {index} of the JSON "
                    f"batch: {exc}"
                ) from exc

        return events

    def write_data(
        self,
        data: dict[str, Any] | str | bytes | None,
        datacontenttype: str | None,
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
            content_type = datacontenttype or self.DEFAULT_CONTENT_TYPE
            if re.match(JSONFormat.JSON_CONTENT_TYPE_PATTERN, content_type):
                return dumps(data, cls=_JSONEncoderWithDatetime).encode("utf-8")

            # for other contenttypes we still try to generate a json-decodable string
            # if not possible, a string representing
            try:
                return dumps(data, cls=_JSONEncoderWithDatetime).encode("utf-8")
            except TypeError:
                pass

        # according to the spec, we return an encoded string per default
        # careful: the result is not json-decodable as the dict keys are single-quoted
        return str(data).encode("utf-8")

    def read_data(
        self, body: bytes, datacontenttype: str | None
    ) -> dict[str, Any] | str | bytes | None:
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
        content_type = datacontenttype or self.DEFAULT_CONTENT_TYPE
        if re.match(JSONFormat.JSON_CONTENT_TYPE_PATTERN, content_type):
            try:
                decoded = body.decode("utf-8")
                parsed: dict[str, Any] = loads(decoded)
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

    def get_batch_content_type(self) -> str:
        """
        Get the Content-Type header value for JSON batch mode.

        :return: ``application/cloudevents-batch+json``
        """
        return self.BATCH_CONTENT_TYPE
