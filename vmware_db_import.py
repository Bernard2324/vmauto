import pymysql
import csv


'''
Quick and easy:  Use this ti import VM's to DB
'''

class InsertSQL(object):

	def __init__(self):
		self.sql = pymysql.connect(host='localhost', user='root', password='abc123', database='vmprovision', port=3306)
		self.cur = self.sql.cursor()

	def query(self, row):
		query = "INSERT INTO vm (hostname, cpu, ram, disk, power, owner) VALUES (\'{}\', {}, {}, {}, \'{}\', \'{}\'});".format(
			row[0], row[1], row[2], row[3], row[4], 'None'
		)
		self.cur.execute(query)
		self.sql.commit()

	def close(self):
		self.sql.close()


db = InsertSQL()
import_file = 'vmlist.csv'
with open(import_file, 'rb') as csvfile:
	skip = True
	vmreader = csv.reader(csvfile, delimiter='\t')
	for row in vmreader:
		if skip:
			skip=False
			continue
		print "Inserting Data For: {}\n".format(row[0])
		db.query(row)

	db.close()
	csvfile.close()
