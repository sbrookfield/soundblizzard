
try:
	import sys, time
except:
	warn('Could not find required python libraries: sys, time')
'''
	Spambox Log Functions
	'''

#TODO: Have a null version of loggy for speed
runtime = int(time.time())
def uptime():
	return (int(time.time() - runtime))
def currenttime():
	return (int(time.time()))
errors=[]
debug_setting = False
sb = None
def __init__():
	''
def debug(message):
	if debug_setting : print'\033[94m' + time.strftime('%x %X') + '- ' + message.replace('\n','|') + '\033[0m'
def log(message):
	print '\033[32m' + time.strftime('%x %X') + '- ' + message.replace('\n','|') + '\033[0m'
def warn(message):
	message = '\033[31m' + time.strftime('%x %X') + '- ' + message.replace('\n','|') + '\033[0m' 
	print message
#	errors.append(message)#TODO: test and fix log of warnings
#	if len(errors)>50:
#		warn('Maximum errors exceeded') # TAIL RECURSION
def die(message):
	print '\033[91m' + time.strftime('%x %X') + '- ' + message.replace('\n','|')+ '\033[0m'
	quit()
def quit():
	if sb:
		sb.mainloop.quit()
	print 'Now killing'
	#sys.exit() #TODO: tidy quit

if __name__ == "__main__":
	debug('Debug')
	log('Log')
	warn('Warn')
	die('Die')
	quit()