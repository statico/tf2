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
    os.path.dirname(sys.argv[0]), 'trades',
    'tftp-%s.csv' % datetime.datetime.now().strftime('%Y-%m-%d'))

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
html = urllib.urlopen('http://tf2tp.com/recent.php').read()
soup = BeautifulSoup(html)

QUALITY = {
    '1': 'genuine',
    '3': 'vintage',
    '5': 'unusual',
    '6': 'unique',
    '11': 'strange',
    }

for div in soup.find_all('div', {'class': 'trade'}):

  href = div.h4.a['href']
  match = re.search(r'trade=(\d+)', href)
  trade_id = int(match.group(1))
  if trade_id < last_trade: continue

  seen = set()

  have = div.find('div', {'class': 'tradeItems'}).find_all('div')
  for item in have:
    title = item['data-name'].lower()
    quality = QUALITY.get(item['data-quality'], 'unknown')

    details = ['Level %s' % item['data-level']]
    if 'data-isfulltradable' in item:
      if item['data-isfulltradable'] != '1':
        details.append('dirty')
    if 'cannotCraft' in item['class']:
      details.append('dirty')
    if 'data-particleeffectname' in item:
      details.append('effect: %s' % item['data-particleeffectname'])
    if 'data-customname' in item:
      details.append('has custom name')
    if 'data-customdescription' in item:
      details.append('has custom label')
    details = ', '.join(details).lower()

    seen.add(('HAVE', quality, title, details))

  want = div.find_all('div', {'class': 'wishlist'})
  for row in want:
    for item in row.find_all('div', {'class': 'itemSized'}):
      title = item['data-name'].lower()
      quality = QUALITY.get(item['data-quality'], 'unknown')
      seen.add(('WANT', quality, title, ''))

  for intent, quality, title, details in seen:
    row = [trade_id, int(time.time()), intent, quality, title, details]
    if sys.stdout.isatty(): print row
    writer.writerow(row)
