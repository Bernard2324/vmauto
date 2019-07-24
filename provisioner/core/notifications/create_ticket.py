from jira import JIRA


class jirasingleton (type):
	_instances = {}
	_username = 'jirauser'
	_password = 'abc123'

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super (jirasingleton, cls).__call__ (*args, **kwargs)
		return cls._instances[cls]


class ExampleJira (object):
	__metaclass__ = jirasingleton

	def __init__(self, title, vmissue):
		self.servicedesk = JIRA (server='http://jira.sub.example.com', logging=False, max_retries=1,
		                         timeout=30, auth=(jirasingleton._username, jirasingleton._password))

		self.vmissue = vmissue
		self.title = title
	def create(self):

		self.servicedesk.create_issue(project='JMP', summary=self.title,
		                               description=self.vmissue,
		                               issuetype={'name': 'Incident'})
