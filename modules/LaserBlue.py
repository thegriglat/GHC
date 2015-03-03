#!/usr/bin/env python

from Data import *

class LaserBlueData(Data):
  runtype = "laserblue"
  description = "Laser"
  average = {}

  def readData(self, source):
    return self.readLaserBlue(source)    
  
  def getAvgGain(self, gain):
    if self.average.has_key(gain):
      return self.average[gain]
    else:
      sum = 0
      ach = self.getActiveChannels()
      for c in ach:
        sum += self.channels[c]["data"][gain][0]
      self.average[gain] = sum / float(len(ach))
      return self.average[gain]

  def getChannelFlags(self, channel):
    data = self.channels[channel]["data"]
    flags = []
    if data["Laser"][0] <= 0:
      flags.append("DLAMPL")
    if data["Laser"][0] / self.getAvgGain("Laser") < 0.1 and data["Laser"][0] > 0:
      flags.append("SLAMPL")
    if data["Laser"][0] > 0 and data["Laser"][1] / float(data["Laser"][0]) > 0.2:
      flags.append("LLERRO")
    return list(set(flags))

  def readLaserBlue(self, source = None):
    if source == None:
      return DBread(source)
    else:
      fd = open(source, 'r')
      print "Reading Laser blue data ..."
      n = 0
      for line in fd.readlines():
        line = line.strip()
        try:
          IOV_ID, channelid, gain12, rms12, APD_OVER_PN_MEAN, APD_OVER_PN_RMS, taskstatus = line.split()
        except:
          print "  Cannot parse line\n  '{0}'\n  for 7 fields!"
        if not self.channels.has_key(channelid):
          pass
#          print "  Hmm. It seems channel {0} is not present in list of all channels. Continue ...".format(channelid)
        else:
          self.setChannelData(channelid, {"Laser": [float(gain12), float(rms12)], "APD.DN" : [float(APD_OVER_PN_MEAN), float(APD_OVER_PN_RMS)]})
          self.channels[channelid]["active"] = True
          n = n + 1
      print "  Done. Processed {0} records.".format(n)
    return n


