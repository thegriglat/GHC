#!/usr/bin/env python

from data import *
       
Data = Data()
numall = Data.readAllChannels("data/EB_all_ch.txt")
numread = Data.readEBPedestalData("data/MON_PEDESTALS.dat")


print "Number of inactive channels : {0}".format(len(Data.findInactiveChannels()))
print "Number of inactive channels : {0}".format(numall - numread)

Data.doROOTAnalysis("G1")
Data.doROOTAnalysis("G6")
Data.doROOTAnalysis("G12")
