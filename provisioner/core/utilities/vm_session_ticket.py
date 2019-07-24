from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import OpenSSL
import ssl
from ssl import _create_unverified_context


class constantsession(object):
	def __init__(cls, name, bases, dict):
		super(constantsession, cls).__init__(name, bases, dict)
		cls.instance = None

	def __call__(cls, *args, **kwargs):
		if cls.instance is None:
			cls.instance = super(constantsession, cls).__call__(*args, **kwargs)
		return cls.instance


class vcenterInitialize(object):
	# __metaclass__ = constantsession

	def __init__(self, host, user, passwd, port, context):

		self.si = SmartConnect(host=host, user=user, pwd=passwd, port=443, sslContext=context)
		self.content = self.si.RetrieveContent()
		self.instance = self.content.about.instanceUuid
		self.vc_cert = ssl.get_server_certificate(('vcenter.sub.example.com', 443))

		self.vc_pem = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, self.vc_cert)
		self.vc_fingerprint = self.vc_pem.digest('sha1')


class SessionTicket(vcenterInitialize):

	def __init__(self):
		super(SessionTicket, self).__init__('vcenter.sub.example.com',
			'sub\admin.user', 'abc123', 443, _create_unverified_context())

	def establishSession(self):
		ssl._create_default_https_context = ssl._create_unverified_context()
		self.instance = self.content.about.instanceUuid
		self.vc_cert = ssl.get_server_certificate(('vcenter.sub.example.com', 443))

		self.vc_pem = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, self.vc_cert)
		self.vc_fingerprint = self.vc_pem.digest('sha1')
		session_manager = self.content.sessionManager
		return (self.instance, self.vc_fingerprint,session_manager.AcquireCloneTicket())


def uri(vmname, vmid):

	sess = SessionTicket()
	instance, fingerprint, ticket = sess.establishSession()

	if not all(isinstance(argument, str) for argument in
		[vmname, vmid]):

		raise TypeError('All Arguments Passed Must be Type: \'str\'\n')

	return "https://vcenter.sub.example.com/ui/webconsole.html?vmId=vm-" + vmid + "&vmName=" + vmname + \
	       "&serverGuid=" + instance + "&host=vcenter.sub.example.com:443&sessionTicket=" + ticket + \
	       "&thumbprint=" + fingerprint + "&locale=en_US"
