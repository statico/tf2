#!/usr/bin/env coffee

fs = require 'fs'
https = require 'https'
async = require 'async'
strftime = require 'strftime'
path = require 'path'

contents = null

async.waterfall [

  ((cb) ->
    if filename = process.argv[2]
      console.log "Reading #{ filename }..."
      fs.readFile filename, (err, content) ->
        return cb err if err
        cb null, content
    else
      console.log "Downloading spreadsheet..."
      params =
        method: 'GET'
        port: 443
        host: 'spreadsheets.google.com'
        path: '/feeds/cells/0AnM9vQU7XgF9dFM2cldGZlhweWFEUURQU2pmOGJVMlE/od6/public/basic?alt=json'
      req = https.get params, (res) ->
        data = []
        res.on 'data', (chunk) -> data.push chunk
        res.on 'end', -> cb(null, data.join '')
      req.on 'error', (err) ->
        cb err
  ),

  ((content, cb) ->
    console.log 'Parsing JSON...'
    obj = JSON.parse content
    console.log 'Done!'

    if obj.version != '1.0'
      return cb "Version must be 1.0, got #{ obj.version }"

    dir = path.join path.dirname(process.argv[1]), 'pricelist'
    fs.mkdir dir
    filename = path.join dir, strftime('%Y-%m-%d.csv')
    writer = fs.createWriteStream filename

    headers = 0
    count = 0
    entries = obj.feed.entry
    row = null
    cell = 0
    cells = []
    for entry in entries

      n = parseInt entry.title.$t.substr(1), 10
      if n != row
        if cells
          if headers >= 2
            writer.write cells.join(',') + '\n'
            count++
          headers++
          cells.length = 0
          cell = 0
        row = n
      else
        cell++

      content = entry.content.$t.trim().toLowerCase()
      if cell == 3

        if /key/.test content then unit = 'key'
        else if /bud/.test content then unit = 'bud'
        else if /rec/.test content then unit = 'rec'
        else if /scrap/.test content then unit = 'scrap'
        else unit = 'ref'

        if match = content.match /(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)/
          low = match[1]
          high = match[2]
        else if match = content.match /(\d+(?:\.\d+)?)/
          low = high = match[1]
        else
          low = high = 0

        cells.push low
        cells.push high
        cells.push unit

      else if cell >= 4
        # 2nd price column
        continue

      else
        if /,/.test content
          content = '"' + content.replace(/"/g, "'") + '"'
        cells.push content


    console.log "Wrote #{ count } rows to #{ filename }."
  )

], (err) ->
  console.err err if err
