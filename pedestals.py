#!/usr/bin/env python

import os
import sys
import shutil
import argparse

sys.path.append("modules")
from Pedestal import *

parser = argparse.ArgumentParser()
parser.add_argument('runs', metavar="RUN", nargs="+", help = "Run(s) to analyse. Use '-' for reading from stdin")
parser.add_argument('-o', '--output', help="Results directory (default: RESULTS)", dest='output')
parser.add_argument('-c', '--dbstr', help="Connection string to DB (oracle://user/pass@db)", dest='dbstr')
parser.add_argument('-j', '--json', help="Filename for output to JSON format", dest='json')
parser.add_argument('-bl','--barrel-limits', dest="barrel_limits", help = "Limits for barrel. Check README")
parser.add_argument('-el','--endcap-limits', dest="endcap_limits", help = "Limits for endcap, Check README")
args = parser.parse_args()

if not args.output:
  outputdir = "RESULTS"
else:
  outputdir = args.output
if not os.path.exists(outputdir):
  os.mkdir(outputdir)

if args.runs == ['-']:
    source = sys.stdin
else:
    runs = args.runs
    if args.dbstr is None:
      print "Please specify --dbstr!"
      sys.exit(0)
    source = args.dbstr

print "=== PEDESTALS ==="
DataEB = PedestalData()
DataEE = PedestalData()
DataEB.readAllChannels("data/EB_all_ch.txt")
DataEE.readAllChannels("data/EE_all_ch.txt")

DataEB.readPedestal(source, runnum=runs)
DataEE.readPedestal(source, runnum=runs)

if args.json:
  sumdict = {}
  sumdict.update(DataEB.getChannels())
  sumdict.update(DataEE.getChannels())
  Data.jsonExport(sumdict, open(args.json, 'w'))

if not args.barrel_limits is None:
  DataEB.setOption("pedestallimits", {"G1" : ((1, 0.2), (1.1, 3)), "G6" : ((1, 0.4), (1.3, 4)), "G12" : ((1, 0.5), (2.1, 6))})
else:
  DataEB.setOption("pedestallimits", args.barrel_limits)
if not args.endcap_limits is None: 
  DataEE.setOption("pedestallimits", {"G1" : ((1, 0.2), (1.5, 4)), "G6" : ((1, 0.4), (2, 5)),   "G12" : ((1, 0.5), (3.2, 7))})
else:
  DataEE.setOption("pedestallimits", args.endcap_limits)

for D in (DataEB, DataEE):
  print "=== {0} ANALYSIS ===".format(("EE", "EB")[D == DataEB])
  print "Number of inactive channels : {0}".format(len(D.findInactiveChannels()))
  print "Number of active channels   : {0}".format(len(D.channels) - len(D.findInactiveChannels()))
  
  activekeys = []
  for k in sorted(D.getDataKeys()):
    if not len(D.channels) - len(D.findInactiveChannels()) == len(D.getChannelsByFlag('DP' + str(k))):
      activekeys.append(k)
      print "Data are available for the gain", str(k)

  print "Statistics of channels by problem classes: "
  print "{classn:45s} | {empty:5s} | {tags:12s}".format(classn = "Classes of pedestal problematic channels", empty="", tags="Short name")

  print "-----------------------------------------------------------------------------------------------------------"
  shorter = D.getChannelsByFlag
  for k in activekeys:
    print "{0:45s} | {1:5d} | {2:12s}".format("Dead pedestal channels", len(shorter("DP" + k)), "DP" + k)
    print "{0:45s} | {1:5d} | {2:12s}".format("Pedestal mean outside [170,230]", len(shorter("BP" + k)), "BP" + k)
    print "{0:45s} | {1:5d} | {2:12s}".format("Large RMS (noisy channels)", len(shorter("LR" + k)), "LR" + k)
    print "{0:45s} | {1:5d} | {2:12s}".format("Very large RMS (very noisy channels)", len(shorter("VLR" + k)), "VLR" + k)
    print "{0:45s} | {1:5d} | {2:12s}".format("Bad pedestal and noisy channels", len(shorter(["BP" + k, "LR" + k])), "BP" + k +"+LR" + k)
    print "{0:45s} | {1:5d} | {2:12s}".format("Bad pedestal and very noisy", len(shorter(["BP" + k,"VLR" + k])), "BP" + k + "+VLR" + k)
    print "-----------------------------------------------------------------------------------------------------------"
  del shorter
  
  print ""

  tpc = 0
  print "Get statistics by FLAGS:"
  for k in activekeys:
    for i in D.PEDESTAL_FLAGS:
      tpc += len([ c for c in D.getActiveChannels() if i+k in D.getChannel(c)["flags"]])
      print "  {0:8s} : {1:5d}".format(i + k, len(D.getChannelsByFlag(i + k)))
  print "Total problematic pedestal channels:", tpc

  print ""
  if not os.path.exists(outputdir + "/pedestals"):
    os.mkdir(outputdir + "/pedestals")
  for i in activekeys:
    for j in (True, False):
      h = D.get1DHistogram(i, None,  j)
      Data.saveHistogram(h, outputdir + "/pedestals/{0}{1}_EB.1D.pdf".format(i, ("", "_RMS")[j])) 
      del h
      plttype = ("barrel", "endcap")[D == DataEE]
      h = D.get2DHistogram(i, j, plottype = plttype)
      Data.saveHistogram(h, outputdir + "/pedestals/{0}{1}_{2}.2D.pdf".format(i, ("", "_RMS")[j],("EE","EB")[D == DataEB]), plttype) 
      del h
  print "    === END PEDESTALS {0} ===".format(("EE", "EB")[D == DataEB])
