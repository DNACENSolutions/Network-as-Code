# Example
# -------
#
#   ansible_test_script.py --testbed testbed.yaml --usecasefile usecases.yaml
#   pyats run job ansible_job.py --testbed testbed.yaml --usecasefile usecases.yaml --execute usecase1,usecase2 --runtype validate --inventory inventory.yml
from pyats import aetest
import yaml
import logging
import yamale
import os
from ansible_runner import run

exec_usecases = []
logger = logging.getLogger(__name__)

def run_playbook(playbook_path, inventory_path, data_file, verbosity=1):
    """
    Helper function to run an Ansible playbook using ansible-runner.

    Args:
        playbook_path (str): Path to the playbook.
        inventory_path (str): Path to the inventory file.
        data_file (str): Path to the data file.

    Returns:
        ansible_runner.runner.Runner: The Ansible runner object.
    """
    # Construct the private data dir path
    private_data_dir = os.path.dirname(playbook_path)
    playbook = playbook_path.split("/")[-1]
    extra_vars = {}
    extra_vars['VARS_FILE_PATH'] = os.path.abspath(data_file)
    result = run(
        private_data_dir=private_data_dir,
        playbook=playbook,
        inventory=inventory_path,
        extravars=extra_vars,
        #extravars=load_yaml_file(data_file),  # Pass data file as extra variables
        verbosity = verbosity
    )
    return result

class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def setup(self,testbed,usecasefile,execute,runtype):
        # add them to testscript parameters
        logger.info('Setting up testbed and usecases')
        logger.info('Testbed: {}'.format(testbed))
        logger.info('Usecases: {}'.format(usecasefile))
        if usecasefile is None:
            print(f"Error reading use case data from {usecasefile}")
            self.error('Error reading use case data from {}'.format(usecasefile))
        with open(usecasefile, 'r') as file:
            usecaseyaml = yaml.safe_load(file)
        if usecaseyaml is None or not usecaseyaml:
            print(f"Error reading use case data from {usecasefile}")
            self.error('Error reading use case data from {}'.format(usecasefile))
        usecases = usecaseyaml.keys()
        self.parent.parameters['usecaseyaml'] = usecaseyaml
        logger.info('Usecases: {}'.format(usecases))
        if execute is None:
            print(f"Error reading execute data from {execute}")
            self.error('Error reading execute data from {}'.format(execute))
        if execute == 'all':
            exec_usecases = list(usecases)
        else:
            exec_usecases = execute.split(',')
        logger.info('\nExecuting usecases: {}'.format(exec_usecases))
        self.parent.parameters['exec_usecases'] = exec_usecases
        if runtype in ["validate", "both"]:
            aetest.loop.mark(ValidateInputsTestcase, uc=exec_usecases)
        else:
            logger.info('Skipping Validation as only execution is selected')
            aetest.loop.mark(ValidateInputsTestcase, uc=["skip"])
        if runtype in ["execute", "both"]:
            aetest.loop.mark(ExecuteAnsibleTestcase, uc=exec_usecases)
        else:
            logger.info('Skipping Execution as only validation is selected')
            aetest.loop.mark(ExecuteAnsibleTestcase, uc=["skip"])

class ValidateInputsTestcase(aetest.Testcase):
    @aetest.test
    def validate_usecase_inputs(self,uc,usecaseyaml,runtype, inventory_path):
        if uc == "skip":
            self.skipped('Skipping validation')
            return
        logger.info('Running usecase: {}'.format(uc))
        if uc not in usecaseyaml.keys():
            self.failed('Usecase {} not found in usecase set'.format(uc))

        playbooks_path_base = os.environ.get("ANSIBLE_PLAYBOOKS_PATH")
        if not playbooks_path_base:
            self.skip("Environment variable 'ANSIBLE_PLAYBOOKS_PATH' not set.")
        cfg_base_path = os.environ.get("CONFIG_FILES_BASE_PATH")
        if not cfg_base_path:
            self.skip("Environment variable 'CONFIG_FILES_BASE_PATH' not set.")

        schema_file = os.path.join(playbooks_path_base, usecaseyaml[uc]["schema_file"])
        playbook = os.path.join(playbooks_path_base, usecaseyaml[uc]["playbook"])
        data_file = os.path.join(cfg_base_path, usecaseyaml[uc]["data_file"])
        if runtype in ["validate", "both"]:
            try:
                schema = yamale.make_schema(schema_file)
                data = yamale.make_data(data_file)
                val_result = yamale.validate(schema, data)
                for res in val_result:
                    if not res.isValid():
                        self.fail(f"Schema validation failed for {uc}: {res.errors}\n Schema: {res.schema}\n Data: {res.data}")
                    else:
                        logger.info(f"Schema validation passed for {uc}, {schema_file}, {data_file}")
            except Exception as e:
                self.fail(f"Schema validation failed for {uc}: {e}")
        logger.info('Usecase: {}'.format(usecaseyaml[uc]))
        self.passed('Usecase {} passed'.format(uc))

class ExecuteAnsibleTestcase(aetest.Testcase):
    @aetest.test
    def run_usecase(self,uc,usecaseyaml,runtype, inventory_path):
        if uc == "skip":
            self.skipped('Skipping execution')
        logger.info('Running usecase: {}'.format(uc))
        if uc not in usecaseyaml.keys():
            self.failed('Usecase {} not found in usecase set'.format(uc))

        playbooks_path_base = os.environ.get("ANSIBLE_PLAYBOOKS_PATH")
        if not playbooks_path_base:
            self.skip("Environment variable 'ANSIBLE_PLAYBOOKS_PATH' not set.")
        cfg_base_path = os.environ.get("CONFIG_FILES_BASE_PATH")
        if not cfg_base_path:
            self.skip("Environment variable 'CONFIG_FILES_BASE_PATH' not set.")

        playbook = os.path.join(playbooks_path_base, usecaseyaml[uc]["playbook"])
        data_file = os.path.join(cfg_base_path, usecaseyaml[uc]["data_file"])
        if runtype in ["execute", "both"]:
            try:
                result = run_playbook(playbook, inventory_path, data_file)
                if result.rc != 0:
                    self.fail(f"Playbook execution failed for {uc}: {result.rc}")
                else:
                    logger.info(f"Playbook execution passed for {uc}, INV:{inventory_path} Playbook:{playbook}, Input:{data_file}")
            except Exception as e:
                self.fail(f"Playbook execution failed for {uc}: {e}")

        logger.info('Usecase: {}'.format(usecaseyaml[uc]))
        self.passed('Usecase {} passed'.format(uc))

class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect(self):
        logger.info ('Closing connections to devices')

if __name__ == '__main__':
    import argparse
    from pyats.topology import loader
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest = 'testbed',
                        type = loader.load)
    parser.add_argument('--usecases', dest = 'usecases', 
                        type = yaml.safe_load)
    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))