#!/bin/bash

if [ ! -d venv ] ; then
    pyvenv-3.4 venv
fi

source venv/bin/activate

echo "installing from python/requirements.txt"
pip -q install -r python/requirements.txt

mkdir -p log


echo "running tests"
mkdir -p out
coverage run --rcfile=python/.coveragerc -m nose2 -s python --config python/unittest.cfg
coverage html --rcfile=python/.coveragerc

pep8 $(find python/ -name "*.py" -print) > out/pep8.log
python $(which pylint) --rcfile=python/pylint.cfg --output-format=parseable $(find python/ -name "*.py" -print) > out/pylint.log || exit 0
