#!/usr/bin/env python

from data import *
       
Data = Data()
numall = Data.readAllChannels("data/EB_all_ch.txt")
numread = Data.readEBPedestalData("data/MON_PEDESTALS.dat")


print numall-numread

print len(Data.findInactiveChannels())


