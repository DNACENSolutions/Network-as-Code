#!/bin/bash
python3 -m venv ./../venv-anisible --prompt=ansible-venv
source ./../venv-anisible/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r ./requirements.txt
ansible-galaxy collection install cisco.dnac --force
# check if the path ./../dnac_ansible_workflows exists, if not clone the repo if exists then got to the dir and perform git pull
[ -d ./../dnac_ansible_workflows ] || git clone https://github.com/DNACENSolutions/dnac_ansible_workflows.git ./../dnac_ansible_workflows
cd ./../dnac_ansible_workflows
git pull
cd -
# check if the path ./../ansible_logs exists, if not create the dir
[ -d ./../ansible_logs ] || mkdir ./../ansible_logs
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export ANSIBLE_PLAYBOOKS_PATH=./../dnac_ansible_workflows/workflows
export ANSIBLE_ROLES_PATH=./../dnac_ansible_workflows/roles
export ANSIBLE_HOSTS_INVENTORY=./ansible_inventory/catalystcenter_inventory_10.195.243.53/hosts.yml
export ANSIBLE_CONFIG=./ansible.cfg
export ANSIBLE_LOG_PATH=./../ansible_logs/ansible.log
export ANSIBLE_LOG_DIR_PATH=./../ansible_logs
export ANSIBLE_DEBUG=True
export ANSIBLE_VERBOSITY=4
export ANSIBLE_STDOUT_CALLBACK=debug
#Assign current path as the base path for the config files
export CONFIG_FILES_BASE_PATH=$(pwd)/catc_configs
#ANSIBLE_PLAYBOOKS_PATH = os.getenv('ANSIBLE_PLAYBOOKS_PATH', '/Users/pawansi/workspace/CatC_Configs/dnac_ansible_workflows/workflows/')
#CONFIG_FILES_BASE_PATH = os.getenv('CONFIG_FILES_BASE_PATH', '/Users/pawansi/workspace/CatC_Configs/CatalystCenter_Configurations/catc_configs/')
#ANSIBLE_HOSTS_INVENTORY = os.getenv('ANSIBLE_HOSTS_INVENTORY', '/Users/pawansi/workspace/CatC_Configs/CatalystCenter_Configurations/ansible_inventory/catalystcenter_inventory_10.195.243.53')
#ANSIBLE_LOG_DIR_PATH = os.getenv('ANSIBLE_LOG_DIR_PATH', '/Users/pawansi/workspace/CatC_Configs/ansible_logs/')