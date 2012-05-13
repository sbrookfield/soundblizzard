class library(object):
    def load_modules(self, modules): # add require support
        self.library = []
        for module in modules:
            try:
                self.library[module] = __import__(module)
                print "loaded module " + module
            except:
                print "Could not load module: " + module
    def load_module(self, module):
        try:
            return __import__(module, fromlist='*')
        except ImportError, e:
            self.out.add("Could not load ." + module + "\n\n" + "Error " + str(e.args))
if __name__ == "__main__":
    test = library()
    test.load_module("pygtk")


