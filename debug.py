'''
Created on 8 Apr 2012

@author: sam
Adds debug capabilities to stdin/stdout - can type commands on stdin using sounblizzard.x interface and these will be eval'ed and outputted onto stdout
Performs this by adding watch onto mainloop for stdin so when data on stdin this is analysed
'''
import sys
from gi.repository import GObject
def oot(fd, condition):
	'''takes line from fd using readline and evals this, returning result of eval and any exceptions'''
	text = fd.readline()
	sb = soundblizzard
	if text.startswith('int'):
		import code
		import readline
		import rlcompleter
		readline.parse_and_bind("tab: complete")		
		code.InteractiveConsole(globals()).interact()
		return True
	try:		
		global soundblizzard
		global sb
		print(eval(text))
	except Exception as inst:
		print inst
		pass
	return True
if __name__ == '__main__':
	loop = GObject.MainLoop()
GObject.io_add_watch(sys.stdin, GObject.IO_IN, oot)
if __name__ == '__main__':
	loop.run()