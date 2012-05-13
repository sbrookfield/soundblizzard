import gtk, pygtk


class slave(gtk.HBox):

    def __init__(self):
        gtk.HBox.__init__(self) # class is itself a hbox (just any old container will do!
        self.builder = gtk.Builder() # each class has it's own gtkbuilder
        self.builder.add_from_file("/home/sam/Code/spambox/src/preferences.glade") # file which contains widget to be inserted into space in master file
        self.widget = self.builder.get_object("hbox1") #find master widget in glade file to move into class
        self.widget.reparent(self) #moves widget into hbox of class slave
        self.builder.connect_signals(self) # connects signals to class

class master(object):
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("/home/sam/Code/spambox/src/gui.glade")
        self.container = self.builder.get_object("hbox2")
        self.slave = slave() # initialise slave class
        self.container.pack_start(self.slave, False, False)
        self.container.show_all() #recursively show some_container and all its child widgets
        self.window = self.builder.get_object("window1")
        self.window.show()
        self.builder.connect_signals(self)

if __name__ == "__main__":
    master()
    gtk.main()
