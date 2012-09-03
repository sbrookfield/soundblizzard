#TODO do i really need this?
#TODO rename as core
try:
	import sys, time
except:
	warn('Could not find required python libraries: sys, time')
#TODO use in all code
'''
	Spambox Log Functions
	'''
#TODO make log color green warn orange, die red
#TODO count calls of each log / function call
#Have a null version of loggy for speed
errors=[]
debug_setting = False
def __init__():
	''
def debug(message):
	if debug_setting : print time.asctime() + ' :: ' + message.replace('\n', '|')
def log(message):
	print '\033[94m' + time.asctime() + ' :: ' + message.replace('\n', '|') + '\033[0m'
def warn(message):
	message = time.asctime() + ' !Error! :: ' + message.replace('\n', '|')
	print message
	errors.append(message)#TODO test and fix log of warnings
	if len(errors)>50:
		warn('Maximum errors exceeded')
def die(message):
	print time.asctime() + ' !Fatal Error! :: ' + message.replace('\n', '|')
	quit()

def quit():
	sys.exit() #TODO tidy quit

if __name__ == "__main__":
	quit()
