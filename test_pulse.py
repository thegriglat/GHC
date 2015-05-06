#!/usr/bin/env python

import os
import sys
import shutil
import argparse

sys.path.append("modules")
from TestPulse  import *

if not os.path.exists("RESULTS"):
  os.mkdir("RESULTS")

parser = argparse.ArgumentParser()
parser.add_argument('runs', metavar="RUN", nargs="+", help = "Run(s) to analyse. Use '-' for reading from stdin")
parser.add_argument('-c', '--dbstr', help="Connection string to DB (oracle://user/pass@db)", dest='dbstr')
args = parser.parse_args()

if args.runs == ['-']:
    source = sys.stdin
else:
    runs = args.runs
    if args.dbstr is None:
      print "Please specify --dbstr!"
      sys.exit(0)
    source = args.dbstr

print "=== TEST PULSE ==="
DataEB = TestPulseData()
DataEE = TestPulseData()
DataEB.readAllChannels("data/EB_all_ch.txt")
DataEB.readAllChannels("data/EE_all_ch.txt")

DataEB.readTestPulse(source, runnum = runs)
DataEE.readTestPulse(source, runnum = runs)

for D in (DataEB, DataEE):
  print "    === TEST PULSE {0} ANALYSIS ===".format(("EE","EB")[D == DataEB])
  print "Number of inactive channels : {0}".format(len(D.findInactiveChannels()))

  activekeys = []
  for k in sorted(D.getDataKeys()):
    if not len(D.channels) - len(D.findInactiveChannels()) == len(D.getChannelsByFlag('DTP' + str(k))):
      activekeys.append(k)
      print "Data are available for the gain", str(k)

  print "Statistics of channels by problem classes: "
  print "{classn:40s} | {empty:5s} | {tags:12s}".format(classn = "Classes of Test Pulse problematic channels", empty="", tags="Short name")

  print "-----------------------------------------------------------------------------------------------------------"
  shorter = D.getChannelsByFlag
  for k in activekeys:
    print "{0:40s} | {1:5d} | {2:12s}".format("Dead TP channels", len(shorter("DTP" + k)), "DTP" + k)
    print "{0:40s} | {1:5d} | {2:12s}".format("Low TP amplitude", len(shorter("STP" + k)), "STP" + k)
    print "{0:40s} | {1:5d} | {2:12s}".format("Large TP amplitude", len(shorter("LTP" + k)), "LTP" + k)
    print "-----------------------------------------------------------------------------------------------------------"
  del shorter

  print "Total problematic pedestal channels:", len([c for c in D.getActiveChannels() if len(D.getChannel(c)["flags"]) != 0])

  print "Get statistics by FLAGS:"
  for k in activekeys:
    for i in D.TESTPULSE_FLAGS:
      print "  {0:8s} : {1:5d}".format(i + k, len(D.getChannelsByFlag(i + k)))

  if not os.path.exists("RESULTS/test_pulse"):
    os.mkdir("RESULTS/test_pulse")
  for i in activekeys:
    for j in (True, False):
      dimx = ((1000, 3000), (0, 20))[j]
      h = D.get1DHistogram(i, dimx, j)
      Data.saveHistogram(h, "RESULTS/test_pulse/{0}{1}_{2}.1D.pdf".format(i, ("", "_RMS")[j], ("EE","EB")[D == DataEB]))
      del h
      h = D.get2DHistogram(i, j, plottype = "barrel")
      Data.saveHistogram(h, "RESULTS/test_pulse/{0}{1}_{2}.2D.pdf".format(i, ("", "_RMS")[j], ("EE","EB")[D == DataEB]), plottype = "barrel")
      del h
  
  print "=== END TEST PULSE {0} ===".format(("EE","EB")[D == DataEB])

