#!/usr/bin/env python

import ROOT

FLAGS = {
     0   :  "Pedestal G1 <= 1 or RMS G1 <= 0.2  ADC counts (dead channels)",
     2   :  "Pedestal G1 < 170 or > 230 ADC counts",
     4   :  "RMS Pedestal G1 > 1.1 ADC counts",
     8   :  "RMS Pedestal G1 > 3.0 ADC counts",
     8   :  "Pedestal G6 <= 1 or RMS G6 <= 0.4  ADC counts (dead channels)",
     16  :  "Pedestal G6 < 170 or > 230 ADC counts",
     32  :  "RMS Pedestal G6 > 1.3 ADC counts",
     64  :  "RMS Pedestal G6 > 4.0 ADC counts",
     64  :  "Pedestal G12 <= 1 or RMS G12 <= 0.5 ADC counts (dead channels)", 
     128 :  "Pedestal G12 < 170 or > 230 ADC counts",
     256 :  "RMS Pedestal G12 > 2.1 ADC counts",
     512 :  "RMS Pedestal G12 > 6.0 ADC counts"
}

PEDESTAL_FLAGS = ["DPG1", "BPG1", "LRG1", "VLRG1",
          "DPG6", "BPG6", "LRG6", "VLRG6",
          "DPG12", "BPG12", "LRG12", "VLRG12"
]
TESTPULSE_FLAGS = [ "DTPG1", "STPG1", "LTPG1",
                    "DTPG6", "STPG6", "LTPG6",
                    "DTPG12","STPG12","LTPG12"
]

BLUELASER_FLAGS = ["DLAMPL", "SLAMPL", "LLERRO"]

HVOFF_FLAGS = ["-"]

class Data:
  channels = {}
  average  = {}
  isClassified = False
  # channel = {
  #   "data"   : {
  #       "G1"  : [value, rms],
  #       "G6"  : [value, rms],
  #       "G12" : [value, rms] 
  #   }
  # }


  def __init__(self):
    pass

  def getTT(self, channel):
    channel = str(channel)
    l1 = self.getXtal(channel)
    l2 = self.getEB(channel)
    row = (l1 - 1) / 20 + 1
    col = (l1 - 1) % 20 + 1
    TTrow = (row - 1) / 5
    TTcol = (col - 1) / 5
    TT = TTrow * 4 + TTcol + 1
    return TT

  def getXtal(self, channel):
    return int(str(channel)[-4:])

  def getEB(self, channel):
    return int(str(channel)[-6:-4])

  def findInactiveChannels(self):
    return [ch for ch in self.channels.keys() if self.isInactive(ch)]
  
  def isActive(self, channel):
    return [True, False][len(self.channels[channel]["data"].keys()) == 0]

  def isInactive(self, channel):
    return not self.isActive(channel)

  def getActiveChannels(self):
    return [ a for a in self.channels.keys() if self.isActive(a)]

  def getNewChannel(self, data = {}):
    return {"data" : data}

  def readAllChannels(self, filename):
    fd = open(filename, 'r')
    print "Getting list of all channels ..."
    n = 0
    for line in fd.readlines():
      line = line.strip()
      self.channels[line] = self.getNewChannel()
      n = n + 1
    print "  Done. Processed {0} records.".format(n)
    return n

  def setChannelData(self, channel, data):
    self.channels[channel]["data"] = data
  
  def readData(self, type,  source = None):
    if type == "pedestal":
      self.runtype = type
      return self.readPedestal(source)
    elif type == "pedestalhvoff":
      self.runtype = "pedestal"
      return self.readPedestalHVOFF(source)
    elif type == "testpulse":
      self.runtype == type
      return self.readTestPulse(source)
    elif type == "laserblue":
      self.runtype = type
      return self.readLaserBlue(source)
    else:
      print "Cannot parse data type '{}'! ".format(type)
      return False
  
  def getDataKeys(self):
    return self.channels[self.getActiveChannels()[0]]["data"].keys()

  def readPedestal(self, source = None, HV = False):
    if source == None:
      return DBread(source)
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
          self.channels[channelid]["HV"] = HV
          n = n + 1
      print "  Done. Processed {0} records.".format(n)
    return n

  def readTestPulse(self, source = None):
    if source == None:
      return DBread(source)
    else:
      fd = open(source, 'r')
      print "Reading Test Pulse data ..."
      n = 0
      for line in fd.readlines():
        line = line.strip()
        try:
          IOV_ID, channelid, gain1, gain6, gain12, rms1, rms6, rms12, taskstatus = line.split()
        except:
          print "  Cannot parse line\n  '{0}'\n  for 9 fields!"
        if not self.channels.has_key(channelid):
          print "  Hmm. It seems channel {0} is not present in list of all channels. Continue ...".format(channelid)
        else:
          self.setChannelData(channelid, {"G1": [float(gain1), float(rms1)], "G6" : [float(gain6), float(rms6)], "G12" : [float(gain12), float(rms12)]})
          n = n + 1
      print "  Done. Processed {0} records.".format(n)
    return n

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
          print "  Hmm. It seems channel {0} is not present in list of all channels. Continue ...".format(channelid)
        else:
          self.setChannelData(channelid, {"G12": [float(gain12), float(rms12)], "APD/DN" : [APD_OVER_PN_MEAN, APD_OVER_PN_RMS]})
          self.channels[channelid]["active"] = True
          n = n + 1
      print "  Done. Processed {0} records.".format(n)
    return n


  def DBread(source):
    return 0

  def get1DHistogram(self, key, dimx = None, RMS = False):
    d1 =("", " (RMS)")[RMS]
    name = "{0}{1}".format(key, d1)
    activech = self.getActiveChannels()
    if dimx == None:
      dimx = ((150, 250), (0, 5))[RMS]
    hist = ROOT.TH1F(name, name, 100, dimx[0], dimx[1]) 
    for ch in activech:
      try:
        hist.Fill(self.channels[ch]["data"][key][RMS])
      except:
        print "  Cannot add value from channel {0} and key {1} {2}!".format(ch, key, ("", "(RMS)")[RMS])
    return hist

  def getChannelFlags(self, channel):
    data = self.channels[channel]["data"]
    flags = []
    if self.runtype == "pedestal":
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
      flags += PedestalComparison("G1", (1, 0.2), (1.1, 3))
      flags += PedestalComparison("G6", (1, 0.4), (1.3, 4))
      flags += PedestalComparison("G12", (1, 0.5), (2.1, 6))
    elif self.runtype == "testpulse":
      for i in ('1', '6', '12'):
        if data["G" + i][0] <= 0:
          flags.append("DTPG" + i)
        if data["G" + i][0] / self.getAvgGain("G" + i) <= 0.5:
          flags.append("STPG" + i)
        if data["G" + i][0] / self.getAvgGain("G" + i) >= 1.5:
          flags.append("LTPG" + i)
    elif self.runtype == "laserblue":
      if data["G12"][0] <= 0:
        flags.append("DLAMPL")
      if data["G12"][0] / self.getAvgGain("G12") < 0.1 and data["G12"][0] > 0:
        flags.append("SLAMPL")
      if data["G12"][0] > 0 and data["G12"][1] / float(data["G12"][0]) > 0.2:
        flags.append("LLERRO")
    return list(set(flags))

  def getAvgGain(self, gain):
    sum = 0
    ach = self.getActiveChannels()
    for c in ach:
      sum += self.channels[c]["data"][gain][0]
    if not self.average.has_key(gain):
      self.average[gain] = sum / float(len(ach))
      return self.average[gain]
    else:
      return self.average[gain]

  def getChannel(self, channel):
    return self.channels[channel]

  def getChannelsByFlag(self, flag):
    return [a for a in self.channels.keys() if flag in self.channels[a]["flags"]]

  def classifyChannels(self):
    for c in self.getActiveChannels():
      self.channels[c]["flags"] = self.getChannelFlags(c)
    self.isClassified = True

  def getChannelsByFlag(self, flags):
    def isChannelHasFlags(channel, flags):
      if not isinstance(flags, list):
        flags = [flags]
      for f in flags:
        if not f in self.channels[channel]["flags"]:
          return False
      return True
    if not isinstance(flags, list):
      flags = [flags]
    if not self.isClassified:
      self.classifyChannels()
    t = [ c for c in self.getActiveChannels() if isChannelHasFlags(c, flags)]
    return list(set(t)) 

def saveHistogram(histogram, filename):
  ROOT.gROOT.SetBatch(ROOT.kTRUE)
  try:
    c = ROOT.TCanvas()
    c.SetLogy()
    histogram.Draw()
    c.Update()
    c.SaveAs(filename)
    return True
  except:
    print "Cannot save '{0}'into {1}".format(repr(hist),filename)
    return False

