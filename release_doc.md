Release process
===============

Run tests on target brunch
--------------------------

Steps:

    tox

Cut off stable branch
---------------------

Steps:

    git checkout -b vX.X.X-stable
    git push origin vX.X.X-stable


Create GitHub tag
-----------------

Steps:

    Releases ---> Draft New Release
    Name: CloudEvents Python SDK version X.X.X stable release


Collect changes from previous version
-------------------------------------

Steps:

    git log --oneline --decorate


Build distribution package
--------------------------

Steps:

    PBR_VERSION=X.X.X python setup.py sdist bdist_wheel


Check install capability for the wheel
--------------------------------------

Steps:

    python3.7 -m venv .test_venv
    source .test_venv/bin/activate
    pip install dist/cloudevents-X.X.X-py3-none-any.whl


Submit release to PYPI
----------------------

Steps:

    twine upload dist/cloudevents-X.X.X-py3-none-any.whl

Verify install capability for the wheel
---------------------------------------

Steps:

    python3.7 -m venv .test_venv
    source .new_venv/bin/activate
    pip install cloudevents --upgrade
