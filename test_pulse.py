#!/usr/bin/env python

import os
import sys
import shutil
from data import *

if not os.path.exists("RESULTS"):
  os.mkdir("RESULTS")

print "=== TEST PULSE ==="

DataTP = Data()
source = "data/MON_TEST_PULSE.dat"
numall = DataTP.readAllChannels("data/EB_all_ch.txt")
numread = DataTP.readTestPulse(source)

print "Number of inactive channels : {0}".format(len(DataTP.findInactiveChannels()))
print "Number of inactive channels : {0}".format(numall - numread)

print "List of available keys: ", DataTP.getDataKeys()
if not os.path.exists("RESULTS/test_pulse"):
  os.mkdir("RESULTS/test_pulse")
for i in DataTP.getDataKeys():
  for j in (True, False):
    dimx = ((1000, 3000), (0, 20))[j]
    h = DataTP.get1DHistogram(i, dimx, j)
    saveHistogram(h, "RESULTS/test_pulse/{0}{1}.pdf".format(i, ("", "_RMS")[j]))
    del h

print "=== END TEST PULSE ==="

