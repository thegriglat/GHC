#!/usr/bin/env python

import ROOT

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

  def readPedestal(self, source = None):
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
      hist.Fill(self.channels[ch]["data"][key][RMS])
    return hist

def saveHistogram(histogram, filename):
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
