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

from cloudevents.exceptions import PydanticFeatureNotInstalled

try:
    from pydantic import VERSION as PYDANTIC_VERSION

    pydantic_major_version = PYDANTIC_VERSION.split(".")[0]
    if pydantic_major_version == "1":
        from cloudevents.pydantic.v1 import CloudEvent, from_dict, from_http, from_json

    else:
        from cloudevents.pydantic.v2 import (  # type: ignore
            CloudEvent,
            from_dict,
            from_http,
            from_json,
        )

except ImportError:  # pragma: no cover # hard to test
    raise PydanticFeatureNotInstalled(
        "CloudEvents pydantic feature is not installed. "
        "Install it using pip install cloudevents[pydantic]"
    )

__all__ = ["CloudEvent", "from_json", "from_dict", "from_http"]
