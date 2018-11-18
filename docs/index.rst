vmauto
========

This is a VM Auto-Provisioning Web Application, built with the Python Flask framework. It allows company personnel, who otherwise would not have access to VMWare vCenter, to Auto-Provision VM's via a centralized management platform. This web application keeps record of user owned databases, allows auto-provisioing (building/configuring) of VM's, VM Specification Selection, and more.

Be sure to set the FLASK_APP environment variable:

	export FLASK_APP=app.py
	
	flask run --host=192.168.1.10 --port=80 --debugger

Features
--------

- MySQL User and Inventory Managagement
- gateone in-app ssh jumpbox
- VMWare Session Ticket generation for in-app Web Console
- Detailed Chef Node Inventory view and Management
- Jira Ticket Creation for VM's
- LDAP Authentication

Installation
------------

Install vmauto  by running:

    install project

Contribute
----------

- Issue Tracker: github.com/Bernard2324/vmauto/issues
- Source Code: github.com/Bernard2324/vmauto

Support
-------

If you are having issues, please let me know.
Ideally, you should create an issue, however if you must reach me, email me at: bernard.infosystems@gmail.com

License
-------

The project is licensed under the MIT License
