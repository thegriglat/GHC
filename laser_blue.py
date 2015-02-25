#!/usr/bin/env python

import os
import sys
import shutil
from data import *

if not os.path.exists("RESULTS"):
  os.mkdir("RESULTS")

print "=== LASER BLUE ==="
DataLB = Data()
source = "data/MON_LASER_BLUE.dat"
numall = DataLB.readAllChannels("data/EB_all_ch.txt")
numread = DataLB.readLaserBlue(source)

print "Number of inactive channels : {0}".format(len(DataLB.findInactiveChannels()))
print "Number of inactive channels : {0}".format(numall - numread)

print "List of available keys: ", DataLB.getDataKeys()
if not os.path.exists("RESULTS/laser_blue"):
  os.mkdir("RESULTS/laser_blue")
for i in DataLB.getDataKeys():
  for j in (True, False):
    if i == "LaserBlue":
      dimx =  ((0, 6000), (0, 200))[j]
    else:
      dimx =  ((0, 5), (0, 0.1))[j]
    h = DataLB.doROOTAnalysis(i, dimx, j)
    saveHistogram(h, "RESULTS/laser_blue/{0}{1}.png".format(i, ("", "_RMS")[j]))
    del h

print "=== END LASER BLUE ==="


