# Releasing CloudEvents SDK for Python

This repository is configured to automatically publish the corresponding [PyPI
package](https://pypi.org/project/cloudevents/) via GitHub Actions.

This git action assumes contributors have updated the proper modules
(e.g. [setup.py](setup.py)) to reflect the pypi version changes. It will
automatically build and deploy onto pypi using
[this pypi github action](https://github.com/pypa/gh-action-pypi-publish). This
action gets called on pushes to master (such as version branch's being merged
into master).

After a version update is merged, maintainers are expected to manually create a
corresponding tag/release.

Feel free to view [pypi-release.yml](.github/workflows/pypi-release.yml) for
more information.
