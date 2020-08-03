# Releasing CloudEvents SDK for Python

To properly release a new cloudevents version, we setup github actions for updating
repo's [PyPi package.](https://pypi.org/project/cloudevents/)

This git action assumes contributors have updated the proper modules
(e.g. [setup.py](setup.py)) to reflect the pypi version changes. It will
automatically build and deploy onto pypi using
[this pypi github action](https://github.com/pypa/gh-action-pypi-publish)

Feel free to view [pypi-release.yml](.github/workflows/pypi-release.yml) for
more information.
