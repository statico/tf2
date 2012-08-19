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

filename = os.path.join( os.path.dirname(sys.argv[0]), 'pricelist', 'backpack-%s.csv'
    % datetime.datetime.now().strftime('%Y-%m-%d'))

writer = csv.writer(codecs.open(filename, 'a', 'utf8'))
html = urllib.urlopen('http://backpack.tf/pricelist').read()

# <td abbr='Demoman's something'>  <-- three apostrophes!
html = re.sub(r'<td abbr.*?>', '<td>', html)

soup = BeautifulSoup(html)

table = soup.find('table', {'id': 'pricelist'})
for row in table.tbody.find_all('tr'):
  cells = row.find_all('td')
  if len(cells) < 7: continue

  name = ' '.join(cells[0].stripped_strings).strip().lower().encode('ascii', 'replace')
  slot = ' '.join(cells[1].stripped_strings).strip().lower().encode('ascii', 'replace')

  pairs = [
      ('unique', 2),
      ('vintage', 3),
      ('genuine', 4),
      ('strange', 5),
      ('haunted', 6),
  ]

  for quality, index in pairs:
    contents = ' '.join(cells[index].stripped_strings).strip().lower()
    match = re.search(r'(\d+(?:\.\d+))\s+(\w+)', contents)
    if not match: continue
    price = float(match.group(1))
    unit = match.group(2).lower().replace('buds', 'bud')

    row = [quality, slot, name, price, price, unit]
    #if sys.stdout.isatty(): print row
    writer.writerow(row)
