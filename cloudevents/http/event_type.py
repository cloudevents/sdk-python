import typing

from cloudevents.sdk.converters import binary, structured


def is_binary(headers: typing.Dict[str, str]) -> bool:
    """Uses internal marshallers to determine whether this event is binary
    :param headers: the HTTP headers
    :type headers: typing.Dict[str, str]
    :returns bool: returns a bool indicating whether the headers indicate a binary event type
    """
    headers = {key.lower(): value for key, value in headers.items()}
    content_type = headers.get("content-type", "")
    binary_parser = binary.BinaryHTTPCloudEventConverter()
    return binary_parser.can_read(content_type=content_type, headers=headers)


def is_structured(headers: typing.Dict[str, str]) -> bool:
    """Uses internal marshallers to determine whether this event is structured
    :param headers: the HTTP headers
    :type headers: typing.Dict[str, str]
    :returns bool: returns a bool indicating whether the headers indicate a structured event type
    """
    headers = {key.lower(): value for key, value in headers.items()}
    content_type = headers.get("content-type", "")
    structured_parser = structured.JSONHTTPCloudEventConverter()
    return structured_parser.can_read(
        content_type=content_type, headers=headers
    )
