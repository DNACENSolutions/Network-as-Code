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
import re
import shutil
from pyats.easypy import runtime
from ansible_runner import Runner, RunnerConfig

exec_usecases = []
logger = logging.getLogger(__name__)

def remove_ansi_escape_sequences(content):
    ansi_escape_regex = re.compile(r"\x1B(?:\[[0-?]*[ -/]*[@-~])")
    return ansi_escape_regex.sub("", content)

class AnsibleRunner:
    def __init__(self, private_data_dir=None, playbook=None, inventory=None,artifact_dir=None, **kwargs):
        """
        Initializes the AnsibleRunner object.

        :param kwargs: Dictionary of arguments.
        :type kwargs: dict
        :param private_data_dir: Path to the private data directory.
        :type private_data_dir: str
        :param playbook: Path to the playbook from private_data_dir path.
        :type playbook: str
        :param inventory: Path to the inventory file from private_data_dir path.
        :type inventory: str
        :param extravars: Dictionary of extra variables, extravars will be used in playbook include vars.
        :type extravars: dict
        :param envvars: Dictionary of environment variables.
        :type envvars: dict
        :param tags: Comma-separated list of tags to run.
        :type tags: str
        """
        if not private_data_dir:
            raise ValueError("Missing private data directory argument")

        if not playbook:
            raise ValueError("Missing playbook argument")

        if not inventory:
            raise ValueError("Missing inventory argument")

        if (
            "envvars" not in kwargs
            or "ANSIBLE_PYTHON_INTERPRETER" not in kwargs["envvars"]
        ):
            kwargs["envvars"] = {
                "ANSIBLE_PYTHON_INTERPRETER": "$(which python)",
            }

        kwargs["private_data_dir"] = private_data_dir
        kwargs["playbook"] = playbook
        kwargs["inventory"] = inventory
        kwargs["artifact_dir"] = artifact_dir
        logger.info(
            f"Ansible Runner initialized with private data directory: {kwargs['private_data_dir']}"
        )
        logger.info(f"Ansible Runner initialized with playbook: {kwargs['playbook']}")
        logger.info(f"Ansible Runner initialized with inventory: {kwargs['inventory']}")
        logger.info(f"Ansible Runner initialized with envvars: {kwargs['envvars']}")
        logger.info(f"Ansible Runner initialized with extravars: {kwargs['extravars']}")
        logger.info(
            f"Ansible Runner initialized with artifact_dir: {kwargs['artifact_dir']}"
        )
        logger.info(
            f"Ansible Runner initialized with verbosity level: {kwargs['verbosity']}"
        )

        self.__setup_runner_config(**kwargs)

    def __setup_runner_config(self, **kwargs):
        """
        Sets up the RunnerConfig object.
        """
        self.runner_config = RunnerConfig(**kwargs)
        self.runner_config.prepare()

    def ansible_run(self, cleanup_events=True):
        """
        Run ansible playbook based on RunnerConfig
        Returns:
            tuple: (status: str, return_code: int)
        """

        r = Runner(config=self.runner_config)
        status, return_code = r.run()

        logger.info(f"Executed Playbook: {r.config.playbook}")
        logger.info(f"run RC: {r.rc}")
        logger.info(f"run output location: {r.stdout.name}")
        logger.info(f"run error location: {r.stderr.name}")
        logger.info(f"run failed events: {r.config.only_failed_event_data}")
        logger.info(f"Run result status {r.stats}")

        a = r.stderr.name.replace("stderr", "job_events")
        if not r.rc == 0:
            with open(r.stderr.name, "r") as f:
                html_content = remove_ansi_escape_sequences(f.read())
                logger.error(html_content)

            with open(r.stdout.name, "r") as f:
                html_content = remove_ansi_escape_sequences(f.read())
                logger.info(html_content)
        else:
            with open(r.stdout.name, "r") as f:
                html_content = remove_ansi_escape_sequences(f.read())
                logger.info(html_content)
        if cleanup_events:
            shutil.rmtree(a)
            os.mkdir(a)

        return r
    

def run_playbook(playbook_path, inventory_path, data_file, verbosity=4):
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
    inventory_path = os.path.abspath(inventory_path)
    logger.info(f"Running playbook: {playbook_path}, inventory: {inventory_path}, data_file: {data_file}")
    logger.info(f"Extra vars: {extra_vars}")
    r = AnsibleRunner(private_data_dir=private_data_dir, playbook=playbook, inventory=inventory_path, artifact_dir=runtime.directory, verbosity=verbosity, extravars=extra_vars)
    return r.ansible_run()

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
        if runtype == 'both':
            logger.info('Running both validation and execution')
            aetest.loop.mark(ValidateInputsTestcase, vc=exec_usecases)
            aetest.loop.mark(ExecuteAnsibleTestcase, uc=exec_usecases)
        elif runtype == 'validate':
            logger.info('Running only validation')
            aetest.loop.mark(ValidateInputsTestcase, vc=exec_usecases)
            aetest.loop.mark(ExecuteAnsibleTestcase, uc=["skip"])
        elif runtype == 'execute':
            logger.info('Running only execution')
            aetest.loop.mark(ExecuteAnsibleTestcase, uc=exec_usecases)
            aetest.loop.mark(ValidateInputsTestcase, vc=["skip"])
        else:
            logger.info('Skipping Execution as only validation is selected')
            aetest.loop.mark(ExecuteAnsibleTestcase, uc=["skip"])
            aetest.loop.mark(ValidateInputsTestcase, vc=["skip"])
class ValidateInputsTestcase(aetest.Testcase):
    @aetest.test
    def validate_usecase_inputs(self,vc,usecaseyaml,runtype):
        if vc == "skip":
            self.skipped('Skipping validation')
            return
        logger.info('Running usecase: {}'.format(vc))
        if vc not in usecaseyaml.keys():
            self.failed('Usecase {} not found in usecase set'.format(vc))

        playbooks_path_base = os.environ.get("ANSIBLE_PLAYBOOKS_PATH")
        if not playbooks_path_base:
            self.skip("Environment variable 'ANSIBLE_PLAYBOOKS_PATH' not set.")
        cfg_base_path = os.environ.get("CONFIG_FILES_BASE_PATH")
        if not cfg_base_path:
            self.skip("Environment variable 'CONFIG_FILES_BASE_PATH' not set.")

        schema_file = os.path.join(playbooks_path_base, usecaseyaml[vc]["schema_file"])
        playbook = os.path.join(playbooks_path_base, usecaseyaml[vc]["playbook"])
        data_file = os.path.join(cfg_base_path, usecaseyaml[vc]["data_file"])

        if runtype in ["validate", "both"]:
            try:
                schema = yamale.make_schema(schema_file)
                data = yamale.make_data(data_file)
                val_result = yamale.validate(schema, data)
                for res in val_result:
                    if not res.isValid():
                        self.failed(f"Schema validation failed for {vc}: {res.errors}\n Schema: {res.schema}\n Data: {res.data}")
                    else:
                        logger.info(f"Schema validation passed for {vc}, {schema_file}, {data_file}")
            except Exception as e:
                self.failed(f"Schema validation failed for {vc}: {e}")
        logger.info('Usecase: {}'.format(usecaseyaml[vc]))
        self.passed('Usecase {} passed'.format(vc))

class ExecuteAnsibleTestcase(aetest.Testcase):
    @aetest.test
    def run_usecase(self,uc,usecaseyaml,runtype, inventory_path, verbosity):
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
                result = run_playbook(playbook, inventory_path, data_file, verbosity)
                if result.rc != 0:
                    self.failed(f"Playbook execution failed for {uc}: {result.rc}")
                else:
                    logger.info(f"Playbook execution passed for {uc}, INV:{inventory_path} Playbook:{playbook}, Input:{data_file}")
            except Exception as e:
                self.failed(f"Playbook execution failed for {uc}: {e}")

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