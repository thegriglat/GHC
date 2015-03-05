#!/usr/bin/env python

import os
import sys
import shutil

sys.path.append("modules")
from LaserBlue import *

if not os.path.exists("RESULTS"):
  os.mkdir("RESULTS")

print "=== LASER BLUE ==="
DataLB = LaserBlueData()
source = "data/MON_LASER_BLUE.dat"
numall = DataLB.readAllChannels("data/EE_all_ch.txt")
numread = DataLB.readData(source)

print "Number of inactive channels : {0}".format(len(DataLB.findInactiveChannels()))
print "Number of inactive channels : {0}".format(numall - numread)

print "List of available keys: ", DataLB.getDataKeys()

print "Getting info per error key :"
for i in DataLB.LASERBLUE_FLAGS:
  print "{0:15s} : {1:5d}".format(i, len(DataLB.getChannelsByFlag(i)))

if not os.path.exists("RESULTS/laser_blue"):
  os.mkdir("RESULTS/laser_blue")
for i in DataLB.getDataKeys():
  for j in (True, False):
    if i == "Laser":
      dimx =  ((0, 6000), (0, 200))[j]
    else:
      dimx =  ((0, 5), (0, 0.1))[j]
    h = DataLB.get1DHistogram(i, dimx, j)
    Data.saveHistogram(h, "RESULTS/laser_blue/{0}{1}_EE.1D.pdf".format(i.replace("/", "."), ("", "_RMS")[j]))
    del h
    h = DataLB.get2DHistogram(i, j, plottype="endcap")
    Data.saveHistogram(h, "RESULTS/laser_blue/{0}{1}_EE.2D.pdf".format(i.replace("/","."), ("", "_RMS")[j]), plottype = "endcap")

print "=== END LASER BLUE ==="


