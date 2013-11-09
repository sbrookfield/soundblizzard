#!/usr/bin/python
import socket, sys, difflib
from gi.repository import GObject
listen_ports = {}
recent_text = {}
def handle_data(source, condition, port):
    data = source.recv(1024)
    if len(data) > 0:
        print (str(port) +"Got " + data.rstrip())
        recent_text[port].append(data)
        return True # run again
    else:
        return False # stop looping (or else gtk+ goes CPU 100%)
def add_listen_port (hostname,port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    sock.connect((hostname,port))
    listen_ports[port] = sock
    recent_text[port] = []
    #sock.send('GET /index.html HTTP/1.1\nHost: pygtk.org\n\n')
    GObject.io_add_watch(sock, GObject.IO_IN, handle_data, port)
def send_input(conn, condition):
    print 'recent diff:'#+ str(recent_text)+"\n"+str(listen_ports)
    (s1,s2) = listen_ports.keys()
    for line in difflib.unified_diff(recent_text[s1], recent_text[s2], fromfile=str(s1), tofile=str(s2)):
        sys.stdout.write(line)
    text = conn.readline()
    print ('sending '+ text.rstrip())
    #print str(listen_ports)
    for i in listen_ports:
        listen_ports[i].send(text)
    #print listen_ports
    return True
add_listen_port('localhost',6600)
add_listen_port('localhost',6601)
GObject.io_add_watch(sys.stdin, GObject.IO_IN|GObject.IO_HUP|GObject.IO_PRI, send_input)
if __name__ == '__main__':
    mainloop = GObject.MainLoop()
    mainloop.run()