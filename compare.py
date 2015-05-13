#!/usr/bin/env python

import sys
import argparse

sys.path.append("modules")
import Data
import log

parser = argparse.ArgumentParser()
parser.add_argument('files', metavar="JSONfile", nargs="+", help = "File(s) to analyse.")
parser.add_argument('-jo', '--join', metavar="JSON", help="Join multiple JSON files into one", dest='joinjon')
parser.add_argument('-s', '--summary', help="Print channels summary", action="store_true", dest="summary")
args = parser.parse_args()

def transformdata(data):
  datanew = {}
  for key in data.keys():
    for ch in data[key].keys():
      if datanew.has_key(int(ch)):
        datanew[int(ch)]['flags'] += data[key][ch]['flags']
        datanew[int(ch)]['data'][key] = data[key][ch]['data']
      else:
        datanew.update({int(ch) : {'flags' : data[key][ch]['flags'], 'data': {key: data[key][ch]['data']}}})
  return datanew

def has_regexp(regexp, liststr):
  import re
  if regexp.__class__ == list:
    for r in regexp:
      if has_regexp(r, liststr):
        return True
  else:
    for v in liststr:
      if len(re.findall(regexp, v)) != 0:
        return True
  return False

data = {}
for D in args.files:
  log.info("Reading file " + D + " ...")
  data.update({D : Data.jsonLoad(open(D,'r').read())})
  log.info("Finished " + D + ".")

log.info("Trasform data structure ...")
data = transformdata(data)
log.info("Finished.")

if args.joinjson:
  log.info("Writing merged data to file + " + args.joinjson + ' ...')
  import json
  json.dump(data, open(args.joinjson, 'w'))
  log.info("Finished.")


if args.summary:
  pregexp = "^[BD]P|^[B]LR"
  tpregexp = "^[DSL]TP"
  lregexp = "^[DS]LAMPL|LLERRO"

  print "=== Summary Total Problematic Channels ==="
  print "  Total problematic channels                  :", sum([1 for c in data.keys() if len(data[c]['flags']) != 0])
  print "  Pedestals problems only                     :", sum([1 for c in data.keys() if has_regexp(pregexp, data[c]['flags'])])
  print "  Test Pulse problems only                    :", sum([1 for c in data.keys() if has_regexp(tpregexp, data[c]['flags'])])
  print "  Laser problems only                         :", sum([1 for c in data.keys() if has_regexp(lregexp, data[c]['flags'])])
  print "  Pedestals + Test Pulse problems only        :", sum([1 for c in data.keys() if has_regexp([pregexp,tpregexp], data[c]['flags'])])
  print "  Pedestals + Laser problems only             :", sum([1 for c in data.keys() if has_regexp([pregexp,lregexp], data[c]['flags'])])
  print "  Test Pulse + Laser problems only            :", sum([1 for c in data.keys() if has_regexp([tpregexp,lregexp], data[c]['flags'])])
  print "  Pedestals + Test Pulse + Laser problems only:", sum([1 for c in data.keys() if has_regexp([pregexp,tpregexp], data[c]['flags'])])

