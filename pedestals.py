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
numread = DataP.readPedestal(source)

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

print "Status flags are"
for x in sorted(FLAGS.keys()):
  print "  {0:3d} : {1}".format(x, FLAGS[x])
print ""
print "Get statistics by FLAGS:"
DataP.classifyChannels()
for x in sorted(FLAGS.keys()):
  count = len ( [a for a in DataP.getActiveChannels() if x in DataP.getChannel(a)["flags"]])
  print "  {0:3d} : {1:5d} channels".format(x, count)

print "=== END PEDESTALS ==="
