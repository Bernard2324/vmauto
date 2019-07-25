import XenAPI
from provisioner.core.config import testbed
from provisioner.core.utilities.cache import CheckCache


class XenConnectionMeta(type):
    __host_string = testbed.config['XenServer']
    __user = testbed.config['XenUser']
    __password = testbed.config['XenPassword']
    __session = XenAPI.Session(__host_string)
    __authenticated_session = __session.xenapi.login_with_password(__user, __password)

    def __new__(cls, *args, **kwargs):
        cls.session_wrapper = cls.__session
        return super(cls, XenConnectionMeta).__new__(cls, *args, **kwargs)


class XenConnection(object):

    __metaclass__ = XenConnectionMeta

    @classmethod
    @CheckCache(seconds=125000, cache_dir='/tmp/cache_directory/')
    def XenServerHosts(cls):
        """

        :return: all XenServer Hosts
        """
        return cls.session_wrapper.xenapi.host.get_all()

    @classmethod
    @CheckCache(seconds=85000, cache_dir='/tmp/cache_directory')
    def XenServerObjectName(cls, label):
        '''

        :param label: name of object to query XenServer for
        :return: Return the queried object
        '''
        return cls.session_wrapper.xenapi.VM.get_by_name_label(label)


class GoogleConnection(object):

    @classmethod
    def stringapi(cls, request):
        pass