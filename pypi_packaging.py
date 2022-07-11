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

import os

import pkg_resources

from setup import pypi_config


def createTag():
    from git import Repo

    # Get local pypi cloudevents version
    published_pypi_version = pkg_resources.get_distribution(
        pypi_config["package_name"]
    ).version

    # Ensure pypi and local package versions match
    if pypi_config["version_target"] == published_pypi_version:
        # Create local git tag
        repo = Repo(os.getcwd())
        repo.create_tag(pypi_config["version_target"])

        # Push git tag to remote master
        origin = repo.remote()
        origin.push(pypi_config["version_target"])

    else:
        # PyPI publish likely failed
        print(
            f"Expected {pypi_config['package_name']}=={pypi_config['version_target']} "
            f"but found {pypi_config['package_name']}=={published_pypi_version}"
        )
        exit(1)


if __name__ == "__main__":
    createTag()
