import logging

def create_logger():
	
	logger = logging.getLogger('vmauto')
	logger.setLevel(logging.DEBUG)
	
	handler = logging.FileHandler(r'/var/log/vmauto.log')
	
	fmt = '%(asctime)s - %(name)s - $(levelname)s - %(message)s'
	
	formatter = logging.Formatter(fmt)
	handler.setFormatter(formatter)
	
	logger.addHandler(handler)
	
	return logger

logger = create_logger()