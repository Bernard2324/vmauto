from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import pymysql
import ssl
import re


class InsertSQL (object):
	def __init__(self):
		self.sql = pymysql.connect (host='localhost', user='root', password='abc123', database='vmprovision',
		                            port=3306)
		self.cur = self.sql.cursor ()

	def query(self, data):
		query = "INSERT INTO vmdata (vmname, vmid) VALUES (\'{}\', \'{}\');".format(
			data['hostname'], data['vmid']
		)
		self.cur.execute(query)
		self.sql.commit()

	def close(self):
		self.sql.close ()



db = InsertSQL()
vms = []
storage = {}

def main():
	context = ssl._create_unverified_context()

	si = SmartConnect(host='vcenter.sub.example.com', user='sub\admin.user', pwd='abc123', port=443,
	                  sslContext=context)


	content = si.RetrieveContent()

	for ch in content.rootFolder.childEntity:
		dc = ch
		vmf = dc.vmFolder
		vml = vmf.childEntity
		for i in vml:
			vms.append(i)

if __name__ == "__main__":
	main()
	for v in vms:
		try:
			if v.name in storage:
				continue
			storage[v.name] = {'hostname': v.name, 'vmid': re.findall('\d+', "{}".format(v.summary.vm))[0]}
		except:
			continue

	for k, v in storage.items():
		print "Inserting Row {}\n".format(k)
		db.query(v)
		print "Insert Complete"

	db.close()
