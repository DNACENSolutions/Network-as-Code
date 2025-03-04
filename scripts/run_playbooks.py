import subprocess
import os
import yaml
import datetime
import argparse
# Define the base path for Ansible playbooks and configuration files
ANSIBLE_PLAYBOOKS_PATH = os.getenv('ANSIBLE_PLAYBOOKS_PATH', '$(pwd)/../catc_ansible_workflows/workflows/')
CONFIG_FILES_BASE_PATH = os.getenv('CONFIG_FILES_BASE_PATH', '$(pwd)/')
ANSIBLE_HOSTS_INVENTORY = os.getenv('ANSIBLE_HOSTS_INVENTORY', '$(pwd)/ansible_inventory/catalystcenter_inventory/hosts.yml')
ANSIBLE_LOG_DIR_PATH = os.getenv('ANSIBLE_LOG_DIR_PATH', '$(pwd)/../ansible_logs/')
CATC_LOG_DIR_PATH = os.getenv('CATC_LOG_DIR_PATH', '$(pwd)/../catc_logs/')
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

def validate_schema(usecase_name, usecase_data):
    """Validates the data file against the schema for the given use case."""
    config_file = os.path.join(ANSIBLE_PLAYBOOKS_PATH, usecase_data[usecase_name]["schema_file"])
    data_file = os.path.join(CONFIG_FILES_BASE_PATH, usecase_data[usecase_name]["data_file"])
    try:
        subprocess.run(["yamale", "-s", config_file, data_file], check=True)
        print(f"Schema validation successful for {usecase_name} \U0001F44D ")
    except subprocess.CalledProcessError as e:
        print(f"Schema validation failed for {usecase_name}: {e} \U0001F44E ")

def execute_playbook(usecase_name, usecase_data, jenkins=False, verbose_level="vvvv"):
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
            "-i", ANSIBLE_HOSTS_INVENTORY,
            playbook,
            "--e", f"VARS_FILE_PATH={data_file} --e catalyst_center_log_file_path={catalyst_center_log_file_path}",
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
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run Catalyst Center Ansible playbooks.")
    parser.add_argument("suitename", nargs='?', default=None, help="Name of the suite to run (e.g., 'fabric', 'sdwan')")
    parser.add_argument("method", choices=["validate", "execute", "both"], nargs='?', default=None, help="Action to perform: 'validate', 'execute', or 'both'")
    parser.add_argument("usecases", nargs='*', default=None, help="List of use cases to run (or 'all')")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    args = parser.parse_args()
    verbose_level = "vvvv" if args.verbose else "v"
    #ansible_log_path = os.path.join(ANSIBLE_LOG_DIR_PATH, f"{usecase_name}_ansible.log")
    with open(f"{ANSIBLE_LOG_DIR_PATH}/ansible_suite.sh", 'w') as ansible_suite:
        ansible_suite.write('\n\n')
    # Get the YAML file path from the user
    ANSIBLE_HOSTS_INVENTORY = os.getenv('ANSIBLE_HOSTS_INVENTORY', '$(pwd)/ansible_inventory/catalystcenter_inventory/hosts.yml')
    ANSIBLE_HOSTS_INVENTORY_DIR = os.path.dirname(ANSIBLE_HOSTS_INVENTORY)
    invyaml_files = [f for f in os.listdir(ANSIBLE_HOSTS_INVENTORY_DIR) if f.endswith(".yml")]
    if not invyaml_files:
        print(f"No YAML files found in {ANSIBLE_HOSTS_INVENTORY_DIR}")
        return
    print("\nAvailable inventory files:")
    for i, file in enumerate(invyaml_files):
        print(f"{i+1}. {file}")
    while True:
        try:
            choice = int(input("\nSelect a file by entering its number: "))
            if 1 <= choice <= len(invyaml_files):
                ANSIBLE_HOSTS_INVENTORY_FILE = os.path.join(ANSIBLE_HOSTS_INVENTORY_DIR, invyaml_files[choice - 1])
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    usecase_maps_dir = "usecase_maps"  # Replace with the actual directory path
    yaml_files = [f for f in os.listdir(usecase_maps_dir) if f.endswith(".yml")]
    if not yaml_files:
        print(f"No YAML files found in {usecase_maps_dir}")
        return
    print("\nAvailable use case data files:")

    if args.suitename and args.method and args.usecases:
        yaml_file = os.path.join(usecase_maps_dir, args.suitename)
        print(f"Reading use case data from {yaml_file}...")
        usecase_data = read_usecase_data(yaml_file)
        if usecase_data is None:
            print(f"Error reading use case data from {yaml_file}")
            return
        selected_usecases = ', '.join(args.usecases)
        selected_usecases = selected_usecases.split(",")
        print(f"Selected use cases: {selected_usecases}")
        print(f"Available usecase from suie file: {usecase_data.keys()}")
        # CLI arguments provided, use them
        suite_usecases = [uc for uc in usecase_data.keys() if uc in selected_usecases]
        if not suite_usecases and args.usecases != ["all"]:
            print(f"No use cases found in suite '{args.suitename}'")
            return
        if args.usecases == ["all"]:
            selected_usecases = list(usecase_data.keys())
        print(f"Selected use cases: {selected_usecases}")
        if args.usecases == ["all"]:
            selected_usecases = usecase_data.keys()
        else:
            # Check if the provided use cases are valid
            invalid_usecases = set(selected_usecases) - set(suite_usecases)
            if invalid_usecases:
                print(f"Invalid use case(s): {', '.join(invalid_usecases)}")
                return
        
        #selected_usecases = args.usecases
        for usecase_name in selected_usecases:
            if args.method == "validate" or args.method == "both":
                validate_schema(usecase_name, usecase_data)
            if args.method == "execute" or args.method == "both":
                execute_playbook(usecase_name, usecase_data, jenkins=True, verbose_level=verbose_level)
    else:
        # Get the YAML file path from the user
        usecase_maps_dir = "usecase_maps"  # Replace with the actual directory path
        yaml_files = [f for f in os.listdir(usecase_maps_dir) if f.endswith(".yml")]
        if not yaml_files:
            print(f"No YAML files found in {usecase_maps_dir}")
            return

        print("\nAvailable use case data files:")
        for i, file in enumerate(yaml_files):
            print(f"{i+1}. {file}")

        while True:
            try:
                choice = int(input("\nSelect a file by entering its number: "))
                if 1 <= choice <= len(yaml_files):
                    yaml_file = os.path.join(usecase_maps_dir, yaml_files[choice - 1])
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        if not yaml_files:
            print(f"No YAML files found in {usecase_maps_dir}")
            yaml_file = input("Enter the path to the YAML file containing use case data: ")
        print(f"Reading use case data from {yaml_file}...")
        usecase_data = read_usecase_data(yaml_file)

        if usecase_data is None:
            return  # Exit if there was an error reading the YAML file

        while True:
            print("\nSelect an option to run:")
            print("1. Validate")
            print("2. Execute")
            print("3. Validate and Execute")
            print("4. Exit")
            option = input("Enter your choice: ")

            if option == "4":
                print("Exiting...")
                break

            print("\nSelect a use case to run:")
            for i, usecase_name in enumerate(usecase_data.keys()):
                print(f"{i+1}. {usecase_name}")
                #print(f"Description: {usecase_data[usecase_name]['description']}")
            print("enter 'a' to select all usecases")
            print(f"{len(usecase_data.keys()) + 1}. Exit")
            choice = input("Enter your choice (comma-separated for multiple, hyphen-separated for range, 'a' for all): ")
            #Update this function to handle the user input for taking multiple usecases as , seperated input or - seperated input for range and all.
            try:
                if choice == "a":  # Run all use cases
                    selected_usecases = list(usecase_data.keys())
                elif "-" in choice:  # Run a range of use cases
                    start, end = map(int, choice.split("-"))
                    selected_usecases = list(usecase_data.keys())[start-1:end]
                elif "," in choice:  # Run multiple specific use cases
                    selected_usecases = [list(usecase_data.keys())[int(c)-1] for c in choice.split(",")]
                else:  # Run a single use case
                    choice = int(choice)
                    if choice == len(usecase_data.keys()) + 1:
                        print("Exiting...")
                        break
                    elif 1 <= choice <= len(usecase_data.keys()):
                        selected_usecases = [list(usecase_data.keys())[choice - 1]]
                    else:
                        print("Invalid choice. Please try again.")
                        continue

                for usecase_name in selected_usecases:
                    if option == "1":
                        validate_schema(usecase_name, usecase_data)
                    elif option == "2":
                        execute_playbook(usecase_name, usecase_data,verbose_level=verbose_level)
                    elif option == "3":
                        validate_schema(usecase_name, usecase_data)
                        execute_playbook(usecase_name, usecase_data, verbose_level=verbose_level)
                    else:
                        print("Invalid option. Please try again.")

            except (ValueError, IndexError) as e:
                print(f"Invalid input: {e}. Please try again.")

if __name__ == "__main__":
    main()
