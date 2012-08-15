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

today = datetime.datetime.now().strftime('%Y-%m-%d')

filename = os.path.join(os.path.dirname(sys.argv[0]), 'pricelist',
    'warehouse-%s.csv' % today)

writer = csv.writer(codecs.open(filename, 'a', 'utf8'))
html = urllib.urlopen('http://www.tf2wh.com/allitems.php').read()
soup = BeautifulSoup(html)

QUALITY = {
    '0': 'normal',
    '1': 'genuine',
    '3': 'vintage',
    '5': 'unusual',
    '6': 'unique',
    '7': 'community',
    '8': 'valve',
    '9': 'self-made',
    '11': 'strange',
    '13': 'haunted',
    }

key_price = 0

for item in soup.find('div', {'class': 'allitems'}).find_all('div', {'class': 'entry'}):

  for cls in item['class']:
    if cls.startswith('qual-'):
      quality = QUALITY[cls.replace('qual-', '')].lower()
    if cls.startswith('slot-'):
      slot = cls.replace('slot-', '').lower()

  price = int(item['price'])
  name = item['name'].encode('ascii', 'replace').lower()

  if 'supply crate key' in name:
    key_price = price

  row = [quality, slot, name, price, price, 'credits']
  if sys.stdout.isatty(): print row
  writer.writerow(row)

# --------------------

meta = {'key': key_price}

filename = os.path.join(os.path.dirname(sys.argv[0]), 'pricelist',
    'warehouse-meta-%s.json' % today)
obj = json.dumps(meta)
if sys.stdout.isatty(): print obj, '->', filename
fh = open(filename, 'w')
fh.write(obj)

