#!/bin/bash
echo "Script name: $0"
echo "First argument: $1"
if [[ "$1" == "clean" ]]; then
    echo "Cleaning the virtual environment"
    rm -rf ./../venv-anisible
    rm -rf ./../catc_ansible_workflows
    rm -rf ./../ansible_logs/*
    rm -rf ./../catc_logs/*
    exit 0
fi
# check if $ contains python in it if so user $2 as python3 
# if not use python2
if [[ $1 == *python* ]]; then
    echo "Creating virtual environment with $1"
    $1 -m venv ./../venv-anisible --prompt=ansible-venv
    source ./../venv-anisible/bin/activate
    which python
    export ANSIBLE_PYTHON_INTERPRETER=$(which python)
elif [[ "$1" == "sourceonly" ]]; then
    echo "Activating the virtual environment"
    source ./../venv-anisible/bin/activate
    which python
    export ANSIBLE_PYTHON_INTERPRETER=$(which python)
else
    echo "Creating virtual environment with python"
    python3 -m venv ./../venv-anisible --prompt=ansible-venv
    source ./../venv-anisible/bin/activate
    which python
    export ANSIBLE_PYTHON_INTERPRETER=$(which python)
fi 
if [[ "$1" != "sourceonly" ]]; then
    #python3 -m venv ./../venv-anisible --prompt=ansible-venv
    python -m pip install --upgrade pip
    pip install --upgrade pip setuptools
    python -m pip install -r ./requirements.txt
    python -m pip install --upgrade dnacentersdk
    ansible-galaxy collection install cisco.dnac --force
fi
# check if the path ./../catc_ansible_workflows exists, if not clone the repo if exists then got to the dir and perform git pull
[ -d ./../catc_ansible_workflows ] || git clone https://github.com/cisco-en-programmability/catalyst-center-ansible-iac.git ./../catc_ansible_workflows
cd ./../catc_ansible_workflows
git pull
cd -
# check if the path ./../ansible_logs exists, if not create the dir
[ -d ./../ansible_logs ] || mkdir ./../ansible_logs
[ -d ./../catc_logs ] || mkdir ./../catc_logs
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export ANSIBLE_PLAYBOOKS_PATH=$(pwd)/../catc_ansible_workflows/workflows
export ANSIBLE_ROLES_PATH=$(pwd)/../catc_ansible_workflows/roles
export ANSIBLE_HOSTS_INVENTORY=$(pwd)/ansible_inventory/catalystcenter_inventory/hosts.yml
export ANSIBLE_CONFIG=$(pwd)/ansible.cfg
export ANSIBLE_LOG_PATH=$(pwd)/../ansible_logs/ansible.log
export ANSIBLE_LOG_DIR_PATH=$(pwd)/../ansible_logs
export CATC_LOG_DIR_PATH=$(pwd)/../catc_logs
export CATC_LOG_DIR=$(pwd)/../catc_logs/catalystcenter_logs.log
export ANSIBLE_DEBUG=True
export ANSIBLE_VERBOSITY=4
export ANSIBLE_STDOUT_CALLBACK=debug
#export ANSIBLE_FORCE_COLOR=true
#Assign current path as the base path for the config files
export CONFIG_FILES_BASE_PATH=$(pwd)
echo "Virtual environment created and activated successfully"
echo "Create you inventory file in the path: $(pwd)/ansible_inventory."
echo "Refer the sample file in the path: $(pwd)/ansible_inventory/catalystcenter_inventory_10.195.243.53/hosts.yml"

