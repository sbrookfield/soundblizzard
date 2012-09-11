#!/usr/bin/python
class toggle(object):
  def __setattr__(self, name, value):
    print 'argh' + name
    print __name__
ben = toggle()
ben.parp = 4
print ben

def __setattr__(self, name, value):
  print 'arTYgh' + name
