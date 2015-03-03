#!/usr/bin/env python

from Data import *

class TestPulseData(Data):
  runtype = "testpulse"
  description = "Test Pulse"
  average = {}

  def readData(self, source):
    return self.readTestPulse(source)    
  
  def getChannelFlags(self, channel):
    data = self.channels[channel]["data"]
    flags = []
    for i in ('1', '6', '12'):
      if data["G" + i][0] <= 0:
        flags.append("DTPG" + i)
      if data["G" + i][0] / self.getAvgGain("G" + i) <= 0.5:
        flags.append("STPG" + i)
      if data["G" + i][0] / self.getAvgGain("G" + i) > 1.5:
        flags.append("LTPG" + i)
    return list(set(flags))

  def getAvgGain(self, gain):
    """
      Returns average  value for <gain>. The function caches results.
    """
    if self.average.has_key(gain):
      return self.average[gain]
    else:
      sum = 0
      ach = self.getActiveChannels()
      for c in ach:
        sum += self.channels[c]["data"][gain][0]
      self.average[gain] = sum / float(len(ach))
      return self.average[gain]

  def readTestPulse(self, source = None):
    if source == None:
      return self.DBread(source)
    else:
      fd = open(source, 'r')
      print "Reading Test Pulse data ..."
      n = 0
      for line in fd.readlines()[1:]:
        line = line.strip()
        try:
          IOV_ID, channelid, gain1, gain6, gain12, rms1, rms6, rms12, taskstatus = line.split()
        except:
          print "  Cannot parse line\n  '{0}'\n  for 9 fields!"
        if not self.channels.has_key(channelid):
          pass
#          print "  Hmm. It seems channel {0} is not present in list of all channels. Continue ...".format(channelid)
        else:
          self.setChannelData(channelid, {"G1": [float(gain1), float(rms1)], "G6" : [float(gain6), float(rms6)], "G12" : [float(gain12), float(rms12)]})
          n = n + 1
      print "  Done. Processed {0} records.".format(n)
    return n

