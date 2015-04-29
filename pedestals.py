#!/usr/bin/env python

import os
import sys
import shutil
import argparse

sys.path.append("modules")
from Pedestal import *

if not os.path.exists("RESULTS"):
  os.mkdir("RESULTS")

parser = argparse.ArgumentParser()
parser.add_argument('runs', metavar="RUN", nargs="+", help = "Run(s) to analyse (can be <num> or <num>:<gain>. Use '-' for reading from stdin")
parser.add_argument('-c', '--dbstr', help="Connection string to DB (oracle://user/pass@db)", dest='dbstr')
parser.add_argument('-bl','--barrel-limits', dest="barrel_limits", help = "Limits for barrel")
parser.add_argument('-el','--endcap-limits', dest="endcap_limits", help = "Limits for endcap")
args = parser.parse_args()

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
if not args.barrel_limits is None:
  DataEB.setOption("pedestallimits", {"G1" : ((1, 0.2), (1.1, 3)), "G6" : ((1, 0.4), (1.3, 4)), "G12" : ((1, 0.5), (2.1, 6))})
else:
  DataEB.setOption("pedestallimits", args.barrel_limits)
if not args.endcap_limits is None: 
  DataEE.setOption("pedestallimits", {"G1" : ((1, 0.2), (1.5, 4)), "G6" : ((1, 0.4), (2, 5)),   "G12" : ((1, 0.5), (3.2, 7))})
else:
  DataEE.setOption("pedestallimits", args.endcap_limits)

for D in (DataEB, DataEE):
  print "    === {0} ANALYSIS ===".format(("EE", "EB")[D == DataEB])
  print "Number of inactive channels : {0}".format(len(D.findInactiveChannels()))
  print "Number of active channels   : {0}".format(len(D.channels) - len(D.findInactiveChannels()))

  print "Data are available for the followings gain/keys: ", ", ".join(sorted(D.getDataKeys()))

  print "Statistics of channels by problem classes: "
  print "{classn:40s} | {empty:5s} | {tags:12s} | {empty:5s} | {tags:12s} | {empty:5s} | {tags:12s}".format(classn = "Classes of pedestal problematic channels", empty="", tags="Short name")

  print "-----------------------------------------------------------------------------------------------------------"
  shorter = D.getChannelsByFlag
  print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Dead pedestal channels", len(shorter("DPG1")), "DPG1", len(shorter("DPG6")), "DPG6", len(shorter("DPG12")), "DPG12")
  print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Pedestal mean outside [170,230]", len(shorter("BPG1")), "BPG1", len(shorter("BPG6")), "BPG6", len(shorter("BPG12")), "BPG12")
  print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Large RMS (noisy channels)", len(shorter("LRG1")), "LRG1", len(shorter("LRG6")), "LRG6", len(shorter("LRG12")), "LRG12")
  print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Very large RMS (very noisy channels)", len(shorter("VLRG1")), "VLRG1", len(shorter("VLRG6")), "VLRG6", len(shorter("VLRG12")), "VLRG12")
  print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Bad pedestal and noisy channels", len(shorter(["BPG1", "LRG1"])), "BPG1+LRG1", len(shorter(["BPG6","LRG6"])), "BPG6+LRG6", len(shorter(["BPG12","LGR12"])), "BPG12+LRG12")
  print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Bad pedestal and very noisy", len(shorter(["BPG1","VLRG1"])), "BPG1+VLRG1", len(shorter(["BPG6","VLGR6"])), "BPG6+VLRG6", len(shorter(["BPG12","VLRG12"])), "BPG12+VLRG12")
  print "-----------------------------------------------------------------------------------------------------------"
  del shorter
  print "Total problematic pedestal channels:", len([c for c in D.getActiveChannels() if len(D.getChannel(c)["flags"]) != 0])

  print ""
  print "Get statistics by FLAGS:"
  for i in D.PEDESTAL_FLAGS:
    print "  {0:8s} : {1:5d}".format(i, len(D.getChannelsByFlag(i)))
  
  print ""
  if not os.path.exists("RESULTS/pedestals"):
    os.mkdir("RESULTS/pedestals")
  for i in D.getDataKeys():
    for j in (True, False):
      h = D.get1DHistogram(i, None,  j)
      Data.saveHistogram(h, "RESULTS/pedestals/{0}{1}_EB.1D.pdf".format(i, ("", "_RMS")[j])) 
      del h
      h = D.get2DHistogram(i, j, plottype = "barrel")
      Data.saveHistogram(h, "RESULTS/pedestals/{0}{1}_EB.2D.pdf".format(i, ("", "_RMS")[j]), "barrel") 
      del h
  print "    === END PEDESTALS {0} ===".format(("EE", "EB")[D == DataEB])
