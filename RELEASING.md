# Releasing CloudEvents SDK for Python

This repository is configured to automatically publish the corresponding [PyPI
package](https://pypi.org/project/cloudevents/) and GitHub Tag via GitHub Actions.

To release a new CloudEvents SDK, contributors should bump `__version__` in
`src/cloudevents/__init__.py` to reflect the new release version. On merge, the action
will automatically build and release to PyPI. This action gets called on all pushes to main
(such as a version branch being merged into main), but skips publishing and tagging when a
Git tag matching `__version__` already exists. Changes made after a release require a new
version number to be published.

After a version update is merged, a GitHub tag for the new cloudevents version is created
using `__version__`.
If publishing succeeds but tag creation fails, verify the published release and restore its
tag at the release commit before subsequent pushes; otherwise PyPI will reject the repeat
upload.

View the GitHub workflow [pypi-release.yml](.github/workflows/pypi-release.yml) for
more information.
