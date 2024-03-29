# Releasing CloudEvents SDK for Python

This repository is configured to automatically publish the corresponding [PyPI
package](https://pypi.org/project/cloudevents/) and GitHub Tag via GitHub Actions.

To release a new CloudEvents SDK, contributors should bump `__version__` in
[cloudevents](cloudevents/__init__.py) to reflect the new release version. On merge, the action
will automatically build and release to PyPI using
[this PyPI GitHub Action](https://github.com/pypa/gh-action-pypi-publish). This
action gets called on all pushes to main (such as a version branch being merged
into main), but only releases a new version when the version number has changed. Note,
this action assumes pushes to main are version updates. Consequently,
[pypi-release.yml](.github/workflows/pypi-release.yml) will fail if you attempt to
push to main without updating `__version__` in
[cloudevents](cloudevents/__init__.py) so don't forget to do so.

After a version update is merged, the script [pypi_packaging.py](pypi_packaging.py)
will create a GitHub tag for the new cloudevents version using `__version__`.
The script fails if `__version__` and the local pypi version for
cloudevents are out of sync. For this reason, [pypi-release.yml](.github/workflows/pypi-release.yml)
first must upload the new cloudevents pypi package, and then download the recently updated pypi
cloudevents package for [pypi_packaging.py](pypi_packaging.py) not to fail.

View the GitHub workflow [pypi-release.yml](.github/workflows/pypi-release.yml) for
more information.
