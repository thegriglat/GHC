#!/usr/bin/env python

import os
import sys
import shutil 
from Pedestal import *

if not os.path.exists("RESULTS"):
  os.mkdir("RESULTS")

print "=== PEDESTALS EB ==="

DataP = PedestalData()
source = "data/MON_PEDESTALS_DAT-60343-content.dat"
numall = DataP.readAllChannels("data/EB_all_ch.txt")
numread = DataP.readData(source)

DataP.setOption("pedestallimits", {"G1" : ((1, 0.2), (1.1, 3)), "G6" : ((1, 0.4), (1.3, 4)), "G12" : ((1, 0.5), (2.1, 6))})

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
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Large RMS (noisy channels)", len(shorter("LRG1")), "LRG1", len(shorter("LRG6")), "LRG6", len(shorter("LRG12")), "LRG12")
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Very large RMS (very noisy channels)", len(shorter("VLRG1")), "VLRG1", len(shorter("VLRG6")), "VLRG6", len(shorter("VLRG12")), "VLRG12")
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Bad pedestal and noisy channels", len(shorter(["BPG1", "LRG1"])), "BPG1+LRG1", len(shorter(["BPG6","LRG6"])), "BPG6+LRG6", len(shorter(["BPG12","LGR12"])), "BPG12+LRG12")
print "{0:40s} | {1:5d} | {2:12s} | {3:5d} | {4:12s} | {5:5d} | {6:12s}".format("Bad pedestal and very noisy", len(shorter(["BPG1","VLRG1"])), "BPG1+VLRG1", len(shorter(["BPG6","VLGR6"])), "BPG6+VLRG6", len(shorter(["BPG12","VLRG12"])), "BPG12+VLRG12")
print "-----------------------------------------------------------------------------------------------------------"
del shorter
print "Total problematic pedestal channels:", len([c for c in DataP.getActiveChannels() if len(DataP.getChannel(c)["flags"]) != 0])

print ""
print "Get statistics by FLAGS:"
for i in DataP.PEDESTAL_FLAGS:
  print "  {0:8s} : {1:5d}".format(i, len(DataP.getChannelsByFlag(i)))

print ""
if not os.path.exists("RESULTS/pedestals"):
  os.mkdir("RESULTS/pedestals")
for i in DataP.getDataKeys():
  for j in (True, False):
    h = DataP.get1DHistogram(i, None,  j)
    DataP.saveHistogram(h, "RESULTS/pedestals/1D_{0}{1}_EB.pdf".format(i, ("", "_RMS")[j])) 
    del h
    h = DataP.get2DHistogram(i, j, plottype = "barrel")
    DataP.saveHistogram(h, "RESULTS/pedestals/2D_{0}{1}_EB.pdf".format(i, ("", "_RMS")[j]), True) 
    del h

print "=== END PEDESTALS EB ==="
