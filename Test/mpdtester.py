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
    try:
        sock.connect((hostname,port))
    except:
        print ('Could not connect to '+str(hostname)+'@'+str(port))
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
def add_input_port(server, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((server, port)) #TODO: check port empty first
    except:
        print ('Server failed to start on host %s port %s' % (server, port))
        return False
    sock.listen(1)
    print('Server Interface Running on ' + server + ':' + str(port) )
    GObject.io_add_watch(sock, GObject.IO_IN, got_input, port)
def got_input(source, data, *port):
    '''Asynchronous connection listener. Starts a handler for each connection.'''
    conn, temp = source.accept()
    print( "mpdserver connected from " + str(conn.getsockname()))
    GObject.io_add_watch(conn, GObject.IO_IN, handle_input)
    conn.send('OK MPD 0.16.0\n')
    return True
def handle_input(self,sock):
    buff = self.recv(65536) #TODO: handle if more on conn to recieve than 4096
    if not len(buff):
        print( "Connection closed - no input to port "+str(port) )
        return False
    elif len(buff)>60000:
        print('Connection buff full, data may be lost' . buff)
    #loggy.log('MPD Server got:' +buff)
    while '\n' in buff:
        (line, buff) = buff.split("\n", 1)
        print ('got data :' +line)
        for i in listen_ports:
            listen_ports[i].send(line+"\n")
    return True
add_listen_port('localhost',6602)
add_listen_port('localhost',6601)
add_input_port('localhost',6600)
GObject.io_add_watch(sys.stdin, GObject.IO_IN|GObject.IO_HUP|GObject.IO_PRI, send_input)
if __name__ == '__main__':
    mainloop = GObject.MainLoop()
    mainloop.run()