from __future__ import print_function
import ldap


class DomainAuthentication(object):
	_bind_user = 'domain.user@sub.example.com'
	_bind_passwd = 'abc123'
	_ldap_url = 'ldap://192.168.1.10:389'

	l = ldap.initialize(_ldap_url)
	l.protocol_vrsion = 3
	l.set_option(ldap.OPT_REFERRALS, 0)
	try:
		authenticator = l.simple_bind(
			_bind_user, _bind_passwd
		)
	except Exception:
		print("Failed to Establish Authentication Object")


	@staticmethod
	def buildAuth(search_user):
		user_data = DomainAuthentication.l.search_s(
			'OU=Users,DC=SUB,DC=EXAMPLE,DC=COM',
			ldap.SCOPE_SUBTREE, '(&(objectClass=user)(sAMAccountName={}))'.format(search_user)
		)

		return user_data
