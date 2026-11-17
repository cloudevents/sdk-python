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

import typing


def has_binary_headers(headers: typing.Mapping[str, str]) -> bool:
    """Determines if all CloudEvents required headers are presents
    in the `headers`.

    :returns: True if all the headers are present, False otherwise.
    """
    return (
        "ce-specversion" in headers
        and "ce-source" in headers
        and "ce-type" in headers
        and "ce-id" in headers
    )
