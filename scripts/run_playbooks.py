import subprocess
import os
import sys
import yaml
import datetime
import argparse
# Define the base path for Ansible playbooks and configuration files
# Use os.path.join for robustness and os.getcwd() for current working directory
ANSIBLE_PLAYBOOKS_PATH = os.getenv('ANSIBLE_PLAYBOOKS_PATH', os.path.join(os.getcwd(), '../catc_ansible_workflows/workflows/'))
CONFIG_FILES_BASE_PATH = os.getenv('CONFIG_FILES_BASE_PATH', os.getcwd())
ANSIBLE_HOSTS_INVENTORY_DIR = os.getenv('ANSIBLE_HOSTS_INVENTORY_DIR', os.path.join(os.getcwd(), 'ansible_inventory', 'catalystcenter_inventory'))
ANSIBLE_LOG_DIR_PATH = os.getenv('ANSIBLE_LOG_DIR_PATH', os.path.join(os.getcwd(), '../ansible_logs/'))
CATC_LOG_DIR_PATH = os.getenv('CATC_LOG_DIR_PATH', os.path.join(os.getcwd(), '../catc_logs/'))
USECASE_MAPS_DIR = os.getenv('USECASE_MAPS_DIR', 'usecase_maps') # Make usecase maps dir configurable

# Function to read usecase data from a YAML file
def read_usecase_data(yaml_file):
    """Reads use case data from the specified YAML file."""
    try:
        with open(yaml_file, 'r') as f:
            usecase_data = yaml.safe_load(f)
        return usecase_data
    except FileNotFoundError:
        print(f"Error: YAML file not found: {yaml_file}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None

def strip_yaml_values(data):
    """
    Recursively traverses a YAML data structure (dict or list)
    and strips leading/trailing whitespace from all string values.
    """
    if isinstance(data, dict):
        # If it's a dictionary, apply stripping to each value
        return {key: strip_yaml_values(value) for key, value in data.items()}
    elif isinstance(data, list):
        # If it's a list, apply stripping to each item
        return [strip_yaml_values(item) for item in data]
    elif isinstance(data, str):
        # If it's a string, strip whitespace
        return data.strip()
    else:
        # For any other data type (int, float, bool, None), return as is
        return data

# Option 1: Modify read_and_strip_yaml to just return stripped data
def read_and_strip_yaml(yaml_file):
    """
    Reads a YAML file and strips leading/trailing whitespace from all string values.
    Returns the stripped data.
    """
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            yaml_content = yaml.load(f, Loader=yaml.SafeLoader)
            print(f"Successfully read and parsed '{yaml_file}'.")
    except FileNotFoundError:
        print(f"Error: Input file '{yaml_file}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error: Could not parse YAML file '{yaml_file}'.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}", file=sys.stderr)
        return None

    if yaml_content is None:
        print("Input YAML file is empty or contains only comments.")
        return None
    else:
        print("Processing YAML content...")
        processed_content = strip_yaml_values(yaml_content)
        print("YAML content processed.")
        return processed_content

# Option 2: Keep read_usecase_data for simple reading and add a separate strip_and_write function
def strip_and_write_yaml(data, output_yaml_file):
    """
    Strips leading/trailing whitespace from string values in data and writes to a YAML file.
    """
    try:
        processed_content = strip_yaml_values(data)
        with open(output_yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(processed_content, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"Successfully wrote processed content to '{output_yaml_file}'.")
    except FileNotFoundError:
        print(f"Error: Output file '{output_yaml_file}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error: Could not write to YAML file '{output_yaml_file}'.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred while writing the file: {e}", file=sys.stderr)
        return None
def select_yaml_file(directory, prompt):
    """Lists YAML files in a directory and prompts the user to select one."""
    yaml_files = [f for f in os.listdir(directory) if f.endswith(".yml")]
    if not yaml_files:
        print(f"No YAML files found in {directory}")
        return None

    print(f"\nAvailable {prompt} files:")
    for i, file in enumerate(yaml_files):
        print(f"{i+1}. {file}")

    while True:
        try:
            choice = int(input(f"\nSelect a {prompt} file by entering its number: "))
            if 1 <= choice <= len(yaml_files):
                return os.path.join(directory, yaml_files[choice - 1])
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def validate_schema(usecase_name, usecase_data):
    """Validates the data file against the schema for the given use case."""
    config_file = os.path.join(ANSIBLE_PLAYBOOKS_PATH, usecase_data[usecase_name]["schema_file"])
    data_file = os.path.join(CONFIG_FILES_BASE_PATH, usecase_data[usecase_name]["data_file"])
    try:
        subprocess.run(["yamale", "-s", config_file, data_file], check=True)
        print(f"Schema validation successful for {usecase_name} \U0001F44D ")
    except subprocess.CalledProcessError as e:
        print(f"Schema validation failed for {usecase_name}: {e} \U0001F44E ")

def validate_inventory(inventory_file):
    """Validates the Ansible inventory file."""
    try:
        subprocess.run(["ansible-inventory", "-i", inventory_file, "--list"], check=True)
        print("Inventory validation successful, proceeding with execution options \U0001F44D ")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Inventory validation failed: {e} \U0001F44E ")
        print("Please check the inventory file and try again.")
        return False

def execute_playbook(usecase_name, usecase_data, inventory_file, jenkins=False, verbose_level="vvvv"):
    """Executes the Ansible playbook for the given use case."""
    playbook = os.path.join(ANSIBLE_PLAYBOOKS_PATH, usecase_data[usecase_name]["playbook"])
    data_file = os.path.join(CONFIG_FILES_BASE_PATH, usecase_data[usecase_name]["data_file"])
    ansible_log_path = os.path.join(ANSIBLE_LOG_DIR_PATH, f"{usecase_name}_ansible.log")
    catalyst_center_log_file_path = os.path.join(CATC_LOG_DIR_PATH, f"{usecase_name}_catc.log")
    #os.system(f'export catalyst_center_log_file_path={catalyst_center_log_file_path}')
    # Read Current time as start time
    print(f"Executing playbook for {usecase_name}...")
    start_time = datetime.datetime.now()
    print(f"Playbooks Start time: {start_time}")
    try:
        cmd = [
            "ansible-playbook",
            "-i", inventory_file,
            "-e", f"VARS_FILE_PATH={data_file}",
            playbook,
            "-e", f"catalyst_center_log_file_path={catalyst_center_log_file_path}",
            f"-{verbose_level}"
        ]
        if jenkins:
            with open(f"{ANSIBLE_LOG_DIR_PATH}/ansible_suite.sh", 'a') as ansible_suite:
                #ansible_suite.write(f'#!/bin/bash\n')
                #ansible_suite.write(f'export catalyst_center_log_file_path={catalyst_center_log_file_path}\n')
                ansible_suite.write(f'ansible-playbook -i {ANSIBLE_HOSTS_INVENTORY} {playbook} --e VARS_FILE_PATH={data_file} --e catalyst_center_log_file_path={catalyst_center_log_file_path} -{verbose_level} \n')
                #| tee {ansible_log_path} \n\n')
                print("Ansible playbook command added to ansible_suite.sh, will be launched from shell script.")
        else:
            with open(ansible_log_path, 'w') as log_file:
                print(f"Executing playbook command: {cmd} \n")
                subprocess.run(cmd, check=True, stdout=log_file, stderr=subprocess.STDOUT)
            print(f"Playbook execution successful for {usecase_name} ! \U0001F44D")
    except subprocess.CalledProcessError as e:
        print(f"Playbook execution failed for {usecase_name}: {e} !! \U0001F44E")
    # Read Current time as end time
    end_time = datetime.datetime.now()
    # Calculate the time taken to execute the playbook
    time_taken = end_time - start_time
    print(f"Playbook execution time: {time_taken}")
    print(f"End time: {end_time}")
    print("Check the logs for more details.")
    print(f"Ansible Logs dir: {ansible_log_path}")
    print(f"CatC Logs dir: {catalyst_center_log_file_path}")

def main():
    """Main function to handle user input and execute actions."""
    parser = argparse.ArgumentParser(description="Run Catalyst Center Ansible playbooks.")
    parser.add_argument("suitename", nargs='?', default=None, help="Name of the suite to run (e.g., 'fabric', 'sdwan')")
    parser.add_argument("method", choices=["validate", "execute", "both"], nargs='?', default=None, help="Action to perform: 'validate', 'execute', or 'both'")
    parser.add_argument("usecases", nargs='*', default=None, help="List of use cases to run (or 'all')")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument("--jenkins", action="store_true", help="Enable Jenkins mode (writes to ansible_suite.sh)")
    args = parser.parse_args()

    verbose_level = "vvvv" if args.verbose else "v"

    # Determine inventory file
    ANSIBLE_HOSTS_INVENTORY_DIR = os.getenv('ANSIBLE_HOSTS_INVENTORY_DIR', os.path.join(os.getcwd(), 'ansible_inventory', 'catalystcenter_inventory'))
    ANSIBLE_HOSTS_INVENTORY_FILE = select_yaml_file(ANSIBLE_HOSTS_INVENTORY_DIR, "inventory")
    if not ANSIBLE_HOSTS_INVENTORY_FILE:
        return # Exit if no inventory file is selected
    validate_inventory(ANSIBLE_HOSTS_INVENTORY_FILE)
    # Determine use case map file and use cases
    usecase_maps_dir = os.getenv('USECASE_MAPS_DIR', 'usecase_maps') # Make directory configurable
    usecase_data = None
    selected_usecases = []

    if args.suitename and args.method:
        # CLI arguments provided
        yaml_file = os.path.join(usecase_maps_dir, args.suitename)
        usecase_data = read_usecase_data(yaml_file)
        if usecase_data is None:
            print(f"Error reading use case data from {yaml_file}")
            return

        if args.usecases and args.usecases[0].lower() == "all":
            selected_usecases = list(usecase_data.keys())
        elif args.usecases:
            selected_usecases = args.usecases
            # Validate provided use cases
            invalid_usecases = set(selected_usecases) - set(usecase_data.keys())
            if invalid_usecases:
                print(f"Error: Invalid use case(s) provided: {', '.join(invalid_usecases)}")
                return
        else:
             print("Error: No use cases specified when using CLI arguments.")
             parser.print_help()
             return

        method = args.method

    else:
        # Interactive mode
        yaml_file = select_yaml_file(usecase_maps_dir, "use case data")
        if not yaml_file:
            return # Exit if no use case data file is selected

        usecase_data = read_usecase_data(yaml_file)
        if usecase_data is None:
            return # Exit if there was an error reading the YAML file

        while True:
            print("\nSelect an option to run:")
            print("1. Validate")
            print("2. Execute")
            print("3. Validate and Execute")
            print("4. Remove Extra spaces in a use case data file") # Clarify this option
            print("5. Print all usecases in this mapfile")
            print("6. Exit")
            option = input("Enter your choice: ")

            if option == "6":
                print("Exiting...")
                return # Use return to exit main function
            if option == "5":
                print(f"\nAvailable use cases:\n{list(usecase_data.keys())}")
                continue

            if option in ["1", "2", "3", "4"]:
                print("\nAvailable use cases:")
                usecase_names = list(usecase_data.keys())
                for i, usecase_name in enumerate(usecase_names):
                    print(f"{i+1}. {usecase_name}")
                print("enter 'a' to select all usecases")
                print(f"{len(usecase_names) + 1}. Back to main options") # Option to go back

                choice = input("Enter your choice (comma-separated for multiple, hyphen-separated for range, 'a' for all): ")

                try:
                    if choice.lower() == "a":
                        selected_usecases = usecase_names
                    elif "-" in choice:
                        start, end = map(int, choice.split("-"))
                        selected_usecases = usecase_names[start-1:end]
                    elif "," in choice:
                        selected_usecases = [usecase_names[int(c)-1] for c in choice.split(",")]
                    else:
                        choice = int(choice)
                        if choice == len(usecase_names) + 1:
                            continue # Go back to main options
                        elif 1 <= choice <= len(usecase_names):
                            selected_usecases = [usecase_names[choice - 1]]
                        else:
                            print("Invalid choice. Please try again.")
                            continue

                    method = {
                        "1": "validate",
                        "2": "execute",
                        "3": "both",
                        "4": "strip" # New method for stripping
                    }.get(option)

                    if method == "strip":
                         # Handle stripping separately as it's a file operation, not playbook execution
                         for usecase_name in selected_usecases:
                             data_file_path = os.path.join(CONFIG_FILES_BASE_PATH, usecase_data[usecase_name]["data_file"])
                             read_and_strip_yaml(data_file_path) # Use the modified function
                             print(f"Extra spaces removed from {data_file_path}.")
                    else:
                        # Prepare for playbook execution/validation
                        # Clear the ansible_suite.sh file if in jenkins mode
                        if args.jenkins:
                             with open(f"{ANSIBLE_LOG_DIR_PATH}/ansible_suite.sh", 'w') as ansible_suite:
                                 ansible_suite.write('\n\n')

                        for usecase_name in selected_usecases:
                            if method == "validate" or method == "both":
                                validate_schema(usecase_name, usecase_data)
                            if method == "execute" or method == "both":
                                execute_playbook(usecase_name, usecase_data, ANSIBLE_HOSTS_INVENTORY_FILE, jenkins=args.jenkins, verbose_level=verbose_level)

                except (ValueError, IndexError) as e:
                    print(f"Invalid input: {e}. Please try again.")
            else:
                print("Invalid option. Please try again.")

    # If CLI arguments were provided, execute the actions
    if args.suitename and args.method and selected_usecases:
         # Clear the ansible_suite.sh file if in jenkins mode
         if args.jenkins:
              with open(f"{ANSIBLE_LOG_DIR_PATH}/ansible_suite.sh", 'w') as ansible_suite:
                  ansible_suite.write('\n\n')

         for usecase_name in selected_usecases:
             if method == "validate" or method == "both":
                 validate_schema(usecase_name, usecase_data)
             if method == "execute" or method == "both":
                 execute_playbook(usecase_name, usecase_data, ANSIBLE_HOSTS_INVENTORY_FILE,jenkins=args.jenkins, verbose_level=verbose_level)

if __name__ == "__main__":
    main()
