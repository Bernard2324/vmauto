from domain_auto_provision.create.create_vm import CreateExhaustiveVM

Infrastructure = {
	"London": {
		"Addison Xeon E5-2620": [
			'192.168.1.1',
			'192.168.1.2',
			'192.168.1.3',
			'192.168.1.4',
			'192.168.1.5'
		],
		"domain Host Cluster": [
			'192.168.1.6',
			'192.168.1.7'
		]
	},
	"Paris": {}
}

CreationList = [
	{
		'Name': 'SampleVM1',
		'CPU': 4,
		'RAM': 4,
		'Disk': 150
	},
	{
		'Name': 'SampleVM2',
		'CPU': 4,
		'RAM': 4,
		'Disk': 100
	}
]


def Build():
	for vm in CreationList:
		create_exhaustive_vm = CreateExhaustiveVM(vm.get('Name'), vm.get('CPU'), vm.get('RAM'), vm.get('Disk'))
		create_exhaustive_vm.cleanup()
		create_exhaustive_vm.run()
		if create_exhaustive_vm.cleardata:
			create_exhaustive_vm.cleanup()
