# vmauto [![Build Status](https://travis-ci.org/Bernard2324/vmauto.svg?branch=master)](https://travis-ci.org/Bernard2324/vmauto)
VM Auto-Provisioning Web Application for VMWare, XenServer, Google Cloud, and/or AWS

## What is it?
This is a VM Auto-Provisioning Web Application, built with the Python Flask framework.  It allows company personnel, who otherwise would
not have access to VM Provisioning Platforms (VMWare vCenter, XenServer, Gcloud, AWS) to Auto-Provision VM's via a centralized management platform.  For personnel that already have access, it provides an automated platform and centralized management environment.  This web application keeps record of 
user owned VM's accross platforms, allows auto-provisioing (building/configuring) of VM's, VM Specification Selection, and more.

## What are some Features of this Web Application?
- MySQL User and Inventory Managagement (May change to Maria)
- gateone in-app ssh jumpbox (I may remove this)
- In-app Web Console for all supported Platforms 
- Support provisioning with Configuration/Provisioning Management tools.
- Jira Ticket Creation for VM's
- LDAP Authentication

## Is this project complete?
No, there is a lot more that needs to be done.  Certain features not yet implemented are:
- Snapshot Management (Only taking - not deleting)
- VM Power On/Off
- Usage of Terraform or other provisioning/configuration management solutions to provision to pre-defined roles.  You will not be able to define the roles, or config the management apps from this webapp.
- Support for XenServer, GCloud, and AWS provisioning using Terraform
- Support for Networking Servers Together
- Support for Building Proxied Environment
- Caching objects with Pickle for improved performance, and less frequent API calls
- XenServer VM Console Forwarding (https://developer-docs.citrix.com/projects/xenserver-sdk/en/7.4/xs-api-extensions/)
- Management of VM's for several platforms.  Not just one, but the ability to config provisioning and management for several platforms, on which your VM's live.
- Provisioning local, lightweight testbeds, using container solutions (docker only).
- Front End vs Back End hierarchy
- SQLAlchemy for more advanced DB Management
- Logging

## Is this Web Application Secure?
I'm honestly not sure how secure it is; I'm simply not there yet!

## Suggestions for Implementation
I would highly suggest using this allong with a working PXE Booting solution.  That will provide a completely hands free VM Provisioning
process for Non VMWare Administrators.  Alternatively, golden images can be created for supported distros.

## How can I help?
In any way you want!  Any suggestions, support, or improvement is welcome!

Current Issues:
- The VM Session Ticket used for Web Console works as expected, however the generated URL cannot be used with HTML iFrame tags.  An alternative would be to open the web console in a new tab, however I would prefer to keep it embedded into dashboard page.  Potential solutions include
  - vCenter configuration to disable the vCenter X-XSS Headers to allow iFrame embedding.
  - Alternative embedding solution to iFrame.  I've found some suggestions online, however I did not have the time to try any of them   out.

## Screenshots
![Alt text](/screenshots/screen02.png "User Dashboard")
![Alt text](/screenshots/screen03.png "Chef Admin")
![Alt text](/screenshots/screen04.png "Home Screen")
![Alt text](/screenshots/screen05.png "Jump Box")
![Alt text](/screenshots/screen06.png "Web Console")
