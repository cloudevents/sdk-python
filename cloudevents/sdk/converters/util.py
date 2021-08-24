import typing


def has_binary_headers(headers: typing.Dict[str, str]) -> bool:
    return (
        "ce-specversion" in headers
        or "ce-source" in headers
        or "ce-type" in headers
        or "ce-id" in headers
    )
