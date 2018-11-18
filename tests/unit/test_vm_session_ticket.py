import os
import tempfile
import pytest
import re

from utilities.vm_session_ticket import uri

def test_session_ticket():
    """
    Given a hostname and VMID, the uri() function
    should return a properly formatted session url
    """
    URL = uri('monitor_node', 'vm-50')
    url_pattern = 'https:\/\/([a-zA-z0-9]+){3,4}\/ui\/webconsole\.html\?\
        vmId=vm-50&vmName=monitor_node.*&locale=en_US'
    formatted_pattern = re.compile(url_pattern)

    assert formatted_pattern.match(URL)
