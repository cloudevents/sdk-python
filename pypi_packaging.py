import codecs

import pkg_resources
import os


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


# FORMAT: 1.x.x
pypi_config = {
    "version_target": get_version("cloudevents/__init__.py"),
    "package_name": "cloudevents",
}


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
