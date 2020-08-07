# Releasing CloudEvents SDK for Python

This repository is configured to automatically publish the corresponding [PyPI
package](https://pypi.org/project/cloudevents/) and GitHub Tag via GitHub Actions.

To release a new CloudEvents SDK, contributors should bump `pypi_config['version_target']` in
[pypi_packaging.py](pypi_packaging.py) to reflect the new release version. On merge, the action
will automatically build and release to PyPI using
[this PyPI GitHub Action](https://github.com/pypa/gh-action-pypi-publish). This
action gets called on all pushes to master (such as a version branch being merged
into master), but only releases a new version when the version number has changed. Note,
this action assumes pushes to master are version updates. Consequently,
[pypi-release.yml](.github/workflows/pypi-release.yml) will fail if you attempt to
push to master without updating `pypi_config['version_target']` in
[pypi_packaging.py](pypi_packaging.py) so don't forget to do so.

After a version update is merged, the script [pypi_packaging.py](pypi_packaging.py)
will create a GitHub tag for the new cloudevents version using `pypi_config['version_target']`.
The script fails if `pypi_config['version_target']` and the local pypi version for
cloudevents are out of sync. For this reason, (pypi-release.yml)(.github/workflows/pypi-release.yml)
first must upload the new cloudevents pypi package, and then download the recently updated pypi
cloudevents package for [pypi_packaging.py](pypi_packaging.py) not to fail.

View the GitHub workflow [pypi-release.yml](.github/workflows/pypi-release.yml) for
more information.
