#!/usr/bin/env python

import os
import sys
import shutil 
from data import *

if not os.path.exists("RESULTS"):
  os.mkdir("RESULTS")

print "=== PEDESTALS ==="

DataP = Data()
source = "data/MON_PEDESTALS_DAT-60343-content.dat"
numall = DataP.readAllChannels("data/EB_all_ch.txt")
numread = DataP.readData('pedestal', source)

print "Number of inactive channels : {0}".format(len(DataP.findInactiveChannels()))
print "Number of inactive channels : {0}".format(numall - numread)
print "Number of active channels   : {0}".format(numread)

print "Data are available for the followings gain/keys: ", ", ".join(sorted(DataP.getDataKeys()))

print "Statistics of channels by problem classes: "
print "{classn:40s} | {empty:5s} | {tags:12s} | {empty:5s} | {tags:12s} | {empty:5s} | {tags:12s}".format(classn = "Classes of pedestal problematic channels", empty="", tags="Short name")

print "-----------------------------------------------------------------------------------------------------------"
shorter = DataP.getChannelsByFlag
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Dead pedestal channels", len(shorter("DPG1")), "DPG1", len(shorter("DPG6")), "DPG6", len(shorter("DPG12")), "DPG12")
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Pedestal mean outside [170,230]", len(shorter("BPG1")), "BPG1", len(shorter("BPG6")), "BPG6", len(shorter("BPG12")), "BPG12")
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Large RMS (moisy channels)", len(shorter("LRG1")), "LRG1", len(shorter("LRG6")), "LRG6", len(shorter("LRG12")), "LRG12")
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Very large RMS (very noisy channels)", len(shorter("VLRG1")), "VLRG1", len(shorter("VLRG6")), "VLRG6", len(shorter("VLRG12")), "VLRG12")
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Bad pedestal and noisy channels", len(shorter(["BPG1", "LRG1"])), "BPG1+LRG1", len(shorter(["BPG6","LRG6"])), "BPG6+LRG6", len(shorter(["BPG12","LGR12"])), "BPG12+LRG12")
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Bad pedestal and very noisy", len(shorter(["BPG1","VLRG1"])), "BPG1+VLRG1", len(shorter(["BPG6","VLGR6"])), "BPG6+VLRG6", len(shorter(["BPG12","VLRG12"])), "BPG12+VLRG12")
print "-----------------------------------------------------------------------------------------------------------"

del shorter


print "Get statistics by FLAGS:"
for i in PEDESTAL_FLAGS:
  print "  {0:8s} : {1:5d}".format(i, len(DataP.getChannelsByFlag(i)))


if not os.path.exists("RESULTS/pedestals"):
  os.mkdir("RESULTS/pedestals")
for i in DataP.getDataKeys():
  for j in (True, False):
    h = DataP.get1DHistogram(i, None,  j)
    saveHistogram(h, "RESULTS/pedestals/{0}{1}.png".format(i, ("", "_RMS")[j])) 
    del h


print "=== END PEDESTALS ==="
