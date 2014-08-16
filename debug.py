'''
Created on 8 Apr 2012

@author: sam
Adds debug capabilities to stdin/stdout - can type commands on stdin using soundblizzard.x interface and these will be eval'ed and outputted onto stdout
Performs this by adding watch onto mainloop for stdin so when data on stdin this is analysed
'''
import sys
from gi.repository import GObject
def oot(fd, condition):
	'''takes line from fd using readline and evals this, returning result of eval and any exceptions'''
	print('oot\n')
	text = fd.readline()
	#sb = soundblizzard
#	if text.startswith('int'):
#		import code
#		import readline
#		import rlcompleter
#		readline.parse_and_bind("tab: complete")		
#		code.InteractiveConsole(globals()).interact()
#		return True
	try:		
		global soundblizzard
		global sb
		sb = soundblizzard
		print(eval(text))
	except Exception as inst:
		print (inst)
		pass
	return True
#fd = sys.stdin.fileno()
#flags = fcntl.fcntl(fd, fcntl.F_GETFL)
#fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
GObject.io_add_watch(sys.stdin, GObject.IO_IN|GObject.IO_HUP|GObject.IO_PRI, oot)

if __name__ == '__main__':
	soundblizzard = None
	loop = GObject.MainLoop()
	loop.run()