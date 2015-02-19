#!/usr/bin/env python

class data:
  channels = []  
  # channel = {
  #   "name"   : name
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
    for ch in self.channels:
      if sum([len (ch["data"]["pedestal"][a]) for a in ch["data"]["pedestal"].keys()]) == 0:
        ch.active = False
    return
  
  def setInactive(self, channel):
    try:
      self.channel[channel].active = False
    except:
      for ch in channel:
        self.channel[ch].active = False
    finally:
      return
   
  def getInactiveChannels(self):
    return [ a for a in self.channels if a.active ]

  def getNewChannel(self, name, active, data):
    return {"name" : name, "active" : active, "data" : data}

  def readEBPedestalFile(self, filename):
    fd = open(filename, 'r')
    for line in fd.readlines():
      line = strip(line)
      n, channel, gain1, rms1, gain6, rms6, gain12, rms12, unk1, unk2 = line.split()
      self.channel.append(self.getNewChannel(channel, False, {"G1": [gain1, rms1], "G6" : [gain6, rms6], "G12" : [gain12, rms12]})
    return
