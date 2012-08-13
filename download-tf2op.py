#!/usr/bin/env python

from bs4 import BeautifulSoup
import urllib
import csv
import os
import sys
import re
import time
import codecs

filename = os.path.join( os.path.dirname(sys.argv[0]), 'trades', 'tf2op-%s.csv'
    % datetime.datetime.now().strftime('%Y-%m-%d'))

last_trade = 0
try:
  fh = codecs.open(filename, 'r', 'utf8')
except IOError:
  pass
else:
  reader = csv.reader(fh)
  for row in reader:
    num = int(row[0])
    if num > last_trade: last_trade = num
  fh.close()

writer = csv.writer(codecs.open(filename, 'a', 'utf8'))
html = urllib.urlopen('http://www.tf2outpost.com/').read()
soup = BeautifulSoup(html)

for div in soup.find_all('div', {'class': 'trade'}):

  href = div.find('a', href=True)['href']
  match = re.search(r'/trade/(\d+)', href)
  trade_id = int(match.group(1))
  if trade_id < last_trade: continue

  parts = div.find_all('div', {'class': 'four-column'})
  for part, intent in ((parts[0], 'HAVE'), (parts[1], 'WANT')):

    seen = set()
    for item in part.find_all('div', {'class': 'item'}):
      details = item.find('div', {'class': 'details'})
      h1 = details.h1.extract()
      quality = ' '.join(h1['class'])
      seen.add((quality.lower(),
                h1.string.lower(),
                ' '.join(details.stripped_strings).lower()))

    for quality, title, details in seen:
      row = [trade_id, int(time.time()), intent, quality, title.encode('ascii', 'replace'), details.encode('ascii', 'replace')]
      writer.writerow(row)
