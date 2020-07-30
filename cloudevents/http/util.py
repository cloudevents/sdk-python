import json
import typing


def default_marshaller(content: any):
    if content is None or len(content) == 0:
        return None
    try:
        return json.dumps(content)
    except TypeError:
        return content


def _json_or_string(content: typing.Union[str, bytes]):
    if len(content) == 0:
        return None
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError) as e:
        return content
