'''
Created on 8 Apr 2012

@author: sam
'''

import sys
from gi.repository import GObject
def oot(fd, condition):

    try:
        global SoundBlizzard
        print(eval(fd.readline()))
    except :
        pass
    return True
if __name__ == '__main__':
    loop = GObject.MainLoop()
GObject.io_add_watch(sys.stdin, GObject.IO_IN, oot)
if __name__ == '__main__':
    loop.run()

