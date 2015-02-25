#!/usr/bin/env python

import ROOT

FLAGS = {
     0   :  "Pedestal G1 <= 1 or RMS G1 <= 0.2  ADC counts",
     2   :  "Pedestal G1 < 170 or > 230 ADC counts",
     4   :  "RMS Pedestal G1 > 1.1 ADC counts",
     8   :  "RMS Pedestal G1 > 3.0 ADC counts",
     8   :  "Pedestal G6 <= 1 or RMS G6 <= 0.4  ADC counts",
     16  :  "Pedestal G6 < 170 or > 230 ADC counts",
     32  :  "RMS Pedestal G6 > 1.3 ADC counts",
     64  :  "RMS Pedestal G6 > 4.0 ADC counts",
     64  :  "Pedestal G12 <= 1 or RMS G12 <= 0.5 ADC counts", 
     128 :  "Pedestal G12 < 170 or > 230 ADC counts",
     256 :  "RMS Pedestal G12 > 2.1 ADC counts",
     512 :  "RMS Pedestal G12 > 6.0 ADC counts"
}

class Data:
  channels = {}
  # channel = {
  #   "active" : True|False
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
  
  def setInactive(self, channel):
    try:
      self.channels[channel].active = False
    except:
      for ch in channel:
        self.channels[ch].active = False
    finally:
      return
  
  def isActive(self, channel):
    return [True, False][len(self.channels[channel]["data"].keys()) == 0]

  def isInactive(self, channel):
    return not self.isActive(channel)

  def getActiveChannels(self):
    return [ a for a in self.channels.keys() if self.isActive(a)]

  def getNewChannel(self, active = False, data = {}):
    return {"active" : active, "data" : data}

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
      self.readPedestal(source)
    elif type == "pedestalhvoff":
      self.readPedestalHVOFF(source)
    elif type == "testpulse":
      self.readTestPulse(source)
    elif type == "laserblue":
      self.readLaserBlue(source)
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
      for line in fd.readlines():
        line = line.strip()
        try:
          IOV_ID, channelid, gain1, rms1, gain6, rms6, gain12, rms12, taskstatus = line.split()
        except:
          print "  Cannot parse line\n  '{0}'\n  for 9 fields!"
        if not self.channels.has_key(channelid):
          print "  Hmm. It seems channel {0} is not present in list of all channels. Continue ...".format(channelid)
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
          IOV_ID, channelid, gain1, rms1, APD_OVER_PN_MEAN, APD_OVER_PN_RMS, taskstatus = line.split()
        except:
          print "  Cannot parse line\n  '{0}'\n  for 7 fields!"
        if not self.channels.has_key(channelid):
          print "  Hmm. It seems channel {0} is not present in list of all channels. Continue ...".format(channelid)
          self.channels[channelid] = self.getNewChannel(True)
        self.setChannelData(channelid, {"LaserBlue": [float(gain1), float(rms1)], "APD/DN" : [APD_OVER_PN_MEAN, APD_OVER_PN_RMS]})
        n = n + 1
      print "  Done. Processed {0} records.".format(n)
    return n


  def DBread(source):
    return 0

  def doROOTAnalysis(self, key, dimx = None, RMS = False):
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
    if data["G1"][0] <= 1 or data["G1"][1] <= 0.2:
      flags.append(0)
    if data["G1"][0] < 170 or data["G1"][0] > 230:
      flags.append(2)
    if data["G1"][1] > 1.1:
      flags.append(4)
    if data["G6"][0] <= 1 or data["G6"][1] <= 0.4:
      flags.append(8)
    if data["G6"][0] < 170 or data["G6"][0] > 230:
      flags.append(16)
    if data["G6"][1] > 1.3:
      flags.append(32)
    if data["G6"][1] > 4:
      flags.append(64)
    if data["G12"][0] < 1 or data["G12"][1] <= 0.5:
      flags.append(64)
    if data["G12"][0] < 170 or data["G12"][0] > 230:
      flags.append(128)
    if data["G12"][1] > 2.1:
      flags.append(256)
    if data["G12"][1] > 6:
      flags.append(512)
    return flags

  def getChannel(self, channel):
    return self.channels[channel]

  def classifyChannels(self):
    for c in self.getActiveChannels():
      self.channels[c]["flags"] = self.getChannelFlags(c)

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

