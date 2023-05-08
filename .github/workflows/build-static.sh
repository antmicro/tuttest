#!/bin/bash

# Builds tuttest command-line tool as a static binary

set -e

SCRIPT_DIR=$(dirname $(realpath $0))

cd $SCRIPT_DIR/../../

if [[ -n "$SKIP_DEPS_INSTALL" ]]
then
    echo "Skipping installation of static build dependencies"
else
    echo "Installing dependencies for static build..."
    apt -qqy update
    apt -qqy install patchelf build-essential python3-pip git zlib1g-dev python3-setuptools python3-venv python3-wheel

    git clone https://github.com/pyinstaller/pyinstaller.git

    cd pyinstaller/bootloader
    CC="gcc -no-pie" python3 waf configure all
    cd -

    cd pyinstaller
    pip3 install .
    cd -

    pip3 install staticx
fi

echo "Building the static binary for tuttest"

pip3 install .

pyinstaller --collect-all tuttest -F bin/tuttest
staticx dist/tuttest tuttest_static
chmod 755 tuttest_static
