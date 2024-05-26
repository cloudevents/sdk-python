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

import codecs
import os
import pathlib

from setuptools import find_packages, setup


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


# FORMAT: 1.x.x
pypi_config = {
    "version_target": get_version("cloudevents/__init__.py"),
    "package_name": "cloudevents",
}

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

if __name__ == "__main__":
    setup(
        name=pypi_config["package_name"],
        summary="CloudEvents Python SDK",
        long_description_content_type="text/markdown",
        long_description=long_description,
        description="CloudEvents Python SDK",
        url="https://github.com/cloudevents/sdk-python",
        author="The Cloud Events Contributors",
        author_email="cncfcloudevents@gmail.com",
        home_page="https://cloudevents.io",
        classifiers=[
            "Intended Audience :: Information Technology",
            "Intended Audience :: System Administrators",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "Development Status :: 5 - Production/Stable",
            "Operating System :: OS Independent",
            "Natural Language :: English",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Typing :: Typed",
        ],
        keywords="CloudEvents Eventing Serverless",
        license="https://www.apache.org/licenses/LICENSE-2.0",
        license_file="LICENSE",
        packages=find_packages(exclude=["cloudevents.tests"]),
        include_package_data=True,
        version=pypi_config["version_target"],
        install_requires=["deprecation>=2.0,<3.0"],
        extras_require={"pydantic": "pydantic>=1.0.0,<3.0"},
        zip_safe=True,
    )
