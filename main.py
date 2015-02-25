#!/usr/bin/env python

import os
from data import *
       
os.mkdir("RESULTS")

print "=== PEDESTALS ==="

DataP = Data()
source = "data/MON_PEDESTALS.dat"
numall = DataP.readAllChannels("data/EB_all_ch.txt")
numread = DataP.readPedestal(source)

print "Number of inactive channels : {0}".format(len(DataP.findInactiveChannels()))
print "Number of inactive channels : {0}".format(numall - numread)

print "List of available keys: ", DataP.getDataKeys()
os.mkdir("RESULTS/pedestals")
for i in DataP.getDataKeys():
  for j in (True, False):
    h = DataP.doROOTAnalysis(i, None,  j)
    saveHistogram(h, "RESULTS/pedestals/{0}{1}.png".format(i, ("", "_RMS")[j])) 
    del h

print "=== END PEDESTALS ==="
print "=== TEST PULSE ==="

DataTP = Data()
source = "data/MON_TEST_PULSE.dat"
numall = DataTP.readAllChannels("data/EB_all_ch.txt")
numread = DataTP.readTestPulse(source)

print "Number of inactive channels : {0}".format(len(DataTP.findInactiveChannels()))
print "Number of inactive channels : {0}".format(numall - numread)

print "List of available keys: ", DataTP.getDataKeys()
os.mkdir("RESULTS/test_pulse")
for i in DataTP.getDataKeys():
  for j in (True, False):
    dimx = ((1000, 3000), (0, 20))[j]
    h = DataTP.doROOTAnalysis(i, dimx, j)
    saveHistogram(h, "RESULTS/test_pulse/{0}{1}.png".format(i, ("", "_RMS")[j]))
    del h

print "=== END TEST PULSE ==="
print "=== LASER BLUE ==="
DataLB = Data()
source = "data/MON_LASER_BLUE.dat"
numall = DataLB.readAllChannels("data/EB_all_ch.txt")
numread = DataLB.readLaserBlue(source)

print "Number of inactive channels : {0}".format(len(DataLB.findInactiveChannels()))
print "Number of inactive channels : {0}".format(numall - numread)

print "List of available keys: ", DataLB.getDataKeys()
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

