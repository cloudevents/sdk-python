# Releasing CloudEvents SDK for Python

This repository is configured to automatically publish the corresponding [PyPI
package](https://pypi.org/project/cloudevents/) and GitHub Tag via GitHub Actions.

To release a new CloudEvents SDK, contributors should bump `__version__` in
`src/cloudevents/__init__.py` to reflect the new release version. On merge, the action
will automatically build and release to PyPI. This action gets called on all pushes to main
(such as a version branch being merged into main), but only releases a new version when the
version number has changed. Note, this action assumes pushes to main are version updates.
Consequently, the release workflow will fail if you attempt to push to main without updating
`__version__` in `src/cloudevents/__init__.py` so don't forget to do so.

After a version update is merged, a GitHub tag for the new cloudevents version is created
using `__version__`.

View the GitHub workflow [pypi-release.yml](.github/workflows/pypi-release.yml) for
more information.
