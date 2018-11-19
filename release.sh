#!/usr/bin/env bash


git checkout -b v${CLOUDEVENTS_SDK_VERSION}-stable
git push origin v${CLOUDEVENTS_SDK_VERSION}-stable
PBR_VERSION=${CLOUDEVENTS_SDK_VERSION} python setup.py sdist bdist_wheel
twine upload dist/cloudevents-${CLOUDEVENTS_SDK_VERSIONN}*
git checkout master
