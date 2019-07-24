from flask import Flask, render_template, redirect, url_for, request, session, send_from_directory, g
from flask_mysqldb import MySQL
from provisioner.core.notifications.create_ticket import ExampleJira
from wtforms import Form, StringField, PasswordField, validators, SelectField, TextAreaField
from passlib.hash import sha256_crypt
from functools import wraps
from provisioner.vmware.create_vm import CreateExhaustiveVM
from provisioner.core.utilities.authentication import DomainAuthentication
from provisioner.core.utilities.vm_session_ticket import uri
from chef import ChefAPI, Node
from celery import Celery

import os


app = Flask(__name__)

# MySQL Section
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'abc123'
app.config['MYSQL_DB'] = 'vmprovision'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'


# Init MySQL
mysql = MySQL(app)

# Init Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

app.secret_key = 'abc123'

username = None

@app.before_request
def before_request():
	g.user = None
	if 'username' in session:
		g.user = {}
		g.ldap_groups = DomainAuthentication.buildAuth(username)


# Favicon
@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Home Page
@app.route('/')
def index():
	return render_template('home.html')


# About Us Page
@app.route('/about')
def about():
	return render_template('about.html')


# # Provision A VM
# @app.route('/provision')
# def provision():
# 	return render_template('provision.html')


# Register Form Class
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords Do Not Match')
	])
	confirm = PasswordField('Confirm Password')


# Register User Account
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		# create cursor
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
		            (name, email, username, password))

		# Commit to DB
		mysql.connection.commit()
		cur.close()

		redirect(url_for('index'))

	return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if g.user:
		return redirect(url_for('dashboard'))
	if request.method == "POST":
		username = request.form['username']
		password_candidate = request.form['password']

		ldap_bind_test = DomainAuthentication.buildAuth(username)
		if ((ldap_bind_test is None) or (password_candidate == '')):
			try:
				# Just in case the Bind Initialization Timed out
				# Re-Initialize and send again

				ldap_bind_test = DomainAuthentication.buildAuth(username)
			except:
				error = "Invalid Login Credentials"
				return render_template('login.html', error=error)
		else:
			session['logged_in'] = True
			session['username'] = username
			session['Name'] = session['username'].split('.')[0][0].upper() + session['username'].split('.')[0][1:]
			session['email'] = session['username'] + '@sub.example.com'
			cur = mysql.connection.cursor()
			tgx = '\'{}\''.format(session['username'])
			result = cur.execute("SELECT * FROM users WHERE username = %s", [tgx])

			execute_it = cur.fetchall()

			if result > 0:
				pass
			else:
				cur.execute(
					"INSERT INTO users (name, email, username) values(%s, %r, %r)",
					(session['Name'], session['email'], session['username'])
				)
				mysql.connection.commit()
				cur.close()

			return redirect(url_for('dashboard'))

	return render_template('login.html')


# Chef if user Logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			return redirect(url_for('login'))
	return wrap


# Logout
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	return redirect(url_for('login'))


# View Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	# Create Cursor
	cur = mysql.connection.cursor()

	# Get vm's by Owner
	result = cur.execute('SELECT * FROM vm WHERE owner = %s', [session['username']])
	vms = cur.fetchall()

	if result > 0:
		return render_template('dashboard.html', vms=vms)
	else:
		msg = "No VM's Found Belonging to %s".format(session['username'])
		return render_template('dashboard.html', msg=msg)
	cur.close()


# @celery.task(bind=True)
# def chef_background_task(self):
# 	self.update_state(state='STARTED')
# 	node_data = {}
#
# 	# Information
# 	chef_server = 'https://chef.sub.example.com/organizations/example'
#
# 	with ChefAPI(chef_server, 'adminuser.pem', 'admin', ssl_verify=False):
# 		for node in Node.list():
# 			nodeobject = Node(node)
# 			node_data[node] = nodeobject.to_dict()
# 	self.update_state(state='SUCCESS')
#
# 	return node_data


# View Dashboard
@app.route('/chef_admin')
@is_logged_in
def chefnodes():
	node_data = {}

	# Information
	chef_server = 'https://chef.sub.example.com/organizations/example'

	with ChefAPI(chef_server, 'adminuser.pem', 'admin', ssl_verify=False):
		for node in Node.list():
			nodeobject = Node(node)
			node_data[node] = nodeobject.to_dict()

	return render_template('chef_admin.html', data=node_data)


# VM Create Class
class VmCreate(Form):
	hostname = StringField('hostname', [validators.Length(min=1, max=50)])
	cpucount = SelectField(u'cpucount', choices=[('1', '1'), ('2', '2'), ('4', '4'), ('8', '8')])
	ram = SelectField(u'ram', choices=[('1', '1'), ('2', '2'), ('4', '4'), ('8', '8')])
	disk = SelectField(u'disk', choices=[('50', '50'), ('100', '100'), ('150', '150')])


# Create VM
@app.route('/provision', methods=['GET', 'POST'])
@is_logged_in
def provision():
	form = VmCreate(request.form)
	if request.method == 'POST' and form.validate():
		hostname = form.hostname.data
		cpucount = form.cpucount.data
		ram = form.ram.data
		disk = form.disk.data

		# Create the Virtual Machine
		create_exhaustive_vm = CreateExhaustiveVM(hostname, int(cpucount), int(ram), int(disk))
		create_exhaustive_vm.cleanup()
		create_exhaustive_vm.run()
		if create_exhaustive_vm.cleardata:
			create_exhaustive_vm.cleanup()

		# flash('Virtual Machine Created', 'success')

		# Add newly created VM to Local DB
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO vm (hostname, cpu, ram, disk, power, owner) values(%s, %r, %r, %r, %s, %s)",
		            (hostname, int(cpucount), int(ram), int(disk), 'OFF', session['username']))
		mysql.connection.commit()

		# close connection
		cur.close()

		# flash('Virtual Machine Data Added to Local DB', 'success')
		return redirect(url_for('dashboard'))

	return render_template('provision.html', form=form)


@app.route('/console_dashboard/<string:pin>', methods=['GET', 'POST'])
@is_logged_in
def build_console(pin):
	cur = mysql.connection.cursor()

	# Get vm's by Owner
	result = cur.execute('SELECT * FROM vm WHERE owner = %s', [session['username']])
	vms = cur.fetchall()

	if request.method == 'POST':
		cur = mysql.connection.cursor()
		result = cur.execute(
			"SELECT h.hostname,v.vmid FROM vm h INNER JOIN vmdata v on (h.hostname=v.vmname) WHERE v.vmname=%s", [pin]
		)

		vmid_info = cur.fetchone()
		cur.close()
		if result > 0:
			URL = uri(str(vmid_info['hostname']), str(vmid_info['vmid']))
			#return render_template('console_session.html', url=URL)
			return render_template('console_dashboard.html', url=URL, vms=vms)
		else:
			msg = "No VM Found For {}".format(pin)
			return render_template('dashboard.html', msg=msg)


@app.route('/manage')
@is_logged_in
def manage():
	return render_template('manage.html')


@app.route('/docs')
def documentation():
	return render_template('docs.html')


@app.route('/packages')
@is_logged_in
def package():
	return render_template('package.html')


# Delete Node
@app.route('/delete_vm/<string:pin>', methods=['POST'])
@is_logged_in
def delete_vm(pin):
	# Create MySQL Cursor
	cur = mysql.connection.cursor()

	# Execute
	cur.execute('DELETE FROM vm WHERE hostname = %s', [pin])

	# commit
	mysql.connection.commit()

	# close
	cur.close()

	return redirect(url_for('dashboard'))


# Open Jira Ticket
class JiraIssue(Form):
	title = StringField('Title', render_kw={'readonly': True})
	issue = SelectField(u'Issue', choices=[('The Virtual Machine is unresponsive, Please troubleshoot connectivity.', 'VM Unresponsive'), ('The Virtual Machine has Incorrect Information.', 'VM Information Incorrect'),
	                                       ('The Virtual Machine was Not Built As requested!  Please review Specifications', 'VM Not Built as Requested')])


@app.route('/jira_ticket/<string:pin>', methods=['GET', 'POST'])
@is_logged_in
def jira_issue(pin):
	# Get Data Base Information for I'd VM
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM vm WHERE hostname = %s", [pin])
	vms = cur.fetchone()

	cur.close()

	form = JiraIssue(request.form)

	if request.method == 'POST' and form.validate():
		title = "Host {} Has an Issue".format(pin)
		issue = form.issue.data

		# Open jira ticket
		ticket = ExampleJira(title, issue)
		ticket.create()
		redirect(url_for('dashboard'))

	return render_template('jira_issue.html', form=form, vms=vms, identify=pin)


# Send Feedback
class Feedback (Form):
	User = StringField('Username', render_kw={'readonly': True})
	Email = StringField('Email', render_kw={'readonly': True})
	Message = TextAreaField('Feedback Message', [validators.optional(), validators.length(max=250)])


@app.route('/feedback', methods=['GET', 'POST'])
@is_logged_in
def feedback():
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT email, name FROM users WHERE username = %s", [session['username']])
	credentials = cur.fetchall()

	cur.close()

	form = Feedback(request.form)

	if request.method == 'POST' and form.validate():
		user = form.User.data
		email = form.Email.data
		message = form.Message.data

		redirect(url_for('dashboard'))

	return render_template('feedback.html', form=form, creds=credentials[0])


@app.route('/terminal')
@is_logged_in
def terminal():
	return render_template('terminal.html')


if __name__ == "__main__":
	app.run(debug=True)
