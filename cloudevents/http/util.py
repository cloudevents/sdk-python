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

import json
import typing


def default_marshaller(content: any):
    if content is None:
        return None
    try:
        return json.dumps(content)
    except TypeError:
        return content


ContentT = typing.TypeVar("ContentT", bound=typing.Union[str, bytes])


def _json_or_string(
    content: typing.Optional[ContentT],
) -> typing.Optional[
    typing.Union[
        typing.Dict[typing.Any, typing.Any],
        typing.List[typing.Any],
        ContentT,
    ]
]:
    if content is None:
        return None
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
        return content
