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
- Detailed Chef Node Inventory view and Management
- Jira Ticket Creation for VM's
- LDAP Authentication

## Is this project complete?
No, there is a lot more that needs to be done.  Certain features not yet implemented are:
- Zoom/Webex Integration (Sharing)
- Snapshot Management
- VM Power On/Off
- Chef Cookbook Pairing for Provisioned VM's

## Is this Web Application Secure?
I'm honestly not sure how secure it is; I'm simply not there yet!

## Suggestions for Implementation
I would highly suggest using this allong with a working PXE Booting solution.  That will provide a completely hands free VM Provisioning
process for Non VMWare Administrators.  I would also use, if desired, SQLAlchemy to build and support a more advanced Database structure, 
using more advanced queries.

## How can I help?
In any way you want!  Any suggestions, support, or improvement is welcome!

Current Issues:
- The VM Session Ticket used for Web Console works as expected, however the generated URL cannot be used with HTML iFrame tags.  An alternative would be to open the web console in a new tab, however I would prefer to keep it embedded into dashboard page.  Potential solutions include
  - vCenter configuration to disable the vCenter X-XSS Headers to allow iFrame embedding.
  - Alternative embedding solution to iFrame.  I've found some suggestions online, however I did not have the time to try any of them   out.
