#!/usr/bin/env python

from data import *
       
Data = Data()
source = "data/MON_PEDESTALS.dat"
numall = Data.readAllChannels("data/EB_all_ch.txt")
numread = Data.readEBPedestalData(source)


print "Number of inactive channels : {0}".format(len(Data.findInactiveChannels()))
print "Number of inactive channels : {0}".format(numall - numread)

for i in ("G1", "G6", "G12"):
  for j in (True, False):
    h = Data.doROOTAnalysis(i, j)
    saveHistogram(h, "{0}{1}.png".format(i, ("", "_RMS")[j])) 
