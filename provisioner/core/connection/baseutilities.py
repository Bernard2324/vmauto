from six.moves import cStringIO
from vmware.vapi.bindings.struct import PrettyPrinter


def pp(value):
    """ Utility method used to print the data nicely. """
    output = cStringIO()
    PrettyPrinter(stream=output).pprint(value)
    return output.getvalue()


class Context(object):
    """Class that holds common context for running vcenter samples."""

    def __init__(self, testbed, service_instance, client):
        # WebConfig configuration
        self._testbed = testbed

        # pyVmomi SOAP Service Instance
        self._service_instance = service_instance

        # vAPI vSphere client
        self._client = client

        self._option = {}

    @property
    def testbed(self):
        return self._testbed

    @testbed.setter
    def testbed(self, value):
        self._testbed = value

    @property
    def service_instance(self):
        return self._service_instance

    @service_instance.setter
    def service_instance(self, value):
        self._service_instance = value

    @property
    def soap_stub(self):
        return self._service_instance._stub

    @soap_stub.setter
    def soap_stub(self, value):
        self._soap_stub = value

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    @property
    def option(self):
        return self._option

    @option.setter
    def option(self, value):
        self._option = value

    def to_option_string(self):
        s = ['=' * 79,
             'WebConfig Options:',
             '=' * 79]
        s += ['   {}: {}'.format(k, self._option[k])
              for k in sorted(self._option.keys())]
        s += ['=' * 79]
        return '\n'.join(s)
