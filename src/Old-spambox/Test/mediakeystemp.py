#!/usr/bin/env python
"""Printing out gnome multi media keys via dbus-python.

   Using dbus with pygame.
"""
import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
import time

import pygame
from pygame.locals import *
DBUS = USEREVENT

def on_mediakey(comes_from, what):
    """ gets called when multimedia keys are pressed down.
    """
    #print ('comes from:%s  what:%s') % (comes_from, what)
    #if what in ['Stop','Play','Next','Previous']:
    #    print ('Got a multimedia key!')
    #else:
    #    print ('Got a multimedia key...')

    e = pygame.event.Event(DBUS, comes_from = comes_from, what = what)
    pygame.event.post(e)


# set up the glib main loop.
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.Bus(dbus.Bus.TYPE_SESSION)
bus_object = bus.get_object('org.gnome.SettingsDaemon',
                            '/org/gnome/SettingsDaemon/MediaKeys')

# this is what gives us the multi media keys.
dbus_interface='org.gnome.SettingsDaemon.MediaKeys'
bus_object.GrabMediaPlayerKeys("MyMultimediaThingy", 0,
                               dbus_interface=dbus_interface)

# connect_to_signal registers our callback function.
bus_object.connect_to_signal('MediaPlayerKeyPressed',
                             on_mediakey)

# We create a loop.
loop = gobject.MainLoop()

# this could be the mainloop, that we run forever.
#loop.run()

# The threads_init() function initializes the the use of Python
#  threading in the gobject module.
#
# http://pygstdocs.berlios.de/pygobject-reference/gobject-functions.html
gobject.threads_init()

# A gobject.MainContext represents a set of event sources that can be
#  run in a single thread
context = loop.get_context()


# Here we have our own main loop.
pygame.init()
screen = pygame.display.set_mode((320,200))
going = True
while going:
    events = pygame.event.get()
    for e in events:
        if e.type in [QUIT, KEYDOWN]:
            going = False
        if e.type is DBUS:
            print 'got a dbus key event!'
            print e

    # Each time around our main loop we do an iteration of the context.
    #  This lets the gobject MainLoop do its business.
    may_block = False
    were_events_dispatched = context.iteration(may_block)
    #print ('were events dispatched:%s:' % were_events_dispatched)
    pygame.display.flip()



