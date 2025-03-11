# Example: ansible_job.py
# -------------------
#
#   a simple job file for the script above
# Author pawansi@cisco.com
#-----------------------------
import argparse
from pyats import aetest
from genie.testbed import load
#from pyats.topology import loader
from pyats.easypy import run
import requests
from pyats.easypy import runtime

SCRIPT_PATH = './job/ansible_test_script.py'
CONFIG_FILE = './job/ansible_test_script.py'
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest = 'testbed', 
                        type = load)

    parser.add_argument('--usecasefile', dest = 'usecasefile', 
                        type = str)
    parser.add_argument('--execute', dest = 'execute', 
                        type = str, default = 'all')
    
    parser.add_argument('--runtype', dest = 'runtype',
                        type = str, default = 'validate')
    
    parser.add_argument('--inventory', dest = 'inventory',
                        type = str, default = '../../ansible_inventory/catalystcenter_inventory/hosts.yml')
    #verbosity
    parser.add_argument('--verbosity', dest = 'verbosity',
                        type = int, default = 3)
    args, unknown = parser.parse_known_args()
    
    # run api launches a testscript as an individual task.
    run(testscript=SCRIPT_PATH, testbed=args.testbed, usecasefile=args.usecasefile, 
        execute=args.execute, runtype=args.runtype,  inventory_path=args.inventory,
        verbosity = args.verbosity)
    
    # Upload the results.json file to the server
    upload_results_to_iacdashboard()

def upload_results_to_iacdashboard():
    # Upload the results.json file to the server
    url = "http://172.23.241.202:8002/uploadfile/"
    result_dir = runtime.directory
    files = {'json_file': open(f'{result_dir}/results.json', 'rb')}
    response = requests.post(url, files=files)
    print(response.text)
    print("Results uploaded to IAC Dashboard")

