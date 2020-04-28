# Release process

## Run tests on target branch

Steps:

    tox

## Cut off stable branch

Steps:

    git checkout -b vX.X.X-stable


## Create GitHub tag

Steps:

    git tag -a X.X.X -m "X.X.X"


## Build distribution package

Steps:

    rm -rf dist
    pip install -U setuptools wheel
    python setup.py sdist bdist_wheel


## Check install capability for the wheel

Steps:

    python3.7 -m venv .test_venv
    source .test_venv/bin/activate
    pip install dist/cloudevents-X.X.X-py3-none-any.whl


## Submit release to PyPI

Steps:

    pip install -U twine
    twine upload dist/*


## Push the release to GitHub

Steps:

    git push origin vX.X.X-stable
    git push --tags


## Verify install capability for the wheel

Steps:

    python3.7 -m venv .test_venv
    source .new_venv/bin/activate
    pip install cloudevents --upgrade
