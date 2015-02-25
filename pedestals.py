#!/usr/bin/env python

import os
import sys
import shutil 
from data import *

if not os.path.exists("RESULTS"):
  os.mkdir("RESULTS")

print "=== PEDESTALS ==="

DataP = Data()
source = "data/MON_PEDESTALS.dat"
numall = DataP.readAllChannels("data/EB_all_ch.txt")
numread = DataP.readData('pedestal', source)

print "Number of inactive channels : {0}".format(len(DataP.findInactiveChannels()))
print "Number of inactive channels : {0}".format(numall - numread)

print "List of available keys: ", DataP.getDataKeys()
if not os.path.exists("RESULTS/pedestals"):
  s.mkdir("RESULTS/pedestals")
for i in DataP.getDataKeys():
  for j in (True, False):
    h = DataP.doROOTAnalysis(i, None,  j)
    saveHistogram(h, "RESULTS/pedestals/{0}{1}.png".format(i, ("", "_RMS")[j])) 
    del h

print "Get statistics by FLAGS:"
DataP.classifyChannels()
stats = {}
for x in DataP.getActiveChannels():
  for fl in DataP.getChannel(x)["flags"]:
    if stats.has_key(fl):
      stats[fl] += 1
    else:
      stats[fl] = 0

for i in sorted(stats.keys()):
  print "  {0:8s} : {1:5d}".format(i, stats[i])
print "=== END PEDESTALS ==="
