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

filename = os.path.join(
    os.path.dirname(sys.argv[0]), 'pricelist',
    'backpack-%s.csv' % datetime.datetime.now().strftime('%Y-%m-%d'))

writer = csv.writer(codecs.open(filename, 'a', 'utf8'))
html = urllib.urlopen('http://backpack.tf/pricelist').read()
soup = BeautifulSoup(html)

COLUMNS = (
    ('unique', 2),
    ('vintage', 3),
    ('genuine', 4),
    ('strange', 5),
    ('haunted', 6)
)

table = soup.find('table', {'id': 'pricelist'})
for row in table.tbody.find_all('tr'):
  cells = row.find_all('td')

  try:
    name = cells[0].string.encode('ascii', 'replace').lower()
    slot = cells[1].string.encode('ascii', 'replace').lower()
  except IndexError:
    continue

  for quality, index in COLUMNS:
    value = ' '.join(cells[index].stripped_strings)
    match = re.search(r'(\d+(?:\.\d+)?)', value)
    if not match: continue
    price = float(match.group(1))

    unit = 'ref'
    if re.search(r'key', value): unit = 'key'
    elif re.search(r'bud', value): unit = 'bud'
    elif re.search(r'rec', value): unit = 'rec'
    elif re.search(r'scrap', value): unit = 'scrap'

    row = [quality, slot, name, price, price, unit]
    if sys.stdout.isatty(): print row
    writer.writerow(row)
