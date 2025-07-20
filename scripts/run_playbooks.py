import subprocess
import os
import sys
import yaml
import datetime
import argparse

# --- Utility for Colored Logging ---
class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def log_info(message):
    print(f"{Color.CYAN}{message}{Color.END}")

def log_success(message):
    print(f"{Color.GREEN}{Color.BOLD}{message} \U0001F44D{Color.END}")

def log_warning(message):
    print(f"{Color.YELLOW}Warning: {message}{Color.END}")

def log_error(message):
    print(f"{Color.RED}{Color.BOLD}Error: {message} \U0001F44E{Color.END}")
    
def log_step(message):
    print(f"\n{Color.PURPLE}====== {message} ======{Color.END}")

# --- Configuration Paths ---
ANSIBLE_PLAYBOOKS_PATH = os.getenv('ANSIBLE_PLAYBOOKS_PATH', os.path.join(os.getcwd(), '../catc_ansible_workflows/workflows/'))
CONFIG_FILES_BASE_PATH = os.getenv('CONFIG_FILES_BASE_PATH', os.getcwd())
ANSIBLE_HOSTS_INVENTORY_DIR = os.getenv('ANSIBLE_HOSTS_INVENTORY_DIR', os.path.join(os.getcwd(), 'ansible_inventory', 'catalystcenter_inventory'))
ANSIBLE_LOG_DIR_PATH = os.getenv('ANSIBLE_LOG_DIR_PATH', os.path.join(os.getcwd(), '../ansible_logs/'))
CATC_LOG_DIR_PATH = os.getenv('CATC_LOG_DIR_PATH', os.path.join(os.getcwd(), '../catc_logs/'))
USECASE_MAPS_DIR = os.getenv('USECASE_MAPS_DIR', 'usecase_maps')

# --- Core Functions ---

def load_usecase_data(yaml_files):
    """Loads use case data from a list of YAML files, preserving order and handling duplicates."""
    ordered_usecases = []
    usecase_counts = {}
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r') as f:
                # Use yaml.FullLoader to preserve order if available, otherwise safe_load
                try:
                    usecase_data = yaml.load(f, Loader=yaml.FullLoader)
                except AttributeError:
                    usecase_data = yaml.safe_load(f)

                if usecase_data:
                    for usecase, data in usecase_data.items():
                        original_usecase = usecase
                        if original_usecase in usecase_counts:
                            usecase_counts[original_usecase] += 1
                            usecase = f"{original_usecase}_{usecase_counts[original_usecase]}"
                            log_warning(f"Duplicate usecase '{original_usecase}' found. Renaming to '{usecase}'.")
                        else:
                            usecase_counts[original_usecase] = 0
                        
                        ordered_usecases.append((usecase, data))

            log_info(f"Successfully loaded use cases from: {os.path.basename(yaml_file)}")
        except FileNotFoundError:
            log_error(f"YAML file not found: {yaml_file}")
            return None
        except yaml.YAMLError as e:
            log_error(f"Error parsing YAML file '{yaml_file}': {e}")
            return None
    return ordered_usecases

def select_yaml_files(directory, prompt):
    """Lists YAML files and prompts the user to select one or more."""
    yaml_files = sorted([f for f in os.listdir(directory) if f.endswith((".yml", ".yaml"))])
    if not yaml_files:
        log_error(f"No YAML files found in {directory}")
        return None

    log_info(f"\nAvailable {prompt} files:")
    for i, file in enumerate(yaml_files):
        print(f"  {i+1}. {file}")

    while True:
        try:
            choice_str = input(f"\n{Color.BOLD}Select file(s) by number (e.g., '1' or '1,3'): {Color.END}")
            choices = [int(c.strip()) for c in choice_str.split(',')]
            selected_files = []
            valid_choices = True
            for choice in choices:
                if 1 <= choice <= len(yaml_files):
                    selected_files.append(os.path.join(directory, yaml_files[choice - 1]))
                else:
                    log_error(f"Choice '{choice}' is out of range.")
                    valid_choices = False
                    break
            if valid_choices:
                return selected_files
            else:
                log_warning("Please enter valid numbers from the list.")
        except ValueError:
            log_error("Invalid input. Please enter numbers separated by commas.")

def validate_schema(usecase_name, usecase_config):
    """Validates the data file against the schema for the given use case."""
    log_info(f"Validating schema for '{usecase_name}'...")
    config_file = os.path.join(ANSIBLE_PLAYBOOKS_PATH, usecase_config.get("schema_file", ""))
    data_file = os.path.join(CONFIG_FILES_BASE_PATH, usecase_config.get("data_file", ""))

    if not os.path.exists(config_file) or not os.path.exists(data_file):
        log_error(f"Schema or data file not found for '{usecase_name}'. Checked paths:\n- {config_file}\n- {data_file}")
        return False

    try:
        subprocess.run(["yamale", "-s", config_file, data_file], check=True, capture_output=True, text=True)
        log_success(f"Schema validation successful for {usecase_name}")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Schema validation failed for {usecase_name}:\n{e.stderr}")
        return False

def validate_inventory(inventory_file):
    """Validates the Ansible inventory file."""
    log_step("Validating Ansible Inventory")
    try:
        subprocess.run(["ansible-inventory", "-i", inventory_file, "--list"], check=True, capture_output=True)
        log_success("Inventory validation successful, proceeding with execution options")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Inventory validation failed: {e}\nPlease check the inventory file and try again.")
        return False

def execute_playbook(usecase_name, usecase_config, inventory_file, jenkins=False, verbose_level="v"):
    """Executes the Ansible playbook for the given use case."""
    log_step(f"Executing Playbook for: {usecase_name}")
    playbook = os.path.join(ANSIBLE_PLAYBOOKS_PATH, usecase_config["playbook"])
    data_file = os.path.join(CONFIG_FILES_BASE_PATH, usecase_config["data_file"])
    ansible_log_path = os.path.join(ANSIBLE_LOG_DIR_PATH, f"{usecase_name}_ansible.log")
    catalyst_center_log_file_path = os.path.join(CATC_LOG_DIR_PATH, f"{usecase_name}_catc.log")

    start_time = datetime.datetime.now()
    log_info(f"Playbook Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    cmd = [
        "ansible-playbook", "-i", inventory_file,
        "-e", f"VARS_FILE_PATH={data_file}",
        playbook,
        "-e", f"catalyst_center_log_file_path={catalyst_center_log_file_path}",
        f"-{verbose_level}"
    ]

    try:
        if jenkins:
            with open(os.path.join(ANSIBLE_LOG_DIR_PATH, "ansible_suite.sh"), 'a') as ansible_suite:
                ansible_suite.write(f'# --- {usecase_name} ---\n')
                ansible_suite.write(' '.join(cmd) + ' \n')
                ansible_suite.write('\n')
            log_success(f"Command for '{usecase_name}' added to ansible_suite.sh")
        else:
            log_info(f"Executing command: {' '.join(cmd)}")
            log_info(f"See log for details: {ansible_log_path}")
            with open(ansible_log_path, 'w') as log_file:
                subprocess.run(cmd, check=True, stdout=log_file, stderr=subprocess.STDOUT)
            log_success(f"Playbook execution completed for {usecase_name}")
    except subprocess.CalledProcessError as e:
        log_error(f"Playbook execution failed for {usecase_name}. See log for details.")
    finally:
        end_time = datetime.datetime.now()
        time_taken = end_time - start_time
        log_info(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')} | Duration: {time_taken}")
        log_info(f"Ansible Log: {ansible_log_path}")
        log_info(f"CatC Log: {catalyst_center_log_file_path}")

def run_main_logic():
    """Main logic for a single run of playbook selection and execution."""
    parser = argparse.ArgumentParser(
        description=f"{Color.BOLD}Run Catalyst Center Ansible playbooks with enhanced verbosity and suite management.{Color.END}",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("suitenames", nargs='*', default=None, help="Name(s) of the suite map file(s) to run (e.g., 'fabric.yml sdwan.yml')")
    parser.add_argument("-m", "--method", choices=["validate", "execute", "both"], default=None, help="Action to perform.")
    parser.add_argument("-u", "--usecases", nargs='*', default=None, help="List of specific use cases to run (or 'all').")
    parser.add_argument("-v", "--verbose", action="count", default=1, help="Increase output verbosity (-v, -vv, -vvv, -vvvv). Default is -v.")
    parser.add_argument("--jenkins", action="store_true", help="Enable Jenkins mode (writes commands to ansible_suite.sh)")
    args = parser.parse_args()

    verbose_level = "v" * args.verbose

    # --- Inventory Selection ---
    inventory_dir = os.getenv('ANSIBLE_HOSTS_INVENTORY_DIR', os.path.join(os.getcwd(), 'ansible_inventory', 'catalystcenter_inventory'))
    inventory_files = select_yaml_files(inventory_dir, "inventory")
    if not inventory_files:
        return
    inventory_file = inventory_files[0] # Use the first selected inventory
    if not validate_inventory(inventory_file):
        return

    # --- Usecase Loading ---
    log_step("Loading Usecase Maps")
    usecase_maps_dir = os.getenv('USECASE_MAPS_DIR', 'usecase_maps')
    ordered_usecases = None

    if args.suitenames:
        yaml_files = [os.path.join(usecase_maps_dir, s) for s in args.suitenames]
        ordered_usecases = load_usecase_data(yaml_files)
    else:  # Interactive mode
        selected_files = select_yaml_files(usecase_maps_dir, "use case map")
        if not selected_files:
            return
        ordered_usecases = load_usecase_data(selected_files)

    if not ordered_usecases:
        log_error("No use cases were loaded. Exiting.")
        return

    usecase_map = dict(ordered_usecases)
    usecase_names = [name for name, data in ordered_usecases]

    # --- Action and Usecase Selection ---
    method = args.method
    selected_usecases_names = []

    if args.usecases:
        if 'all' in [u.lower() for u in args.usecases]:
            selected_usecases_names = usecase_names
        else:
            selected_usecases_names = args.usecases
            invalid_usecases = set(selected_usecases_names) - set(usecase_names)
            if invalid_usecases:
                log_error(f"Invalid use case(s) provided: {', '.join(invalid_usecases)}")
                print("Available use cases are:", ", ".join(usecase_names))
                return
    
    if not method or not selected_usecases_names:
        # Interactive selection if not fully specified by args
        log_step("Select Action and Usecases")
        if not method:
            print("1. Validate")
            print("2. Execute")
            print("3. Validate and Execute")
            method_choice = input(f"{Color.BOLD}Select an option: {Color.END}")
            method = {"1": "validate", "2": "execute", "3": "both"}.get(method_choice)

        if not selected_usecases_names:
            for i, name in enumerate(usecase_names):
                print(f"  {i+1}. {name}")
            choice_str = input(f"{Color.BOLD}Select use cases (e.g., 'a' for all, '1', '1,3', '1-4'): {Color.END}")
            if choice_str.lower() == 'a':
                selected_usecases_names = usecase_names
            elif '-' in choice_str:
                try:
                    start, end = map(int, choice_str.split('-'))
                    selected_usecases_names = usecase_names[start - 1:end]
                except ValueError:
                    log_error("Invalid range format. Please use 'start-end'.")
                    return
            else:
                try:
                    choices = [int(c.strip()) for c in choice_str.split(',')]
                    selected_usecases_names = [usecase_names[c - 1] for c in choices if 1 <= c <= len(usecase_names)]
                except ValueError:
                    log_error("Invalid input. Please enter numbers separated by commas.")
                    return

    if not method or not selected_usecases_names:
        log_error("No method or use cases selected. Exiting.")
        return

    # --- Execution ---
    log_step(f"Running Method: '{method.upper()}' for {len(selected_usecases_names)} Usecase(s)")
    if args.jenkins:
        log_info("Jenkins mode enabled. Clearing and preparing 'ansible_suite.sh'.")
        with open(os.path.join(ANSIBLE_LOG_DIR_PATH, "ansible_suite.sh"), 'w') as f:
            f.write("#!/bin/bash\n\n")

    all_valid = True
    for usecase_name in selected_usecases_names:
        if method in ["validate", "both"]:
            if not validate_schema(usecase_name, usecase_map[usecase_name]):
                all_valid = False

    if not all_valid:
        log_error("Schema validation failed for one or more use cases. Halting execution.")
        return

    if method in ["execute", "both"]:
        for usecase_name in selected_usecases_names:
            execute_playbook(usecase_name, usecase_map[usecase_name], inventory_file, jenkins=args.jenkins, verbose_level=verbose_level)

    log_success("\nAll tasks completed!")

def main():
    """Main function to handle user input and loop for multiple executions."""
    while True:
        run_main_logic()
        
        while True:
            another_run = input(f"\n{Color.BOLD}Do you want to run another set of playbooks? (y/n): {Color.END}").lower()
            if another_run in ['y', 'n']:
                break
            log_warning("Invalid input. Please enter 'y' or 'n'.")

        if another_run == 'n':
            log_info("Exiting program.")
            break

if __name__ == "__main__":
    # Create log directories if they don't exist
    os.makedirs(ANSIBLE_LOG_DIR_PATH, exist_ok=True)
    os.makedirs(CATC_LOG_DIR_PATH, exist_ok=True)
    main()
