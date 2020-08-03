# Releasing CloudEvents SDK for Python

This repository is configured to automatically publish the corresponding [PyPI
package](https://pypi.org/project/cloudevents/) via GitHub Actions.

To release a new CloudEvents SDK, contributors should bump the `version` in
[setup.py](setup.py)) to reflect the new release version. On merge, the action
will automatically build and release to PyPI using
[this PyPI GitHub Action](https://github.com/pypa/gh-action-pypi-publish). This
action gets called on all pushes to master (such as a version branch being merged
into master), but only releases a new version when the version number has changed.

After a version update is merged, maintainers are expected to manually create a
corresponding tag/release.

View the GitHub workflow [pypi-release.yml](.github/workflows/pypi-release.yml) for
more information.
