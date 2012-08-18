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

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(1)

def mkpath(dt):
  return os.path.join(os.path.dirname(sys.argv[0]), 'changes',
      'backpack-%s.csv' % dt.strftime('%Y-%m-%d'))

for path in [mkpath(yesterday), mkpath(today)]:
  seen = {}
  try:
    fh = codecs.open(path, 'r', 'utf8')
  except Exception, e:
    if sys.stdout.isatty(): print e
  else:
    reader = csv.reader(fh)
    for url, quality, name, change in reader:
      seen[url] = True

QUALITY = {
    't0': 'normal',
    't1': 'genuine',
    't3': 'vintage',
    't5': 'unusual',
    't6': 'unique',
    't7': 'community',
    't8': 'valve',
    't9': 'self-made',
    't11': 'strange',
    't13': 'haunted',
    }

writer = csv.writer(codecs.open(mkpath(today), 'a', 'utf8'))
html = urllib.urlopen('http://backpack.tf/latest').read()
soup = BeautifulSoup(html)

table = soup.find('table', {'class': 'table-striped'})
for row in table.find_all('tr'):
  cells = row.find_all('td')
  if len(cells) < 3: continue

  url = 'http://backpack.tf' + cells[0].a['href']
  if url in seen: continue

  span = cells[0].a.span
  if span and span.get('class'):
    quality = QUALITY.get(span['class'][0], 'unique')
  else:
    quality = 'unique'

  name = ' '.join(cells[0].a.stripped_strings)\
      .encode('ascii', 'replace').strip().lower()

  tag = cells[2].i
  change = tag.get('data-original-title', tag.get('title'))
  change = re.sub(r'\d+ \w+ ago', '', change)
  change = change.encode('ascii', 'replace').strip().lower()

  row = [url, quality, name, change]
  if sys.stdout.isatty(): print row
  writer.writerow(row)
