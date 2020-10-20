import typing


def has_binary_headers(headers: typing.Dict[str, str]) -> bool:
    return (
        "ce-specversion" in headers
        and "ce-source" in headers
        and "ce-type" in headers
        and "ce-id" in headers
    )
