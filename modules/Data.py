#!/usr/bin/env python

import sys
import ROOT
import log
import sqlite3
import re

class Data(object):
  """
    Basic class for Data obtained from detector
  """
  PEDESTAL_FLAGS = ["DP", "BP", "LR", "VLR" ]
  TESTPULSE_FLAGS = [ "DTP", "STP", "LTP" ]
  LASER_FLAGS = ["DLAMPL", "SLAMPL", "LLERRO"]

  avgLaser = None
  avgTestPulse = {}
  
  def __init__(self, database = ":memory:"):
    """
      At the moment do nothing.
    """
    self.runtype = None
    self.description = None
    self.options = {}
    dbh = sqlite3.connect(database)
    cur = dbh.cursor()
    for l in open("dbschema.sql", 'r').readlines():
      l = l.strip()
      cur.execute (l)
    dbh.commit()
    dbh.create_function("REGEXP", 2, regexp)
    self.dbh = dbh
    self.cur = cur

  def setDesc(self, desc):
    """ 
      Set description for object
    """
    self.description = desc

  def getDesc(self):
    """
      Returns description of object
    """
    return self.description

  def getAllChannels(self):
    return [c[0] for c in self.dbh.execute("select channel_id from all_channels").fetchall()]

  def numOfInactiveChannels(self):
    """
      Returns list of inactive channels
    """
    return len(self.getAllChannels()) - len(self.getActiveChannels(type))
  
  def getActiveChannels(self, **kwargs):
    """
      Returns list of active channels
    """ 
    types = ['pedestal_hvon', 'pedestal_hvoff', 'testpulse', 'laser']
    if kwargs.has_key('type'):
      if kwargs['type'].__class__ != list:
        types = [kwargs['type']]
      else:
        types = kwargs['type']
    if len(types) >= 2:
      sql = " union ".join(["select channel_id from {0}".format(c) for c in ["data_" + i for i in types]])
    else:
      sql = "select distinct channel_id from {0}".format("data_" + types[0])
    return [c[0] for c in self.dbh.execute(sql).fetchall()]

  def readAllChannels(self, filename):
    """
      Reads all channels into self.channels
    """
    fd = open(filename, 'r')
    log.info( "Getting list of all channels ...")
    n = 0
    cur = self.dbh.cursor()
    for line in fd.readlines():
      line = line.strip()
      ch = int(line)
      cur.execute("insert into all_channels values ({channel}, '{location}', {sm}, {tt}, {xtal})".format(channel = ch, 
      location = getChannelClass(ch), sm = getSM(ch), tt = getTT(ch), xtal = getXtal(ch)))
      n = n + 1
    self.dbh.commit()
    log.info( "Done. Processed {0} records.".format(n))
    return n

  def getDataKeys(self):
    """
      Returns available data keys for the class.
      At the moment it chechs only first available channel
    """
    sql = " union ".join(["select key from {0}".format(c) for c  in ['data_pedestal_hvon', 'data_testpulse', 'data_laser', 'data_pedestal_hvoff']])
    try:
      return [ c[0] for c in self.dbh.execute(sql).fetchall()]
    except:
      return []

  def setOption(self, option, value):
    """
      Set self.options[option] to value
    """
    self.options[option] = value

  def getOption(self, option):
    """
      Returns self.options[option]
    """
    if self.options.has_key(option):
      return self.options[option]
    else:
      return None

  def DBread(self, source):
    """
      At the moment do nothing
    """
    return 0

  def get1DHistogram(self, **kwargs):
    """
      Return TH1F histogram.
      Parameters:
        key     : key of data to be used
        dimx    : range of X axis. Default is ((150, 250), (0, 5))[RMS]
        useRMS  : use mean (False) or RMS (True) data. Default is False
        name    : title of histogram. Default is "{0} {1}, Gain {2}".format(self.description, ("mean", "RMS")[RMS], key)
        type    : run type to use
        part    : "EB" | "EE"
    """
    if not kwargs.has_key('name'):
      if "pedestal" in kwargs['type'] or "testpulse" in kwargs["type"]:
        name = "{0} {1}, {2} (ADC counts)".format(kwargs['type'], ("mean", "RMS")[kwargs['useRMS']], kwargs['key'])
      elif kwargs['type'] == "laser":
        name = "Laser {0}".format(("Amplitude " + (" ", "RMS")[kwargs['useRMS']] + "(ADC counts)", key + ' ' + ("ratio", "RMS")[kwargs['useRMS']])[key == "APD/PN"])
    else:
      name = kwargs['name']
    activech = [ c[0] for c in self.cur.execute("select channel_id from {tab} where key = '{key}'".format(tab = 'data_' + kwargs['type'], key = kwargs['key'])).fetchall() if getChannelClass(c[0]) == kwargs['part']]
    if not kwargs.has_key('dimx'):
      if kwargs['type'] == "testpulse":
        if kwargs['part'] == "EB":
          dimx = ((1000,3000),(0,20))[kwargs['useRMS']]
        else:
          dimx = ((1000,4000),(0,20))[kwargs['useRMS']]
      elif kwargs['type'] == "laser":
        if "OVER" in kwargs['key']:
          dimx = ((0,5),(0, 0.1))[kwargs['useRMS']]
        else:
          dimx = ((0,6000),(0,5))[kwargs['useRMS']]
      else:
        dimx = ((150, 250), (0, 5))[kwargs['useRMS']]
    else:
      dimx = kwargs['dimx']
    hist = ROOT.TH1F(name, name, 100, dimx[0], dimx[1]) 
    hist.SetXTitle("{0} (ADC counts)".format(("Mean", "RMS")[kwargs['useRMS']]))
    for ch in activech:
      try:
        hist.Fill(float(self.getChannelData(ch, kwargs['key'], kwargs['type'])))
      except Exception as e:
        log.error( "  Cannot add value from channel {0} and key {1} {2}!: {3}".format(ch, key, ("", "(RMS)")[kwargs['useRMS']], e))
    return hist

  def get2DHistogram(self, **kwargs):
    """
      Returns TH2F histogram.
      Parameters:
        key      : data[key] which will be used
        RMS      : use mean (False) or RMS (True) data. Default is False
        plottype : "barrel"|"endcap"
        name     : title of histogram. Default is "{0} {1}, Gain {2}".format(self.description, ("mean", "RMS")[RMS], key)
        lim      : hash table which determines X,Y axis range 
    """
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
    RMS = (False, kwargs['useRMS'])[kwargs.has_key('useRMS')]
    lim = None
    gain = kwargs['key'].split("_")[-1:][0]
    if not "G" in gain:
      # laser 
      if kwargs['key'].split("_")[1] == "OVER":
        gain = 'APD/PN'
      else:
        gain = 'Laser'
    if not kwargs.has_key('name'):
      if "pedestal" in kwargs['type'] or kwargs['type'] == "testpulse":
        name = "{0} {1}, Gain {2} (ADC counts)".format(kwargs['type'], ("mean", "RMS")[RMS], kwargs['key'])
      elif kwargs['type'] == "laser":
        name = "Laser {0}".format(("Amplitude " + (" ", "RMS")[RMS] + "(ADC counts)", kwargs['key'] + ' ' + ("ratio", "RMS")[RMS])[kwargs['key'] == "APD/PN"])
    else:
      name = kwargs['name']
    if kwargs['part'] == "EE":
      hist = ROOT.TH2F (name, name, 200, 0, 200, 100, 0, 100) 
      if "pedestal" in kwargs['type']:
        lim = ({True: {"G1" : (0.3, 0.8), "G6" : (0.7, 1.5), "G12" : (1.2, 3.4)}, False : {"G1": (160, 240), "G6" : (160, 240), "G12" : (160, 240)}}, lim)[lim != None]
      elif kwargs['type'] == "testpulse":
        lim = ({True: {"G1" : (0, 12), "G6" : (0, 6), "G12" : (0, 6)}, False : {"G1": (2000, 3500), "G6" : (2000, 3000), "G12" : (2000, 3000)}}, lim)[lim != None]
      elif kwargs['type'] == "laser":
        lim = ({True: {"Laser" : (0, 60), 'APD/PN' : (0, 0.05)}, False: {"Laser" : (0, 2000), 'APD/PN' : (0, 2.5)}}, lim)[lim != None]
      hist.SetNdivisions(40, "X")
      hist.SetNdivisions(20, "Y")
      hist.SetXTitle("iX (iX + 100)")
      hist.SetYTitle("iY")
      func = getXY
    elif kwargs['part'] == "EB":
      hist = ROOT.TH2F (name, name, 360, 0, 360, 170, -85, 85) 
      if "pedestal" in kwargs['type']:
        lim = ({True: {"G1" : (0.3, 0.8), "G6" : (0.4, 1.1), "G12" : (0.8, 2.2)}, False : {"G1": (160, 240), "G6" : (160, 240), "G12" : (160, 240)}}, lim)[lim != None]
      elif kwargs['type'] == "testpulse":
        lim = ({True: {"G1" : (0, 10), "G6" : (0, 4), "G12" : (0, 3)}, False : {"G1": (1400, 3000), "G6" : (1400, 3000), "G12" : (1400, 3000)}}, lim)[lim != None]
      elif kwargs['type'] == "laser":
        lim = ({True: {"Laser" : (0, 50), 'APD/PN' : (0, 0.06)}, False: {"Laser" : (0, 2000), 'APD/PN' : (0, 3)}}, lim)[lim != None]
      hist.SetNdivisions(18, "X")
      hist.SetNdivisions(2, "Y")
      hist.SetXTitle("i#phi")
      hist.SetYTitle("i#eta")
      func = getEtaPhi
    else:
      log.error( "Unsupported plottype '{0}'".format(plottype))
      sys.exit(0)
    hist.SetMinimum(lim[RMS][gain][0])
    hist.SetMaximum(lim[RMS][gain][1])
    for c in [ c[0] for c in self.cur.execute("select distinct channel_id from {tab} where key = '{key}'".format(tab = "data_" + kwargs['type'], key = kwargs['key'])) if getChannelClass(c[0]) == kwargs['part']]:
      try:
        hist.SetBinContent(func(c)[1], func(c)[0], float(self.getChannelData(c, kwargs['key'], kwargs['type'])))
      except:
        log.error( "Cannot add bin content to histogram for channel", c)
    return hist

  def getChannelData(self, channel, key, type):
    try:
      return  self.cur.execute("select value from {table} where channel_id = {channel} and key = '{key}'".format(table = "data_" + type, channel = channel, key = key)).fetchone()[0]
    except:
      return None

  def getChannelFlags(self, channel, type):
    """
      Compare channel data with limits and return list of error flags
      Function getChannelFlags should be overloaded in other modules.
    """
    if type == "pedestal_hvon":
      return self.getPedestalFlags(channel)
    elif type == 'testpulse':
      return self.getTestPulseFlags(channel)
    elif type == 'laser':
      return self.getLaserFlags(channel)
    return None

  def getPedestalFlags(self, channel):
    def PedestalComparison(key, deadlimits, badlimits):
      tmpflags = []
      mean = self.getChannelData(channel, 'PED_MEAN_' + key, 'pedestal_hvon')
      rms = self.getChannelData(channel, 'PED_RMS_' + key, 'pedestal_hvon')
      if mean <= deadlimits[0] or rms <= deadlimits[1]:
        tmpflags.append("DP" + key)
      else:
        if rms >= badlimits[0] and rms < badlimits[1] and mean > deadlimits[0]:
          tmpflags.append("LR" + key)
        if rms > badlimits[1] and mean > deadlimits[0]:
          tmpflags.append("VLR" + key)
        if abs(mean - 200) >= 30 and mean > deadlimits[0]:
          tmpflags.append("BP" + key)
      return tmpflags
    flags = []
    if self.cur.execute("select location from all_channels where channel_id = " + str(channel)).fetchone()[0] == "EB":
      limits = {"G1" : ((1, 0.2), (1.1, 3)), "G6" : ((1, 0.4), (1.3, 4)), "G12" : ((1, 0.5), (2.1, 6))}
    else:
      limits = {"G1" : ((1, 0.2), (1.5, 4)), "G6" : ((1, 0.4), (2, 5)),   "G12" : ((1, 0.5), (3.2, 7))}
    flags += PedestalComparison("G1", limits["G1"][0], limits["G1"][1])
    flags += PedestalComparison("G6", limits["G6"][0], limits["G6"][1])
    flags += PedestalComparison("G12", limits["G12"][0], limits["G12"][1])
    return list(set(flags))

  def getTestPulseFlags(self, channel):
    def getavgtestpulse(key):
      if self.avgTestPulse.has_key(key):
        return self.avgTestPulse[key]
      else:
        self.avgTestPulse[key] = self.dbh.execute("select sum(value) from data_testpulse where key = '{key}'".format(key = 'ADC_MEAN_' + key)).fetchone()[0] / float( self.dbh.execute("select count(channel_id) from data_testpulse").fetchone()[0])
        return self.avgTestPulse[key]
    flags = []
    for i in ('G1', 'G6', 'G12'):
      mean = self.getChannelData(channel, 'ADC_MEAN_' + i, 'testpulse')
      mean = self.getChannelData(channel, 'ADC_RMS_' + i, 'testpulse')
      if mean <= 0:
        flags.append("DTP" + i)
      if mean / getavgtestpulse(i) <= 0.5:
        flags.append("STP" + i)
      if mean / getavgtestpulse(i) > 1.5:
        flags.append("LTP" + i)
    return list(set(flags))

  def getLaserFlags(self, channel):
    def getavglaser():
      if not self.avgLaser is None:
        return self.avgLaser
      else:
        self.avgLaser = self.dbh.execute("select sum(value) from data_laser where key = 'APD_MEAN'").fetchone()[0] / float( self.dbh.execute("select count(channel_id) from data_laser").fetchone()[0])
        return self.avgLaser
    flags = []
    mean = self.getChannelData(channel, 'APD_MEAN', 'laser')
    rms = self.getChannelData(channel, 'APD_RMS', 'laser')
    if mean <= 0:
      flags.append("DLAMPL")
    if mean / getavglaser() < 0.1 and mean > 0:
      flags.append("SLAMPL")
    location =  self.cur.execute("select location from all_channels where channel_id = {channel}".format(channel = channel)).fetchone()[0]
    if location == "EB":
      LLERRO_b = 0.2
    elif location == "EE":
      LLERRO_b = 0.05
    else:
      log.error("Cannot define location on channel" + str(channel))
    if mean > 0 and rms / float(mean) > LLERRO_b:
      flags.append("LLERRO")
    return list(set(flags))


  def classifyChannels(self):
    """
      Call getChannelFlags for each active channel and set 'flags' value for channels
    """
    cur = self.dbh.cursor()
    for t in ['pedestal_hvon','testpulse', 'laser']:
      log.info("Classifying {0} channels ...".format(t))
      for c in [ k[0] for k in self.dbh.execute("select channel_id from {table}".format(table = "data_" + t)).fetchall()]:
        for f in self.getChannelFlags(c, t):
          cur.execute("insert or ignore into flags values ({0}, '{1}')".format(int(c), f))
    # pedestal HV OFF channels problems
    log.info("Classifying pedestal HV OFF channels ...")
    for key in ["G1", "G6", "G12"]:
      sql = "select data_pedestal_hvon.channel_id  from data_pedestal_hvon, data_pedestal_hvoff \
             where data_pedestal_hvon.channel_id = data_pedestal_hvoff.channel_id and \
             data_pedestal_hvon.key = data_pedestal_hvoff.key and \
             abs(data_pedestal_hvon.value - data_pedestal_hvoff.value) < 0.2 \
             and data_pedestal_hvon.key = '{0}'".format( 'PED_RMS_' + key)
      badchannels = [ c[0] for c in self.cur.execute(sql).fetchall() ]
      for c in list(set(badchannels)):
        cur.execute("insert or ignore into flags values ({0}, '{1}')".format(int(c), 'BV' + key))
    self.dbh.execute("insert into options values ('isClassified', 1)")
    self.dbh.commit()

  def getChannelsByFlag(self, flags):
    """
      Returns list of channels which has <flags> (string|list)
    """
    if self.dbh.execute("select count(*) from options where name = 'isClassified'").fetchone()[0] == 0:
      self.classifyChannels()
    if flags.__class__ == list:
      str = "flag = " + " or flag = ".join([ "\"{0}\"".format(c) for c in flags])
    else:
      str = "flag = \"{0}\"".format(flags)
    return [c[0] for c in self.cur.execute("select distinct channel_id from flags where {0}".format(str)).fetchall()]

  def Export(self, filename):
    dbout = sqlite3.connect(filename)
    DumpDB(self.dbh, dbout)
    dbout.close()

  def Load(self, filename):
    self.dbh = sqlite3.connect(":memory:")
    dbin = sqlite3.connect(filename)
    DumpDB(dbin, self.dbh)
  
  def readData(self, source, **kwargs):
    """
      Read pedestal values from database
        connstr : connection string to database
        runnum  : array of runs which contains data
    """
    if not kwargs.has_key("runs"):
      log.error("readData function should be called with 'runs' parameter")
    if not kwargs.has_key("type"):
      log.error("readData function should be called with 'type' parameter")
    if kwargs.has_key('lasertable'):
      log.info("Table {0} will be user as source for Laser data".format(kwargs['lasertable']))
    table = "data_" + kwargs['type']
    log.info("Trying to connect to Oracle")
    import cx_Oracle
    ora = cx_Oracle.connect(source.split('oracle://')[1])
    log.info("OK")
    log.info("Exporting data from Oracle to inner DB ...")

    for run in kwargs['runs']:
      log.info("Process run " + str(run) + " ...")
      if "pedestal" in table:
        sql = "select LOGIC_ID, PED_MEAN_G1, PED_RMS_G1, PED_MEAN_G6, PED_RMS_G6, PED_MEAN_G12, PED_RMS_G12 \
          from MON_PEDESTALS_DAT where IOV_ID=(select IOV_ID from MON_RUN_IOV where RUN_IOV_ID=(select IOV_ID from RUN_IOV where RUN_NUM={0}))".format(run)
        fields = ['PED_MEAN_G1', 'PED_RMS_G1', 'PED_MEAN_G6', 'PED_RMS_G6', 'PED_MEAN_G12', 'PED_RMS_G12']
      elif "testpulse" in table:
        sql = "select LOGIC_ID, ADC_MEAN_G1, ADC_RMS_G1, ADC_MEAN_G6, ADC_RMS_G6, ADC_MEAN_G12, ADC_RMS_G12 \
          from MON_TEST_PULSE_DAT where IOV_ID=(select IOV_ID from MON_RUN_IOV where RUN_IOV_ID=(select IOV_ID from RUN_IOV where RUN_NUM={0}))".format(run)
        fields = ['ADC_MEAN_G1', 'ADC_RMS_G1', 'ADC_MEAN_G6', 'ADC_RMS_G6', 'ADC_MEAN_G12', 'ADC_RMS_G12']
      elif "laser" in table:
        sql = "select LOGIC_ID, APD_MEAN, APD_RMS, APD_OVER_PN_MEAN, APD_OVER_PN_RMS \
          from {0} where IOV_ID=(select IOV_ID from MON_RUN_IOV where RUN_IOV_ID=(select IOV_ID from RUN_IOV where RUN_NUM={1}))".format(kwargs['lasertable'], run)
        fields = ['APD_MEAN', 'APD_RMS', 'APD_OVER_PN_MEAN', 'APD_OVER_PN_RMS']
      cur = self.dbh.cursor()
      result = ora.cursor().execute(sql)
      cur.execute("insert into runs values ({0}, '{1}', \"\")".format(int(run), kwargs['type']))
      for row in result:
        for k in xrange(len(fields)):
          # we will insert only matter data
          # merging ...
          c =  cur.execute("select value from {table} where channel_id = {channel} and key = '{key}'".format(table = table, key = fields[k], channel = int(row[0]))).fetchall()
          if len(c) == 0:
            cur.execute("insert into {table} values ({channel}, '{key}', {data}) ".format(table = table, channel = int(row[0]), data = row[k + 1], key = fields[k]))
          elif c[0][0] == -1 and row [k + 1] != -1:
            log.debug ("Replace {key} values for channel {channel}: {old} -> {new}".format(key = fields[k], channel = row[0], old = c[0][0], new = row[k + 1]))
            cur.execute("update {table} set value = {data} where channel_id = {channel} and key = '{key}' ".format(table = table, channel = int(row[0]), data = row[k + 1], key = fields[k]))
      self.dbh.commit()
    ora.close()

def DumpSQL(db, filename):
  f = open(filename, 'w')
  log.info("Dumping database to '{0}' in SQL format.".format(filename))
  for line in db.iterdump():
    f.write('%s\n' % line)
  log.info("Finished.")

def DumpDB(dbin, dbout):
  dbin.text_factory = sqlite3.OptimizedUnicode
  dbout.text_factory = sqlite3.OptimizedUnicode
  cout = dbout.cursor()
  for tablerow in dbin.execute('select * from sqlite_master').fetchall():
    tablename = tablerow[2]
    log.info ("Create table '" + tablename + "'")
    if "sqlite" in tablerow[1]:
      continue
    try:
      cout.execute(tablerow[4])
    except Exception as e:
      log.error("Cannot create table {0} in DB {1}!: {2}".format(tablename, str(dbout), str(e)))
    log.info ("Exporting data from table '" + tablename + "' ...")
    for row in dbin.execute('select * from ' + tablename).fetchall():
      cout.execute ('insert into ' + tablename + ' values ' + str(row))
    dbout.commit()
    log.info (tablename + " : Done.")

def saveHistogram(histogram, filename, plottype):
  """
    Save <histogram> into filename according to <plottype>
  """
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
    l.SetTextSize(0.04)
    # Dee 
    l.DrawLatex(5,   95, "Dee1")
    l.DrawLatex(85,  95, "Dee2")
    l.DrawLatex(105, 95, "Dee4")
    l.DrawLatex(185, 95, "Dee3")
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
    ROOT.gStyle.SetLabelSize(0.017, "X")
    ROOT.gStyle.SetLabelSize(0.017, "Y")
    if type(histogram) is ROOT.TH2F:
      histogram.Draw("colz")
      c.SetGridx(True)
      c.SetGridy(True)
      ROOT.gStyle.SetOptStat("e")
      ROOT.gStyle.SetTickLength(0.01, "xy")
      if plottype == "EB":
        drawEBNumbers()
      elif plottype == "EE":
        c.SetCanvasSize(1000, 500)
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
  ROOT.gStyle.Clear()

def getTT(channel):
  """
    Returns TT number for channel
  """
  channel = str(channel)
  l1 = getXtal(channel)
  l2 = getEB(channel)
  row = (l1 - 1) / 20 + 1
  col = (l1 - 1) % 20 + 1
  TTrow = (row - 1) / 5
  TTcol = (col - 1) / 5
  TT = TTrow * 4 + TTcol + 1
  return TT

def getXtal(channel):
  """
    Returns crystal number for channel
  """
  return int(str(channel)[-4:])

def getEB(channel):
  """
    Returns EB number for channel
  """
  return int(str(channel)[-6:-4])

def getSM(channel):
  """
    Returns supermodule (SM) number for channel
  """
  channel = int(channel) - 1011000000
  xtal = channel % 10000
  return (channel - xtal) / 10000

def getChannelClass(channel):
  """
    Returns EB|EE depending on detector place of channel
  """
  if str(channel)[0] == "1":
    return "EB"
  else:
    return "EE"

def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None
