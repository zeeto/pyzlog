#!/bin/bash
#

source ~/.bashrc

if [ ! -d $WORKON_HOME/pyzlog ]; then
    mkdir -p $WORKON_HOME
    cd $WORKON_HOME
    virtualenv pyzlog
fi

workon-pyzlog

cd /vagrant
pip install -U setuptools
pip install -r requirements_dev.txt
