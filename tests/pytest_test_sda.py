import pytest
import yaml
import yamale
import os
from ansible_runner import run

def load_yaml_file(file_path):
    """
    Helper function to load a YAML file.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        dict: The loaded YAML data.
    """
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def get_usecases_map(request):
    """
    Fixture to load the usecase map from the specified file.
    """
    print("Loading usecase map...")
    print(request.config)
    config_file = request.config.getoption("--MAPFILE")
    return load_yaml_file(config_file)

@pytest.fixture(scope="session")
def get_inventory(request):
    """
    Fixture to get the inventory path.
    """
    return request.config.getoption("--INV")

@pytest.fixture(scope="session")
def get_usecases(request):
    """
    Fixture to get the list of usecases to run.
    """
    return request.config.getoption("--UCS")

@pytest.fixture(scope="session")
def get_runtype(request):
    """
    Fixture to get the run type.
    """
    return request.config.getoption("--RUNTYPE")
def make_usecase_list(usecases_to_run, usecases_map):
    """
    Helper function to get the list of usecases to run.
    """
    return usecases_to_run.split(",") if usecases_to_run != "all" else list(usecases_map.keys())

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

def validate_input_data(schema_file, data_file):
    """
    Validates the input data against the schema using yamale.

    Args:
        schema_file (str): Path to the schema file.
        data_file (str): Path to the data file.

    Raises:
        yamale.yamale_error.YamaleError: If the data does not conform to the schema.
    """
    schema = yamale.make_schema(schema_file)
    data = yamale.make_data(data_file)
    val_result = yamale.validate(schema, data)
    return val_result

def test_catalyst_center_playbook(get_usecases_map, get_inventory, get_usecases, get_runtype):
    """
    Test Catalyst Center Ansible Playbooks.
    """
    playbooks_path_base = os.environ.get("ANSIBLE_PLAYBOOKS_PATH")
    if not playbooks_path_base:
        pytest.skip("Environment variable 'ANSIBLE_PLAYBOOKS_PATH' not set.")
    cfg_base_path = os.environ.get("CONFIG_FILES_BASE_PATH")
    if not cfg_base_path:
        pytest.skip("Environment variable 'CONFIG_FILES_BASE_PATH' not set.")

    usecases_map = get_usecases_map
    inventory_path = get_inventory
    usecases_to_run = make_usecase_list(get_usecases, usecases_map)
    runtype = get_runtype

    for usecase_name in usecases_to_run:
        print(f"Processing usecase: {usecase_name}")
        # Create a new test case for each usecase
        @pytest.mark.parametrize("usecase_data", [usecases_map.get(usecase_name)])
        def test_usecase(usecase_data):  # Define a new inner test function
            print(f"Running test for usecase: {usecase_name}")
            if "schema_file" not in usecase_data.keys():
                pytest.fail(f"Schema file not found for usecase: {usecase_name}")
            if "playbook" not in usecase_data.keys():
                pytest.fail(f"Playbook not found for usecase: {usecase_name}")
            if "data_file" not in usecase_data.keys():
                pytest.fail(f"Data file not found for usecase: {usecase_name}")

            schema_file = os.path.join(playbooks_path_base, usecase_data["schema_file"])
            playbook = os.path.join(playbooks_path_base, usecase_data["playbook"])
            data_file = os.path.join(cfg_base_path, usecase_data["data_file"])

            if runtype in ["validate", "both"]:
                try:
                    print(f"Validating input data for usecase: {usecase_name}")
                    print(f"Schema file: {schema_file}")
                    print(f"Data file: {data_file}")
                    val_result = validate_input_data(schema_file, data_file)
                    print(f"Schema validation result for {usecase_name}: {val_result}")
                    for res in val_result:
                        assert res.isValid(), f"Schema validation failed for {usecase_name}: {res.errors}\n Schema: {res.schema}\n Data: {res.data}"
                except yamale.yamale_error.YamaleError as e:
                    pytest.fail(f"Schema validation failed for {usecase_name}: {e}")

            if runtype in ["execute", "both"]:
                try:
                    result = run_playbook(playbook, inventory_path, data_file)
                    assert result.status == "successful", f"Playbook execution failed for {usecase_name}: {result.rc}"
                except Exception as e:
                    pytest.fail(f"Playbook execution failed for {usecase_name}: {e}")

            print(f"Successfully processed usecase: {usecase_name}")
        # Call the test_usecase function with the usecase_data
        print(f"Calling test_usecase for usecase: {usecases_map.get(usecase_name)}")
        test_usecase(usecases_map.get(usecase_name)) 
        
