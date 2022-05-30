# Ansible-role-check-mk-API-agent

The purpose of the Ansible role is to insatll, configure a check_mk agent on a host and add this host to a check_mk server

## Description

This role do the following : 

- Installing package from a repo, file or URL
- Configure firewall according to the OS used
- Add local check if wanted (URL or file)
- Add host to check_mk server (various options are available) trough REST API

## Getting Started

### Requirements

* Python 2.6+
* Python module `requests`

Tested on Ubuntu 18+, Debian 10+ and CentOS 7+

### Installing

	ansible-galaxy install ramuskay.check_mk_agent_full

### Variables

* `check_mk_package: check-mk-agent` You can use a different name corresponding on your repo or an URL
* `check_mk_firewall: true` Add rule on the local firewall (firewalld for RHEL, ufw for Debian)
* `check_mk_certs_trust: true` Indicate if you trust the certificate URL of your check_mk
* `check_mk_api_add_host: true` If you want to add the target server on your checkmk server
* `check_mk_api_hostname:` IP or hostname of the host you want to add.  Relevant if check_mk_api_add_host is true
* `check_mk_api_url:` URL of the checkmk server. Relevant if check_mk_api_add_host is true
* `check_mk_api_username:` Username of the automation user who will interract with the API. Relevant if check_mk_api_add_host is true
* `check_mk_api_secret:` This is the secret of the automation user. Relevant if check_mk_api_add_host is true  
* `check_mk_api_folder: "/"` Indicate which check_mk folder you want to put your host in. Relevant if check_mk_api_add_host is true  
* `check_mk_api_state: "present"` Indicate if you want to add or delete an your host on checkmk. Relevant if check_mk_api_add_host is true 
* `check_mk_api_activate_changes: True` Indicate if you want to apply the changes done before. Relevant if check_mk_api_add_host is true 
* `check_mk_api_discover_services: refresh` Indicate the style of discover you want to make (if you want to). See module doc. Relevant if check_mk_api_add_host is true 
* `check_mk_local_checks: []` Need name parameter and url or src parameter. See example. Relevant if check_mk_api_add_host is true 


## Authors

[ramuskay](https://github.com/ramuskay) <aurel@beerus.fr>

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

Inspiration
* [ansible-role-check-mk-agent](https://github.com/elnappo/ansible-role-check-mk-agent)

