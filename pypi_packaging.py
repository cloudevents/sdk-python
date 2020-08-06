from importlib.metadata import version
from git import Repo
import os


# FORMAT: 1.x.x
_LOCAL_PYPI_VERSION="1.0.0"

def createTag():
    # metadata.version only works on python3.8
    # Make sure to install most updated version of package 
    published_pypi_version = version('cloudevents')

    # Check pypi and local package version match
    if _LOCAL_PYPI_VERSION == published_pypi_version:
        # Create tag
        repo = Repo(os.getcwd())
        repo.create_tag(_LOCAL_PYPI_VERSION)

        # Push tag to origin master
        origin = repo.remote()
        origin.push(_LOCAL_PYPI_VERSION)
    else:
        # PyPI publish likely failed
        exit(1)


if __name__ == '__main__':
    createTag()

