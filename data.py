#!/usr/bin/env python

import ROOT

class Data:
  channels = {}
  # channel = {
  #   "active" : True|False
  #   "data"   : {
  #     "pedestal" : {
  #       "G1"  : [value, rms],
  #       "G6"  : [value, rms],
  #       "G12" : [value, rms] 
  #     }
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
    return not self.isInactive(channel)

  def isInactive(self, channel):
    if len(self.channels[channel]["data"].keys()) == 0:
      return True
    else:
      return False

  def getActiveChannels(self):
    return [ a for a in self.channels.keys() if self.channels[a]["active"] ]

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

  def readEBPedestalData(self, filename):
    fd = open(filename, 'r')
    print "Reading Pedestal data ..."
    n = 0
    for line in fd.readlines():
      line = line.strip()
      try:
        idx, channelid, gain1, rms1, gain6, rms6, gain12, rms12, unk1 = line.split()
      except:
        print "  Cannot parse line\n  '{0}'\n  for 9 fields!"
      if not self.channels.has_key(channelid):
        print "  Hmm. It seems channel {0} is not present in list of all channels. Continue ...".format(channelid)
      self.setChannelData(channelid, {"G1": [gain1, rms1], "G6" : [gain6, rms6], "G12" : [gain12, rms12]})
      n = n + 1
    print "  Done. Processed {0} records.".format(n)
    return n
  
  def doROOTAnalysis(self, gain, useRMS = False):
    d = 1 if useRMS else 0
    d1 = "(RMS)" if useRMS else ""
    name = "{0} pedestal {1}".format(gain, d1)
    hist = ROOT.TH1F(name, name, 1000, -4, 4) 
    for ch in self.getActiveChannels():
      hist.Fill(self.channels[ch]["data"][gain][d])
    saveHistImage(hist, "{0}.png".format(name))
    return

def saveHistImage(histogram, filename):
  c = ROOT.TCanvas()
  histogram.Draw()
  c.Update()
  c.SaveAs(filename)
