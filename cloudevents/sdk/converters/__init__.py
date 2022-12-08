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

from cloudevents.sdk.converters import binary, structured
from cloudevents.sdk.converters.binary import is_binary
from cloudevents.sdk.converters.structured import is_structured

TypeBinary: str = binary.BinaryHTTPCloudEventConverter.TYPE
TypeStructured: str = structured.JSONHTTPCloudEventConverter.TYPE

__all__ = [
    "binary",
    "structured",
    "is_binary",
    "is_structured",
    "TypeBinary",
    "TypeStructured",
]
