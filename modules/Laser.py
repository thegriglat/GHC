#!/usr/bin/env python

import Data 

class LaserData(Data.Data):

  def __init__(self):
    super(LaserData, self).__init__()
    self.runtype = "laser"
    self.description = "Laser"
    self.average = {}

  def readData(self, source):
    return self.readLaser(source)    
  
  def getAvgGain(self, gain):
    """
      Returns average value for <gain>. The function caches results.
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

  def readChannel(self, str):
    str = str.strip()
    try:
      IOV_ID, channelid, gain12, rms12, APD_OVER_PN_MEAN, APD_OVER_PN_RMS, taskstatus = str.split()
    except:
      log.error( "  Cannot parse line\n  '{0}'\n  for 7 fields!")
    if not self.channels.has_key(channelid):
      return False
    else:
      self.setChannelData(channelid, {"Laser": [float(gain12), float(rms12)], "APD/PN" : [float(APD_OVER_PN_MEAN), float(APD_OVER_PN_RMS)]})
      self.channels[channelid]["active"] = True
      return True

  def readLaser(self, source = None):
    if source == None:
      return DBread(source)
    else:
      log.info ("Reading Laser blue data ...")
      n = 0
      for line in source.readlines():
        if self.readChannel(line):
          n = n + 1
      log.info( "  Done. Processed {0} records.".format(n))
    return n


