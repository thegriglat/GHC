#!/usr/bin/env python

import sys
import argparse

sys.path.append("modules")
import Data
import log

parser = argparse.ArgumentParser()
parser.add_argument('files', metavar="JSONfile", nargs="+", help = "File(s) to analyse.")
parser.add_argument('-jo', '--join', metavar="JSON", help="Join multiple JSON files into one", dest='joinjson')
parser.add_argument('-s', '--summary', help="Print channels summary", action="store_true", dest="summary")
parser.add_argument('-G', '--compareGHC', help="Compare multiple GHC runs", action="store_true", dest="cGHC")
args = parser.parse_args()

def transformdata(data):
  #datanew: {
  #  channel : {
  #    flags : [],
  #    data : {
  #      file1 : {<data>},
  #      file2 : {<data>}
  #      }
  #    }
  #  }
  #}
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

def getRMS(value):
  from numpy import mean, sqrt, square, arange
  return sqrt(mean(square(value)))

data = {}
for D in args.files:
  log.info("Reading file " + D + " ...")
  data.update({D : Data.jsonLoad(open(D,'r').read())})
  log.info("Finished " + D + ".")

if not args.cGHC:
  log.info("Trasform data structure ...")
  data = transformdata(data)
  log.info("Finished.")

if args.joinjson:
  log.info("Writing merged data to file " + args.joinjson + ' ...')
  import json
  Data.jsonExport(data, open(args.joinjson, 'w'))
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


if args.cGHC:
  print "=== Compare GHC runs ==="
  def getGHCStats(f):
    subdata = data[f]
    print "  " + f + " ==="
    print "  Active channels                         :"
    print "  Masked channels                         :", sum([1 for c in subdata.keys() if has_regexp("^DT?PG|^DLAMLP", subdata[c]['flags'])])
    print "  Total Problematic channels              :", sum([1 for c in subdata.keys() if len(subdata[c]['flags']) != 0])
    print "  Channels with design performance in G12 :", sum([1 for c in subdata.keys() if not has_regexp(".*G12", subdata[c]['flags'])])
    print "  Noisy (2 <= rms <= 6 ADC counts) in G12   :", sum([1 for c in subdata.keys() if "LRG12" in subdata[c]['flags']])
    print "  Very noisy (rms > 6 ADC counts) in G12  :", sum([1 for c in subdata.keys() if "VLRG12" in subdata[c]['flags']])
    
    print "  => Please select name of pedestal tag:"
    print "  => Possible values are: " + " ".join(data[f].items()[0][1]['data'].keys())
    f1 = raw_input ("  : ") 
    print "  Pedestal rms ADC counts in G12          :", getRMS([subdata[c]['data'][f1]['G12'][1] for c in subdata.keys() if subdata[c]['data'][f1].has_key('G12')])
    print "  Pedestal rms ADC counts in G6           :", getRMS([subdata[c]['data'][f1]['G6'][1] for c in subdata.keys() if subdata[c]['data'][f1].has_key('G6')])
    print "  Pedestal rms ADC counts in G1           :", getRMS([subdata[c]['data'][f1]['G1'][1] for c in subdata.keys() if subdata[c]['data'][f1].has_key('G1')])
    print "  APD with bad or no connection to HV     :", sum([1 for c in subdata.keys() if "SLAMPL" in subdata[c]['flags']])
    print "  Dead channels due to LVR board problems :", sum([1 for c in subdata.keys() if "DLAMPL" in subdata[c]['flags']])
  for f in args.files:
    getGHCStats(f)
  
