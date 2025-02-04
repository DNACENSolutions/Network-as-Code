
def pytest_addoption(parser):
    """
    Adds command line options to specify the usecase map, inventory, and usecases.
    """
    parser.addoption("--MAPFILE", action="store", default="usecase_maps/california_sda_site_fabric_usecases.yml", help="Path to the usecase_maps path")
    parser.addoption("--INV", action="store", default="../ansible_inventory", help="Path to the inventory directory or file")
    parser.addoption("--UCS", action="store", default="all", help="List of comma separated usecases to run: all,usecase1,usecase2,...")
    parser.addoption("--RUNTYPE", action="store", default="validate", help="Validate inputs, run playbooks or both: validate,execute,both")
