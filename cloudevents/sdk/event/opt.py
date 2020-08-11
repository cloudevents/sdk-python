# All Rights Reserved.
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


class Option(object):
    def __init__(self, name, value, is_required):
        self.name = name
        self.value = value
        self.is_required = is_required

    def set(self, new_value):
        is_none = new_value is None
        if self.is_required and is_none:
            raise ValueError(
                "Attribute value error: '{0}', "
                ""
                "invalid new value.".format(self.name)
            )

        self.value = new_value

    def get(self):
        return self.value

    def required(self):
        return self.is_required

    def __eq__(self, obj):
        return (
            isinstance(obj, Option)
            and obj.name == self.name
            and obj.value == self.value
            and obj.is_required == self.is_required
        )
