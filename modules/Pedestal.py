#!/usr/bin/env python

from Data import *

class PedestalData(Data):
  runtype = "pedestal"

  def readData(self, source):
    return self.readPedestal(source)    
  
  def getChannelFlags(self, channel):
    def PedestalComparison(key, deadlimits, badlimits):
      tmpflags = []
      if data[key][0] <= deadlimits[0] or data[key][1] <= deadlimits[1]:
        tmpflags.append("DP" + key)
      else:
        if data[key][1] >= badlimits[0] and data[key][1] < badlimits[1] and data[key][0] > deadlimits[0]:
          tmpflags.append("LR" + key)
        if data[key][1] > badlimits[1] and data[key][0] > deadlimits[0]:
          tmpflags.append("VLR" + key)
        if abs(data[key][0] - 200) >= 30 and data[key][0] > deadlimits[0]:
          tmpflags.append("BP" + key)
      return tmpflags
    data = self.channels[channel]["data"]
    flags = []
    if self.getOption("pedestallimits") != None:
      limits = self.getOption("pedestallimits")
    else:
      limits = {"G1" : ((1, 0.2), (1.1, 3)), "G6" : ((1, 0.4), (1.3, 4)), "G12" : ((1, 0.5), (2.1, 6))}
    flags += PedestalComparison("G1", limits["G1"][0], limits["G1"][1])
    flags += PedestalComparison("G6", limits["G6"][0], limits["G6"][1])
    flags += PedestalComparison("G12", limits["G12"][0], limits["G12"][1])
    return list(set(flags))

  def readPedestal(self, source = None):
    if source == None:
      return self.DBread(source)
    else:
      fd = open(source, 'r')
      print "Reading Pedestal data ..."
      n = 0
      for line in fd.readlines()[1:]:
        line = line.strip()
        try:
          IOV_ID, channelid, gain1, rms1, gain6, rms6, gain12, rms12, taskstatus = line.split()
        except:
          print "  Cannot parse line\n  '{0}'\n  for 9 fields!"
        if not self.channels.has_key(channelid):
          print "  Hmm. It seems channel {0} is not present in list of all channels. Continue ...".format(channelid)
        else:
          self.setChannelData(channelid, {"G1": [float(gain1), float(rms1)], "G6" : [float(gain6), float(rms6)], "G12" : [float(gain12), float(rms12)]})
          n = n + 1
      print "  Done. Processed {0} records.".format(n)
    return n

