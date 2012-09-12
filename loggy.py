
try:
	import sys, time
except:
	warn('Could not find required python libraries: sys, time')
#TODO: use in all code
'''
	Spambox Log Functions
	'''
#TODO: make log color green warn orange, die red
#TODO: see python logging module
#TODO: count calls of each log / function call
#Have a null version of loggy for speed
errors=[]
debug_setting = False
def __init__():
	''
def debug(message):
	if debug_setting : print'\033[94m' + time.strftime('%x %X') + '- ' + message.replace('\n', '|') + '\033[0m'
def log(message):
	print '\033[32m' + time.strftime('%x %X') + '- ' + message.replace('\n', '|') + '\033[0m'
def warn(message):
	message = '\033[31m' + time.strftime('%x %X') + '- ' + message.replace('\n', '|') + '\033[0m' 
	print message
	errors.append(message)#TODO: test and fix log of warnings
	if len(errors)>50:
		warn('Maximum errors exceeded')
def die(message):
	print '\033[91m' + time.strftime('%x %X') + '- ' + message.replace('\n', '|')+ '\033[0m'
	quit()
def quit():
	sys.exit() #TODO: tidy quit

if __name__ == "__main__":
	debug('Debug')
	log('Log')
	warn('Warn')
	die('Die')
	quit()