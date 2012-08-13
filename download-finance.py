#!/usr/bin/env python

from bs4 import BeautifulSoup
import urllib
import csv
import os
import sys
import re
import time
import datetime
import codecs
import json

filename = os.path.join(
    os.path.dirname(sys.argv[0]), 'trades',
    'finance-%s.json' % datetime.datetime.now().strftime('%Y-%m-%d'))

data = {}

html = urllib.urlopen('http://tf2finance.com/').read()
soup = BeautifulSoup(html)
table = soup.find('section', {'id': 'price'}).find('table')
text = ' '.join(table.stripped_strings)
match = re.search(r'1 Earbuds = (\d+(?:\.\d+)?) USD', text)
data['bud_dollars'] = float(match.group(1))

obj = json.dumps(data)
if sys.stdout.isatty(): print obj, '->', filename

fh = open(filename, 'w')
fh.write(obj)
