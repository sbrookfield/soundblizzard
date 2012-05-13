#!/usr/bin/env python
import os
from os.path import join, getsize
for root, dirs, files in os.walk('/home/sam/Music'):
    print root, "consumes",
    print sum(getsize(join(root, name)) for name in files),
    print "bytes in", len(files), "non-directory files"
    if 'CVS' in dirs:
        dirs.remove('CVS')
