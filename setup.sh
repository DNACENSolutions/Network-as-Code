#!/bin/bash
python3 -m venv ./../venv-anisible --prompt=ansible-venv
source ./../venv-anisible/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r ./requirements.txt
python3 -m pip install --upgrade dnacentersdk
ansible-galaxy collection install cisco.dnac --force
# check if the path ./../catc_ansible_workflows exists, if not clone the repo if exists then got to the dir and perform git pull
[ -d ./../catc_ansible_workflows ] || git clone https://github.com/cisco-en-programmability/catalyst-center-ansible-iac.git ./../catc_ansible_workflows
cd ./../catc_ansible_workflows
git pull
cd -
# check if the path ./../ansible_logs exists, if not create the dir
[ -d ./../ansible_logs ] || mkdir ./../ansible_logs
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export ANSIBLE_PLAYBOOKS_PATH=$(pwd)/../catc_ansible_workflows/workflows
export ANSIBLE_ROLES_PATH=$(pwd)/../catc_ansible_workflows/roles
export ANSIBLE_HOSTS_INVENTORY=$(pwd)/ansible_inventory/catalystcenter_inventory_10.195.243.53/hosts.yml
export ANSIBLE_CONFIG=$(pwd)/ansible.cfg
export ANSIBLE_LOG_PATH=$(pwd)/../ansible_logs/ansible.log
export ANSIBLE_LOG_DIR_PATH=$(pwd)/../ansible_logs
export CATC_LOG_DIR=$(pwd)/../catc_logs/catalystcenter_logs.log
export ANSIBLE_DEBUG=True
export ANSIBLE_VERBOSITY=4
export ANSIBLE_STDOUT_CALLBACK=debug
export ANSIBLE_FORCE_COLOR=true
#Assign current path as the base path for the config files
export CONFIG_FILES_BASE_PATH=$(pwd)/catc_configs
echo "Virtual environment created and activated successfully"
echo "Create you inventory file in the path: $(pwd)/ansible_inventory."
echo "Refer the sample file in the path: $(pwd)/ansible_inventory/catalystcenter_inventory_10.195.243.53/hosts.yml"
