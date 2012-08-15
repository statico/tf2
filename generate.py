#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from bs4 import BeautifulSoup
import urllib
import datetime
import sys
import os
import csv
import re
import json

if len(sys.argv) > 1:
  dt = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')
else:
  dt = datetime.datetime.now()

today = dt.strftime('%Y-%m-%d')
yesterday = (dt - datetime.timedelta(1)).strftime('%Y-%m-%d')
tomorrow = (dt + datetime.timedelta(1)).strftime('%Y-%m-%d')

filename = os.path.join(os.path.dirname(sys.argv[0]), 'output', '%s.html' % today)

if sys.stdout.isatty():
  print 'Generating output for %s...' % today

fh = open(filename, 'w')

fh.write('''<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="robots" content="noindex, nofollow"/>
<title>%(today)s trade stats</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
<script src="common.js"></script>
</head>
<body>
<p>
  <a href="%(yesterday)s.html">← %(yesterday)s</a>
  <a href="%(tomorrow)s.html">%(tomorrow)s →</a>
</p>
<p>
  <a href="http://backpack.tf/pricelist">backpack.tf price list</a>
  <a href="http://tf2spreadsheet.blogspot.com">tf2 spreadsheet</a>
  <a href="http://www.tf2outpost.com/search">TF2 Outpost search</a>
  <a href="http://tf2tp.com/searchMongo72.php">TF2 TP search</a>
  <a href="http://www.sourceop.com/modules.php?name=Forums&file=viewforum&f=21">SourceOp</a>
</p>
<h1>Trade Stats for %(today)s</h1>
''' % locals())

def do_trades(prefix):
  reader = csv.reader(open('trades/%s-%s.csv' % (prefix, today), 'r'))
  stats = defaultdict(int)
  for tid, t, intent, quality, name, details in reader:
    if intent == 'WANT':
      stats[(quality, name)] += 1
  keys = reversed(sorted(stats.keys(), key=lambda x: stats[x]))
  for key in keys:
    count = stats[key]
    if count > 10:
      fh.write('<tr><td>%s <span class="name">%s</span></td><td>%s</td></tr>' % (key[0], key[1], count))

####### OUTPOST WANTS

fh.write('<div class="module">')
fh.write('<h2>TF2 Outpost wants</h2>')
fh.write('<div class="long"><table>')
do_trades('tf2op')
fh.write('</table></div>')
fh.write('</div>')

####### TRADING POST WANTS

fh.write('<div class="module">')
fh.write('<h2>TF2 Trading Post wants</h2>')
fh.write('<div class="long"><table>')
do_trades('tftp')
fh.write('</table></div>')
fh.write('</div>')

####### SPREADSHEET

key_price = 0
bill_price = 0
bud_price = 0

def do_prices(prefix):
  global key_price
  global bill_price
  global bud_price

  old = {}
  reader = csv.reader(open('pricelist/%s-%s.csv' % (prefix, yesterday), 'r'))
  for quality, slot, name, low, high, unit in reader:
    key = '%s %s' % (quality, name)
    try:
      high = float(high)
    except:
      high = 0
    old[key] = (high, unit)

  reader = csv.reader(open('pricelist/%s-%s.csv' % (prefix, today), 'r'))
  for quality, slot, name, low, high, unit in reader:

    if quality == 'unusual': continue

    if prefix == 'spreadsheet':
      if name == 'key':
        key_price = float(high)
      if name == "bill's hat":
        bill_price = float(high)
      if name == 'earbuds':
        bud_price = float(high)

    key = '%s %s' % (quality, name)
    cls = None
    try:
      high = float(high)
    except:
      high = 0
    if key in old:
      old_high, old_unit = old[key]
      if old_high < high:
        cls = 'up'
      elif high < old_high:
        cls = 'down'
    else:
      old_high = 0
      old_unit = ''
      cls = 'new'
    if cls:
      if unit == 'credits':
        fh.write('''
          <tr>
            <td>%(quality)s <span class="name">%(name)s</span></td>
            <td>%(old_high)dc</td>
            <td class="%(cls)s">%(high)dc</td>
          </tr>''' % locals())
      else:
        fh.write('''
          <tr>
            <td>%(quality)s <span class="name">%(name)s</span></td>
            <td>%(old_high).2f %(old_unit)s</td>
            <td class="%(cls)s">%(high).2f %(unit)s</td>
          </tr>''' % locals())

fh.write('<div class="module">')
fh.write('<h2>TF2 Spreadsheet Price Updates</h2>')
fh.write('<div class="long"><table>')
do_prices('spreadsheet')
fh.write('</table></div>')
fh.write('</div>')

fh.write('<div class="module">')
fh.write('<h2>TF2 Warehouse Updates</h2>')
fh.write('<div class="long"><table>')
do_prices('warehouse')
fh.write('</table></div>')
fh.write('</div>')

####### BACKPACK

fh.write('<div class="module">')
fh.write('<h2>Backpack.tf Changes</h2>')
fh.write('<div class="long"><table>')

old = {}
reader = csv.reader(open('changes/backpack-%s.csv' % today, 'r'))
for url, quality, name, change in reader:
  if quality == 'unusual': continue # too noisy

  match = re.search(r'(\w+) (\d+(?:\.\d+)?) (\w+) from (\d+(?:\.\d+)?) (\w+)', change)
  direction = match.group(1)
  diff = float(match.group(2))
  unit1 = match.group(3)
  old = float(match.group(4))
  unit2 = match.group(5)

  if direction == 'up':
    cls = 'up'
    new = old + diff
  elif direction == 'down':
    cls = 'down'
    new = old - diff
  else:
    cls = 'new'
    new = 0

  fh.write('''
    <tr>
      <td><a href="%(url)s" target="_blank">%(name)s</a></td>
      <td>%(old).2f %(unit1)s</td>
      <td class="%(cls)s">%(new).2f %(unit2)s</td>
    </tr>''' % locals())

fh.write('</table></div>')
fh.write('</div>')

####### FINANCE IMAGE

fh.write('<hr/>');

fh.write('<h2>TF2 finance</h2>')
fh.write('<p><img src="finance.jpg"/></p>')

####### FOOTER / SCRIPTS

data = json.loads(open('trades/finance-%s.json' % today, 'r').read())
bud_dollars = data['bud_dollars']

data = json.loads(open('pricelist/warehouse-meta-%s.json' % today, 'r').read())
key_credits = data['key']

fh.write('''
  <script>
    key_price = %(key_price).5f;
    bill_price = %(bill_price).5f;
    bud_price = %(bud_price).5f;
    bud_dollars = %(bud_dollars).5f;
    key_credits = %(key_credits).5f;
  </script>
  <footer>This data is for private use only. Do not share. It is not indexed.</footer>
''' % locals())

fh.write('</body></html>\n')
