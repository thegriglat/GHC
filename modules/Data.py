#!/usr/bin/env python

import sys

class Data:
  channels = {}
  isClassified = False
  runtype = None
  options = {}
  # channel = {
  #   "data"   : {
  #       "G1"  : [value, rms],
  #       "G6"  : [value, rms],
  #       "G12" : [value, rms] 
  #   }
  # }
  PEDESTAL_FLAGS = ["DPG1", "BPG1", "LRG1", "VLRG1",
          "DPG6", "BPG6", "LRG6", "VLRG6",
          "DPG12", "BPG12", "LRG12", "VLRG12"
  ]
  TESTPULSE_FLAGS = [ "DTPG1", "STPG1", "LTPG1",
                    "DTPG6", "STPG6", "LTPG6",
                    "DTPG12","STPG12","LTPG12"
  ]
  BLUELASER_FLAGS = ["DLAMPL", "SLAMPL", "LLERRO"]

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

  def getSM(self, channel):
   channel = int(channel) - 1011000000
   xtal = channel % 10000
   return (channel - xtal) / 10000

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
    print "Function 'readData' should be overloaded in other classes."
    pass
  
  def getDataKeys(self):
    return self.channels[self.getActiveChannels()[0]]["data"].keys()

  def setOption(self, option, value):
    self.options[option] = value

  def getOption(self, option):
    if self.options.has_key(option):
      return self.options[option]
    else:
      return None

  def DBread(self, source):
    return 0

  def get1DHistogram(self, key, dimx = None, RMS = False, name = ""):
    import ROOT
    if name == "":
      name = "{0} {1}, Gain {2}".format(self.runtype[0].upper() + self.runtype[1:], ("mean", "RMS")[RMS], key)
    activech = self.getActiveChannels()
    if dimx == None:
      dimx = ((150, 250), (0, 5))[RMS]
    hist = ROOT.TH1F(name, name, 100, dimx[0], dimx[1]) 
    hist.SetXTitle("{0} (ADC counts)".format(("Mean", "RMS")[RMS]))
    for ch in activech:
      try:
        hist.Fill(self.channels[ch]["data"][key][RMS])
      except:
        print "  Cannot add value from channel {0} and key {1} {2}!".format(ch, key, ("", "(RMS)")[RMS])
    return hist

  def get2DHistogram(self, key, RMS = False, plottype = "barrel", name = "", lim = None):
    import ROOT
    def getEtaPhi(channel):
      # return (eta, phi)
      ch = int(channel) - 1011000000
      xtal = ch % 10000
      sm = (ch - xtal) / 10000
      if sm < 19:
        return ((xtal - 1) / 20 + 86, 19 - (xtal - 1) % 20  + (sm - 1) * 20 + 1)
      else:
        return (84 - (xtal - 1) / 20 - 85 + 86, (xtal - 1) % 20 + (sm - 19) * 20 + 1)
    def getXY(channel):
      channel = int(channel) - 2010000000
      side = channel / 1000000
      channel = channel - (side * 1000000)
      y = channel % 1000
      x = channel / 1000
      x = [x, x + 100][side == 0]
      return (y, x)
    if name == "":
      name = "{0} {1}, Gain {2}".format(self.runtype[0].upper() + self.runtype[1:], ("mean", "RMS")[RMS], key)
    if plottype == "endcap":
      hist = ROOT.TH2F (name, name, 200, 0, 200, 100, 0, 100) 
      if self.runtype == "pedestal":
        lim = ({True: {"G1" : (0.3, 0.8), "G6" : (0.7, 1.5), "G12" : (1.2, 3.4)}, False : {"G1": (160, 240), "G6" : (160, 240), "G12" : (160, 240)}}, lim)[lim != None]
      elif self.runtype == "testpulse":
        lim = ({True: {"G1" : (0, 12), "G6" : (0, 6), "G12" : (0, 6)}, False : {"G1": (2000, 3500), "G6" : (2000, 3000), "G12" : (2000, 3000)}}, lim)[lim != None]
      hist.SetNdivisions(40, "X")
      hist.SetNdivisions(20, "Y")
      hist.SetXTitle("iX")
      hist.SetYTitle("iY")
      func = getXY
    elif plottype == "barrel":
      hist = ROOT.TH2F (name, name, 360, 0, 360, 170, -85, 85) 
      if self.runtype == "pedestal":
        lim = ({True: {"G1" : (0.3, 0.8), "G6" : (0.4, 1.1), "G12" : (0.8, 2.2)}, False : {"G1": (160, 240), "G6" : (160, 240), "G12" : (160, 240)}}, lim)[lim != None]
      elif self.runtype == "testpulse":
        lim = ({True: {"G1" : (0, 10), "G6" : (0, 4), "G12" : (0, 3)}, False : {"G1": (1400, 3000), "G6" : (1400, 3000), "G12" : (1400, 3000)}}, lim)[lim != None]
      hist.SetNdivisions(18, "X")
      hist.SetNdivisions(2, "Y")
      hist.SetXTitle("i#phi")
      hist.SetYTitle("i#eta")
      func = getEtaPhi
    else:
      print "Unsupported plottype '{0}'".format(plottype)
      sys.exit(0)
    hist.SetMinimum(lim[RMS][key][0])
    hist.SetMaximum(lim[RMS][key][1])
    for c in self.getActiveChannels():
      try:
        hist.SetBinContent(func(c)[1], func(c)[0], self.channels[c]["data"][key][RMS])
      except:
        print "Cannot add bin content to histogram for channel", c
    return hist

  def getChannelFlags(self, channel):
    print "Function getChannelFlags should be overloaded in other modules."
    return []

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

  def saveHistogram(self, histogram, filename, is2D = False, plottype = "barrel"):
    import ROOT
    def drawEBNumbers():
      l = ROOT.TLatex()
      l.SetTextSize(0.03)
      for y in ((42.5, "+"), (-42.5, "-")):
        idx = 1
        for x in xrange(5, 360, 20):
          l.DrawLatex(x, y[0], "{0}{1:2d}".format(y[1], idx))
          idx += 1
    def DrawLine(x, y):
      line = ROOT.TPolyLine()
      for p in xrange(len(x)):
        line.SetNextPoint(x[p], y[p])
        line.SetLineColor(1)
        line.SetLineWidth(2)
      return line
    def getEENumbers():
      l = ROOT.TLatex()
      l.SetTextSize(0.03)
      # Dee 
      l.DrawLatex(5,   95, "Dee1")
      l.DrawLatex(85,  95, "Dee2")
      l.DrawLatex(105, 95, "Dee3")
      l.DrawLatex(185, 95, "Dee4")
      for xo in (0 - 3, 100 - 3):
        sign = ("+", "-")[xo > 50]
        l.DrawLatex(xo + 40, 85, sign + '1')
        l.DrawLatex(xo + 60, 85, sign + '9')
        l.DrawLatex(xo + 20, 65, sign + '2')
        l.DrawLatex(xo + 80, 65, sign + '8')
        l.DrawLatex(xo + 15, 45, sign + '3')
        l.DrawLatex(xo + 85, 45, sign + '7')
        l.DrawLatex(xo + 25, 20, sign + '4')
        l.DrawLatex(xo + 75, 20, sign + '6')
        l.DrawLatex(xo + 50, 10, sign + '5')
    def getEELines():
      xa1 = [50,40,40,35,35,40,40,45,45,50] 
      y1 =  [ 0, 0, 3, 3,15,15,30,30,39,39] 
      xa2 = [35,25,25,20,20,15,15,13,13, 8, 8,10,10,20,20,30,30,35,35,40,40,41,41,42,42,43,43,45,45] 
      y2 =  [ 5, 5, 8, 8,13,13,15,15,20,20,25,25,30,30,35,35,40,40,45,45,43,43,42,42,41,41,40,40,39] 
      xa3 = [ 8, 5, 5, 3, 3, 0, 0,10,10,35,35,39,39] 
      y3 = [25,25,35,35,40,40,60,60,55,55,50,50,45] 
      xa4 = [ 3, 3, 5, 5, 8, 8,13,13,15,15,20,20,25,25,30,30,35,35,40,40,43,43,42,42,41,41,40,40,39,39] 
      y4 = [60,65,65,75,75,80,80,85,85,87,87,85,85,75,75,70,70,65,65,60,60,59,59,58,58,57,57,55,55,50] 
      xa5 = [20,20,25,25,35,35,40, 40, 50,50,45,45,42] 
      y5 = [87,92,92,95,95,97,97,100,100,61,61,60,60] 
      xa6 = [50,60,60,65,65,60,60,55,55,50] 
      xa7 = [65,75,75,80,80,85,85,87,87,92,92,90,90,80,80,70,70,65,65,60,60,59,59,58,58,57,57,55,55]
      xa8 = [92,95,95,97,97,100,100,90,90,65,65,61,61]
      xa9 = [97,97,95,95,92,92,87,87,85,85,80,80,75,75,70,70,65,65,60,60,57,57,58,58,59,59,60,60,61,61] 
      xa10= [80,80,75,75,65,65,60, 60, 50,50,55,55,58] 
      xb1 = [150, 140, 140, 135, 135, 140,140,145, 145,150] 
      xb2 = [135,125,125,120,120,115,115,113,113,108,108,110,110,120,120,130,130,135,135,140,140,141,141,142,142,143,143,145,145] 
      xb3 = [108,105,105,103,103,100,100,110,110,135,135,139,139] 
      xb4 = [103,103,105,105,108,108,113,113,115,115,120,120,125,125,130,130,135,135,140,140,143,143,142,142,141,141,140,140,139,139] 
      xb5 = [120,120,125,125,135,135,140,140,150,150,145,145,142] 
      xb6 = [150,160,160,165,165,160,160,155,155,150] 
      xb7 = [165,175,175,180,180,185,185,187,187,192,192,190,190,180,180,170,170,165,165,160,160,159,159,158,158,157,157,155,155] 
      xb8 = [192,195,195,197,197,200,200,190,190,165,165,161,161] 
      xb9 = [197,197,195,195,192,192,187,187,185,185,180,180,175,175,170,170,165,165,160,160,157,157,158,158,159,159,160,160,161,161] 
      xb10= [180,180,175,175,165,165,160,160,150,150,155,155,158] 
      for x in ( (xa1, y1), (xa2, y2), (xa3, y3), (xa4, y4), (xa5, y5),
                 (xa6, y1), (xa7, y2), (xa8, y3), (xa9, y4), (xa10, y5),
                 (xb1, y1), (xb2, y2), (xb3, y3), (xb4, y4), (xb5, y5),
                 (xb6, y1), (xb7, y2), (xb8, y3), (xb9, y4), (xb10, y5), 
                 ([100, 100], [0, 100])
               ):
        yield x
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    try:
      c = ROOT.TCanvas()
      if is2D:
        histogram.Draw("colz")
        c.SetGridx(True)
        c.SetGridy(True)
        ROOT.gStyle.SetOptStat("e")
        if plottype == "barrel":
          drawEBNumbers()
        elif plottype == "endcap":
          ROOT.gStyle.SetLabelSize(0.017, "X")
          ROOT.gStyle.SetLabelSize(0.017, "Y")
          lines = []
          for p in getEELines():
            lines.append(DrawLine(p[0], p[1]))
          for i in lines:
            i.Draw()
          getEENumbers()
      else:
        c.SetLogy()
        histogram.Draw()
        ROOT.gStyle.SetOptStat("emruo")
      c.Update()
      c.SaveAs(filename)
      return True
    except:
      print "Cannot save '{0}'into {1}".format(repr(histogram),filename)
      return False

