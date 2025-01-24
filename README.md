<p align="center">
    <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" align="center" width="30%">
</p>
<p align="center"><h1 align="center">CATC_SD_ACCESS_CAMPUS.GIT</h1></p>
<p align="center">
	<em><code>❯ REPLACE-ME</code></em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/DNACENSolutions/CatC_SD_Access_campus.git?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/DNACENSolutions/CatC_SD_Access_campus.git?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/DNACENSolutions/CatC_SD_Access_campus.git?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/DNACENSolutions/CatC_SD_Access_campus.git?style=default&color=0080ff" alt="repo-language-count">
</p>
<p align="center"><!-- default option, no dependency badges. -->
</p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>
<br>

##  Table of Contents

- [ Overview](#-overview)
- [ Features](#-features)
- [ Project Structure](#-project-structure)
  - [ Project Index](#-project-index)
- [ Getting Started](#-getting-started)
  - [ Prerequisites](#-prerequisites)
  - [ Installation](#-installation)
  - [ Usage](#-usage)
  - [ Testing](#-testing)
- [ Project Roadmap](#-project-roadmap)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)

---

##  Overview

<code> 
	Cisco SD-Access Automation with Ansible
	This GitHub project provides a comprehensive Ansible framework for automating the deployment and management of Cisco SD-Access on a freshly installed Catalyst center. By leveraging Ansible's automation capabilities, this project streamlines the configuration process, reduces manual errors, and ensures consistency across your SD-Access fabric.
</code>

---

##  Key Features

<code>❯
	End-to-End Automation: This project covers the complete lifecycle of SD-Access deployment, from initial setup to ongoing management.
	Modular Design: The Ansible roles are organized in a modular fashion, allowing you to easily adapt and customize the automation to your specific needs.
	Idempotent Operations: The playbooks are designed to be idempotent, meaning they can be run multiple times without causing unintended changes to your network.
	Comprehensive Documentation: Clear and concise documentation guides you through the setup and usage of the Ansible playbooks.
	Workflow:

	The project automates the following key steps in the SD-Access deployment process:

	Roles and Users: Creates necessary roles and user accounts on the Catalyst center.
	Catalyst Center and ISE Integration: Integrates the Catalyst center with Cisco ISE for authentication and authorization.
	Global Credentials: Configures global credentials for device management.
	California Site Devices Discovery: Discovers and adds devices at the California site to the Catalyst center.
	Global Network Settings Servers: Configures global network settings, including DNS and NTP servers.
	Global Network Settings Global IP Pools: Defines global IP address pools for various purposes.
	California Site Design: Creates the site hierarchy and defines network settings specific to the California site.
	California Site Device Credentials: Assigns device-specific credentials for secure access.
	California Site Network Settings: Configures network settings for the California site, including VLANs and subnets.
	California Site Network Settings IP Pools: Defines site-specific IP address pools.
	California Site Devices Inventory: Gathers detailed inventory information for all devices at the California site.
	California Site Devices Provision: Provisions the discovered devices with the necessary configurations.
	California Site SWIM Devices Upgrade: Upgrades software images on devices using Cisco Software Image Management (SWIM).
	California Site Fabric: Builds the SD-Access fabric, including control plane and data plane configurations.
	California Site Fabric Transits: Configures fabric transit nodes for inter-site connectivity.
	California Site Virtual Networks: Creates virtual networks (VN) for different user groups and applications.
	California Site Devices to Fabric: Attaches devices to the SD-Access fabric.
	California Site Anchor VNs: Configures anchor VNs for external network connectivity.
	California Site Host Onboarding: Automates the onboarding of hosts onto the SD-Access fabric.
</code>

---

##  Project Structure

```sh
└── CatC_SD_Access_campus.git/
    ├── ansible.cfg
    ├── ansible_inventory
    │   └── catalystcenter_inventory_10.195.243.53
    ├── catc_configs
    │   ├── global
    │   └── sites
    ├── images
    │   ├── CCO_swim_image_download.png
    │   ├── CatC_Ise_AAA-Intg.png
    │   ├── CatC_Ise_AAA-Intg1.png
    │   ├── NW_Global_ip_pool.png
    │   ├── inventory_image_distribution_activation.png
    │   └── site_nw_ip_pools.png
    ├── requirements.txt
    ├── scripts
    │   └── run_playbooks.py
    ├── setup.sh
    └── usecase_maps
        ├── delete_confis_sda_fabric.yml
        └── sda_site_fabric_bringup_usecase.yml
```


###  Project Index
<details open>
	<summary><b><code>CATC_SD_ACCESS_CAMPUS.GIT/</code></b></summary>
	<details> <!-- __root__ Submodule -->
		<summary><b>__root__</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/setup.sh'>setup.sh</a></b></td>
				<td><code>❯ REPLACE-ME</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/requirements.txt'>requirements.txt</a></b></td>
				<td><code>❯ REPLACE-ME</code></td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- scripts Submodule -->
		<summary><b>scripts</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/scripts/run_playbooks.py'>run_playbooks.py</a></b></td>
				<td><code>❯ REPLACE-ME</code></td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- usecase_maps Submodule -->
		<summary><b>usecase_maps</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/usecase_maps/sda_site_fabric_bringup_usecase.yml'>sda_site_fabric_bringup_usecase.yml</a></b></td>
				<td><code>❯ REPLACE-ME</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/usecase_maps/delete_confis_sda_fabric.yml'>delete_confis_sda_fabric.yml</a></b></td>
				<td><code>❯ REPLACE-ME</code></td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- catc_configs Submodule -->
		<summary><b>catc_configs</b></summary>
		<blockquote>
			<details>
				<summary><b>global</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/global/network_settings_servers.yml'>network_settings_servers.yml</a></b></td>
						<td><code>❯ REPLACE-ME</code></td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/global/device_credentials.yml'>device_credentials.yml</a></b></td>
						<td><code>❯ REPLACE-ME</code></td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/global/catalyst_center_and_ise_integration.yml'>catalyst_center_and_ise_integration.yml</a></b></td>
						<td><code>❯ REPLACE-ME</code></td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/global/network_settings_global_ip_pools.yml'>network_settings_global_ip_pools.yml</a></b></td>
						<td><code>❯ REPLACE-ME</code></td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/global/swim_cco_image_tag.yml'>swim_cco_image_tag.yml</a></b></td>
						<td><code>❯ REPLACE-ME</code></td>
					</tr>
					<tr>
						<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/global/roles_and_users.yml'>roles_and_users.yml</a></b></td>
						<td><code>❯ REPLACE-ME</code></td>
					</tr>
					</table>
				</blockquote>
			</details>
			<details>
				<summary><b>sites</b></summary>
				<blockquote>
					<details>
						<summary><b>california</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_sda_fabric_devices.yml'>site_sda_fabric_devices.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_network_settings_servers.yml'>site_network_settings_servers.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_sda_fabric_sites_zones.yml'>site_sda_fabric_sites_zones.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_swim.yml'>site_swim.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_sda_fabric_anchor_vns.yml'>site_sda_fabric_anchor_vns.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_inventory.yml'>site_inventory.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_device_discovery.yml'>site_device_discovery.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/swim_distribution_activate.yml'>swim_distribution_activate.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_devices_provision.yml'>site_devices_provision.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_nw_settings_ippools.yml'>site_nw_settings_ippools.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_hierarchy_design.yml'>site_hierarchy_design.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_sda_fabric_vn_l2l3_gateways.yml'>site_sda_fabric_vn_l2l3_gateways.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_sda_transits.yml'>site_sda_transits.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_device_credentials.yml'>site_device_credentials.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_network_compliance.yml'>site_network_compliance.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/catc_configs/sites/california/site_sda_fabric_hostonboarding.yml'>site_sda_fabric_hostonboarding.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							</table>
						</blockquote>
					</details>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<details> <!-- ansible_inventory Submodule -->
		<summary><b>ansible_inventory</b></summary>
		<blockquote>
			<details>
				<summary><b>catalystcenter_inventory_10.195.243.53</b></summary>
				<blockquote>
					<table>
					<tr>
						<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/ansible_inventory/catalystcenter_inventory_10.195.243.53/hosts.yml'>hosts.yml</a></b></td>
						<td><code>❯ REPLACE-ME</code></td>
					</tr>
					</table>
					<details>
						<summary><b>group_vars</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/ansible_inventory/catalystcenter_inventory_10.195.243.53/group_vars/all.yml'>all.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							</table>
						</blockquote>
					</details>
					<details>
						<summary><b>host_vars</b></summary>
						<blockquote>
							<table>
							<tr>
								<td><b><a href='https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/master/ansible_inventory/catalystcenter_inventory_10.195.243.53/host_vars/dnac1.yml'>dnac1.yml</a></b></td>
								<td><code>❯ REPLACE-ME</code></td>
							</tr>
							</table>
						</blockquote>
					</details>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---
##  Getting Started

###  Prerequisites

Before getting started with CatC_SD_Access_campus.git, ensure your runtime environment meets the following requirements:

- **Programming Language:** Shell
- **Package Manager:** Pip


###  Installation

Install CatC_SD_Access_campus using one of the following methods:

**Build from source:**

1. Clone the CatC_SD_Access_campus.git repository:
```sh
❯ git clone https://github.com/DNACENSolutions/CatC_SD_Access_campus.git
```

2. Navigate to the project directory:
```sh
❯ cd CatC_SD_Access_campus
```

3. Install the project dependencies:


**Using `bash`** &nbsp; [<img align="center" src="" />]()

```sh
❯ source setup.sh
```

###  Usage
Run CatC_SD_Access_campus using the following command:
**Using `Python3`** &nbsp; [<img align="center" src="" />]()

```sh
❯ python3 scripts/run_playbooks.py
```
Follow the prompts. 
---
##  Project Roadmap

---

##  Contributing

- **💬 [Join the Discussions](https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/issues)**: Submit bugs found or log feature requests for the `CatC_SD_Access_campus.git` project.
- **💡 [Submit Pull Requests](https://github.com/DNACENSolutions/CatC_SD_Access_campus.git/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/DNACENSolutions/CatC_SD_Access_campus.git
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/DNACENSolutions/CatC_SD_Access_campus.git/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=DNACENSolutions/CatC_SD_Access_campus.git">
   </a>
</p>
</details>

---

##  License

This project is protected under the [SELECT-A-LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

##  Acknowledgments

- List any resources, contributors, inspiration, etc. here.

---
