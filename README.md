# vmauto
VM Auto-Provisioning Web Application for VMWare

## What is it?
This is a VM Auto-Provisioning Web Application, built with the Python Flask framework.  It allows company personnel, who otherwise would
not have access to VMWare vCenter, to Auto-Provision VM's via a centralized management platform.  This web application keeps record of 
user owned databases, allows auto-provisioing (building/configuring) of VM's, VM Specification Selection, and more.

## What are some Features of this Web Application?
- MySQL User and Inventory Managagement
- gateone in-app ssh jumpbox
- VMWare Session Ticket generation for in-app Web Console 
- Chef Node Inventory view and management
- Jira Ticket Creation for VM's
- LDAP Authentication

## Is this project complete?
No, there is a lot more development needed.  Certain features not yet implemented are:
- Zoom/Webex Integration (Sharing)
- Snapshot Management
- VM Power On/Off
- Chef Cookbook Pairing for Provisioned VM's

## Is this Web Application Secure?
I'm honestly not sure how secure it is; I'm simply not there yet!

## Suggestions for Implementation
I would highly suggest using this allong with a working PXE Booting solution.  That will provide a completely hands free VM Provisioning
process for Non VMWare Administrators.  I would also use, if desired, SLAlchemy to build and support a more advanced Database structure, 
using more advanced queries.

## How can I help?
In any way you want!  Any suggestions, support, or improvement is welcome!
