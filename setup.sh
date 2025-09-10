#!/bin/bash

show_help() {
    echo ""
    echo "Usage: $0 [install python_interpreter|sourceonly|clean|-h|--help]"
    echo ""
    echo "Options:"
    echo "  install python_interpreter   Install a new virtual environment with the specified python (e.g. python3.11)."
    echo "  sourceonly                   Only activate (source) the existing virtual environment."
    echo "  clean                        Remove the virtual environment, logs, and workflows."
    echo "  -h, --help                   Show this help message and exit."
    echo ""
    echo "Examples:"
    echo "  $0 install python3.11        # Create venv with python3.11"
    echo "  $0 sourceonly                # Source existing venv"
    echo "  $0 clean                     # Remove venv, logs, and workflows"
    echo ""
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

echo "Script name: $0"
echo "Arguments: $*"

if [[ "$1" == "clean" ]]; then
    echo "Cleaning the virtual environment"
    rm -rf ./../venv-anisible
    rm -rf ./../catc_ansible_workflows
    rm -rf ./../ansible_logs/*
    rm -rf ./../catc_logs/*
    exit 0
fi

if [[ "$1" == "install" ]]; then
    if [[ -z "$2" || "$2" != python* ]]; then
        echo "Error: Please specify the python interpreter after 'install'."
        echo "Example: $0 install python3.11"
        exit 1
    fi
    if [[ -d ./../venv-anisible ]]; then
        read -p "A virtual environment already exists. Overwrite? [y/N]: " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            echo "Aborting installation."
            exit 1
        fi
        rm -rf ./../venv-anisible
    fi
    echo "Creating virtual environment with $2"
    $2 -m venv ./../venv-anisible --prompt=ansible-venv
    source ./../venv-anisible/bin/activate
    export ANSIBLE_PYTHON_INTERPRETER=$(which python)
    python -m pip install --upgrade pip
    pip install --upgrade pip setuptools
    python -m pip install -r ./requirements.txt
    python -m pip install --upgrade dnacentersdk
    ansible-galaxy collection install cisco.dnac --force
elif [[ "$1" == "sourceonly" ]]; then
    if [[ ! -d ./../venv-anisible ]]; then
        echo "No virtual environment found to source."
        exit 1
    fi
    echo "Activating the virtual environment"
    source ./../venv-anisible/bin/activate
    export ANSIBLE_PYTHON_INTERPRETER=$(which python)
else
    echo "Error: Invalid usage."
    show_help
    exit 1
fi

[ -d ./../catc_ansible_workflows ] || git clone https://github.com/cisco-en-programmability/catalyst-center-ansible-iac.git ./../catc_ansible_workflows
cd ./../catc_ansible_workflows
git pull
cd -
touch ~/.vault_pass.txt
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
export CONFIG_FILES_BASE_PATH=$(pwd)
export ANSIBLE_PYTHON_INTERPRETER=$(which python)
echo "Virtual environment setup complete."
echo "Create your inventory file in the path: $(pwd)/ansible_inventory."
echo "Refer the sample file in the path: $(pwd)/ansible_inventory/catalystcenter_inventory_10.195.243.53/hosts.yml"