#!/bin/bash
python3 -m venv ./../venv-anisible --prompt=ansible-venv
source ./../venv-anisible/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r ./requirements.txt
ansible-galaxy collection install cisco.dnac --force
git clone https://github.com/DNACENSolutions/dnac_ansible_workflows.git ./../dnac_ansible_workflows
deactivate



