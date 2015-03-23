#!/usr/bin/env python

import os
import sys
import shutil

sys.path.append("modules")
from TestPulse  import *

if not os.path.exists("RESULTS"):
  os.mkdir("RESULTS")

if len(sys.argv) > 2:
  print "Please provide input file name or use - as stdin"
  sys.exit(0)
else: 
  if len(sys.argv) == 1 or sys.argv[1] == "-": 
    source = sys.stdin
  else:
    source = open(sys.argv[1])


print "=== TEST PULSE ==="

DataEB = TestPulseData()
DataEE = TestPulseData()
DataEB.readAllChannels("data/EB_all_ch.txt")
DataEB.readAllChannels("data/EE_all_ch.txt")

for l in source.readlines()[1:]:
  l = l.strip()
  DataEB.readChannel(l)
  DataEE.readChannel(l)

for D in (DataEB, DataEE):
  print "    === TEST PULSE {0} ANALYSIS ===".format(("EE","EB")[D == DataEB])
  print "Number of inactive channels : {0}".format(len(D.findInactiveChannels()))
  print "List of available keys: ", D.getDataKeys()

  print "Statistics of channels by problem classes: "
  print "{classn:40s} | {empty:5s} | {tags:12s} | {empty:5s} | {tags:12s} | {empty:5s} | {tags:12s}".format(classn = "Classes of Test Pulse problematic channels",         empty="", tags="Short name")

  print "-----------------------------------------------------------------------------------------------------------"
  shorter = D.getChannelsByFlag
  print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Dead TP channels", len(shorter("DTPG1")), "DTPG1", len(shorter("DTPG6")), "DTPG6",  len(shorter("DTPG12")), "DTPG12")
  print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Low TP amplitude", len(shorter("STPG1")), "STPG1", len(shorter("STPG6")), "STPG6", len(shorter("STPG12")), "STPG12")
  print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Large TP amplitude", len(shorter("LTPG1")), "LTPG1", len(shorter("LTPG6")),      "LTPG6", len(shorter("LTPG12")), "LTPG12")
  print "-----------------------------------------------------------------------------------------------------------"
  del shorter

  print "Total problematic pedestal channels:", len([c for c in D.getActiveChannels() if len(D.getChannel(c)["flags"]) != 0])

  if not os.path.exists("RESULTS/test_pulse"):
    os.mkdir("RESULTS/test_pulse")
  for i in D.getDataKeys():
    for j in (True, False):
      dimx = ((1000, 3000), (0, 20))[j]
      h = D.get1DHistogram(i, dimx, j)
      Data.saveHistogram(h, "RESULTS/test_pulse/{0}{1}_{2}.1D.pdf".format(i, ("", "_RMS")[j], ("EE","EB")[D == DataEB]))
      del h
      h = D.get2DHistogram(i, j, plottype = "barrel")
      Data.saveHistogram(h, "RESULTS/test_pulse/{0}{1}_{2}.2D.pdf".format(i, ("", "_RMS")[j], ("EE","EB")[D == DataEB]), plottype = "barrel")
      del h
  
  print "=== END TEST PULSE {0} ===".format(("EE","EB")[D == DataEB])

