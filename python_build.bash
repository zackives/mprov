#!/bin/bash

OUTPUT_DIR="pennprov_python_client"

rm -fr build dist pennprov.egg-info

python setup.py sdist
python setup.py bdist_wheel --universal
