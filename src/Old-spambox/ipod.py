#!/usr/bin/env python
import gpod #TODO - error handle not installed

ipoddb = gpod.Database('/media/GEORGE')
try:
    import pygtk
    pygtk.require("2.0")
    import gtk
except:
    print "Required libraries not found! Please install\n"
    #sys.quit()
