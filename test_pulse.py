#!/usr/bin/env python

import os
import sys
import shutil
from TestPulse  import *

if not os.path.exists("RESULTS"):
  os.mkdir("RESULTS")

print "=== TEST PULSE ==="

DataTP = TestPulseData()
source = "data/MON_TEST_PULSE_DAT-60342-content.dat"
numall = DataTP.readAllChannels("data/EB_all_ch.txt")
numread = DataTP.readData(source)

print "Number of inactive channels : {0}".format(len(DataTP.findInactiveChannels()))
print "Number of inactive channels : {0}".format(numall - numread)

print "List of available keys: ", DataTP.getDataKeys()

print "Statistics of channels by problem classes: "
print "{classn:40s} | {empty:5s} | {tags:12s} | {empty:5s} | {tags:12s} | {empty:5s} | {tags:12s}".format(classn = "Classes of Test Pulse problematic channels",         empty="", tags="Short name")

print "-----------------------------------------------------------------------------------------------------------"
shorter = DataTP.getChannelsByFlag
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Dead TP channels", len(shorter("DTPG1")), "DTPG1", len(shorter("DTPG6")), "DTPG6",  len(shorter("DTPG12")), "DTPG12")
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Low TP amplitude", len(shorter("STPG1")), "STPG1", len(shorter("STPG6")), "STPG6", len(shorter("STPG12")), "STPG12")
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Large TP amplitude", len(shorter("LTPG1")), "LTPG1", len(shorter("LTPG6")),      "LTPG6", len(shorter("LTPG12")), "LTPG12")
print "-----------------------------------------------------------------------------------------------------------"
del shorter

print "Total problematic pedestal channels:", len([c for c in DataTP.getActiveChannels() if len(DataTP.getChannel(c)["flags"]) != 0])

if not os.path.exists("RESULTS/test_pulse"):
  os.mkdir("RESULTS/test_pulse")
for i in DataTP.getDataKeys():
  for j in (True, False):
    dimx = ((1000, 3000), (0, 20))[j]
    h = DataTP.get1DHistogram(i, dimx, j)
    DataTP.saveHistogram(h, "RESULTS/test_pulse/1D_{0}{1}.pdf".format(i, ("", "_RMS")[j]))
    del h
    h = DataTP.get2DHistogram(i, j, plottype = "barrel")
    DataTP.saveHistogram(h, "RESULTS/test_pulse/2D_{0}{1}.pdf".format(i, ("", "_RMS")[j]), True)
    del h

print "=== END TEST PULSE ==="

