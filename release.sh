#!/usr/bin/env bash

# Fail fast and fail hard.
set -eo pipefail

# Check for our version
if [ -z "$CLOUDEVENTS_SDK_VERSION" ]; then
    echo "Need to set CLOUDEVENTS_SDK_VERSION"
    exit 1
fi

# Run tests on target branch
tox

# Cut off stable branch
git checkout -b v${CLOUDEVENTS_SDK_VERSION}-stable

# Create GitHub tag
git tag -a ${CLOUDEVENTS_SDK_VERSION} -m "${CLOUDEVENTS_SDK_VERSION}"

# Build distribution package
rm -rf dist
pip install -U setuptools wheel
python setup.py sdist bdist_wheel

# Submit relase to PyPI
pip install -U twine
twine upload dist/*

# Push the release to GitHub
git push origin v${CLOUDEVENTS_SDK_VERSION}-stable
git push --tags

# Switch back to the master branch
git checkout master
