#! /usr/bin/env python
import logging
import os
import shutil
from ansible_runner import Runner, RunnerConfig
import re

logger = logging.getLogger("AnsibleLogger")

def remove_ansi_escape_sequences(content):
    ansi_escape_regex = re.compile(r"\x1B(?:\[[0-?]*[ -/]*[@-~])")
    return ansi_escape_regex.sub("", content)

class CatAnsibleRunner:
    def __init__(self, private_data_dir=None, playbook=None, inventory=None, verbosity=5,artifact_dir=None, **kwargs):
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
        :param verbosity: Verbosity level.
        :type verbosity: int
        :param artifact_dir: Path to the artifact directory.
        :type artifact_dir: str
        :param extravars: Dictionary of extra variables.
        :type extravars: dict
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
            "extravars" not in kwargs
            or "ANSIBLE_PYTHON_INTERPRETER" not in kwargs["extravars"]
        ):
            kwargs["extravars"] = {
                "ANSIBLE_PYTHON_INTERPRETER": "$(which python)",
            }

        kwargs["private_data_dir"] = private_data_dir
        kwargs["playbook"] = playbook
        kwargs["inventory"] = inventory
        kwargs["artifact_dir"] = artifact_dir
        kwargs["verbosity"] = verbosity

        logger.info(
            f"Ansible Runner initialized with private data directory: {kwargs['private_data_dir']}"
        )
        logger.info(f"Ansible Runner initialized with playbook: {kwargs['playbook']}")
        logger.info(f"Ansible Runner initialized with inventory: {kwargs['inventory']}")
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

    def run(self, cleanup_events=True):
        """
        Run ansible playbook based on RunnerConfig.
        Returns:
            Runner: The ansible-runner Runner object.
        """

        r = Runner(config=self.runner_config)
        r.run()

        logger.info(f"Executed Playbook: {r.config.playbook}")
        logger.info(f"run RC: {r.rc}")
        logger.info(f"run output location: {r.stdout.name}")
        logger.info(f"run error location: {r.stderr.name}")
        logger.info(f"run failed events: {r.config.only_failed_event_data}")
        logger.info(f"Run result stats: {r.stats}")

        job_events_dir = r.stderr.name.replace("stderr", "job_events")

        if r.rc != 0:
            with open(r.stderr.name, "r") as f:
                error_content = remove_ansi_escape_sequences(f.read())
                logger.error(error_content)

            with open(r.stdout.name, "r") as f:
                output_content = remove_ansi_escape_sequences(f.read())
                logger.info(output_content)

        else:
            with open(r.stdout.name, "r") as f:
                output_content = remove_ansi_escape_sequences(f.read())
                logger.info(output_content)

        if cleanup_events:
            shutil.rmtree(job_events_dir, ignore_errors=True) #avoid errors if directory already does not exist.
            os.makedirs(job_events_dir, exist_ok=True) #Create directory if it does not exist.
        return r
if __name__ == "__main__":
    private_data_dir = "sda_fabric_sites_zones"
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    schema_file = "sda_fabric_sites_zones/schema/sda_fabric_sites_zones_schema.yml"
    playbook = "../catc_ansible_workflows/workflows/sda_fabric_sites_zones/playbook/sda_fabric_sites_zones_playbook.yml"
    data_file = "catc_configs/sites/california/site_sda_fabric_sites_zones.yml"
    inventory = "ansible_inventory/catalystcenter_inventory/hosts.yml"
    ar = CatAnsibleRunner(
        private_data_dir,
        playbook,
        inventory,
        extravars={"VARS_FILE_PATH": data_file}
    )
    status, return_code = ar.run()

    if status != "successful":
        logger.error(f"ANSIBLE: DNAC DISCOVERY FAILED\n{status}")
    else:
        logger.info(f"Result: ANSIBLE: DNAC DISCOVERY passed \n{status}")
