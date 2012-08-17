#!/usr/bin/env python

import os
import datetime
import sys
import re

cutoff = datetime.datetime.now() - datetime.timedelta(5)
basedir = os.path.dirname(sys.argv[0])
pattern = re.compile(r'(\d{4}-\d{2}-\d{2})\.(csv|json|html)$')

for root, dirs, files in os.walk(basedir):
  for filename in files:
    match = pattern.search(filename)
    if match:
      dt = datetime.datetime.strptime(match.group(1), '%Y-%m-%d')
      if dt < cutoff:
        path = os.path.join(root, filename)
        os.remove(path)
        if sys.stdout.isatty(): print 'Removed', path
