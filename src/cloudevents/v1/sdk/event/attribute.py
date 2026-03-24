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

import datetime
import uuid
from enum import Enum


class SpecVersion(str, Enum):
    """
    The version of the CloudEvents specification which an event uses.
    This enables the interpretation of the context.

    Currently, this attribute will only have the 'major' and 'minor' version numbers
    included in it. This allows for 'patch' changes to the specification to be made
    without changing this property's value in the serialization.
    """

    v0_3 = "0.3"
    v1_0 = "1.0"


DEFAULT_SPECVERSION = SpecVersion.v1_0


def default_time_selection_algorithm() -> datetime.datetime:
    """
    :return: A time value which will be used as CloudEvent time attribute value.
    """
    return datetime.datetime.now(datetime.timezone.utc)


def default_id_selection_algorithm() -> str:
    """
    :return: Globally unique id to be used as a CloudEvent id attribute value.
    """
    return str(uuid.uuid4())
