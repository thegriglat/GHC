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
  PEDESTAL_FLAGS = ["DP", "BP", "LR", "VLR", "BV"]
  TESTPULSE_FLAGS = [ "DTP", "STP", "LTP" ]
  LASER_FLAGS = ["DLAMPL", "SLAMPL", "LLERRO"]

  def __init__(self, database = ":memory:"):
    """
      Initalize (in-memory) sqlite3 database.
    """
    dbh = sqlite3.connect(database)
    cur = dbh.cursor()
    for l in open("dbschema.sql", 'r').readlines():
      l = l.strip()
      cur.execute (l)
    dbh.commit()
    dbh.create_function("REGEXP", 2, regexp)
    self.dbh = dbh
    self.cur = cur

  def getAllChannels(self):
    """
      Return list of all channels
    """
    return [c[0] for c in self.dbh.execute("select channel_id from all_channels")]

  def numOfInactiveChannels(self):
    """
      Returns number of inactive channels
    """
    return len(self.getAllChannels()) - len(self.getActiveChannels())
 
  def getProblematicChannels(self):
    self.classifyChannels()
    return [c[0] for c in self.dbh.execute("select distinct channel_id from flags")]
 
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
    return [c[0] for c in self.dbh.execute(sql)]

  def readAllChannels(self, filename):
    """
      Reads all channels
    """
    fd = open(filename, 'r')
    log.info( "Getting list of all channels ...")
    n = 0
    cur = self.dbh.cursor()
    for line in fd.readlines():
      line = line.strip()
      ch = int(line)
      cur.execute("insert into all_channels values ({channel}, '{location}')".format(channel = ch, location = getSubDetector(ch)))
      n = n + 1
    self.dbh.commit()
    log.info( "Done. Processed {0} records.".format(n))
    return n

  def getDataKeys(self):
    """
      Returns available data keys.
    """
    sql = " union ".join(["select key from {0}".format(c) for c  in ['data_pedestal_hvon', 'data_testpulse', 'data_laser', 'data_pedestal_hvoff']])
    try:
      return [ c[0] for c in self.dbh.execute(sql)]
    except:
      return []

  def setOption(self, option, value):
    """
      Set option's value
    """
    self.dbh.execute("insert or replace into options values ('{0}', {1})".format(option, value))
    self.dbh.commit()

  def getOption(self, option):
    """
      Returns option's value
    """
    r = self.dbh.execute("select value from options where name = '{0}'".format(option)).fetchone()
    if r is None:
      return None
    else:
      return r[0]

  def resetFlags(self):
    """
      Reset flags in DB
    """
    self.dbh.execute("delete from flags")
    self.setOption('isClassified', 0)
    self.dbh.commit()

  def get1DHistogram(self, **kwargs):
    """
      Return TH1F histogram.
      Parameters:
        key     : key of data to be used
        dimx    : range of X axis. Default is ((150, 250), (0, 5))[RMS]
        useRMS  : use mean (False) or RMS (True) data.
        name    : title of histogram.
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
    activech = [ c[0] for c in self.cur.execute("select channel_id from {tab} where key = '{key}'".format(tab = 'data_' + kwargs['type'], key = kwargs['key'])) if getSubDetector(c[0]) == kwargs['part']]
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
        hist.Fill(float(self.getChannelData(ch, key = kwargs['key'], type = kwargs['type'])))
      except Exception as e:
        log.error( "  Cannot add value from channel {0} and key {1} {2}!: {3}".format(ch, kwargs['key'], ("", "(RMS)")[kwargs['useRMS']], e))
    return hist

  def get2DHistogram(self, **kwargs):
    """
      Returns TH2F histogram.
      Parameters:
        key      : data[key] which will be used
        useRMS   : use mean (False) or RMS (True) data.
        type     : run type
        part     : "EB"|"EE"
        name     : title of histogram.
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
    for c in [ c[0] for c in self.cur.execute("select distinct channel_id from {tab} where key = '{key}'".format(tab = "data_" + kwargs['type'], key = kwargs['key'])) if getSubDetector(c[0]) == kwargs['part']]:
      try:
        hist.SetBinContent(func(c)[1], func(c)[0], float(self.getChannelData(c, key = kwargs['key'], type = kwargs['type'])))
      except:
        log.error( "Cannot add bin content to histogram for channel", c)
    return hist

  def getChannelData(self, channel, **kwargs):
    """
      Returns channel's value for channels
      If additional keys ('key' and 'type') are specified -- return value
      else return dict with all values for channel
    """
    if kwargs.has_key('key') and kwargs.has_key("type"): 
      try:
        return  self.cur.execute("select value from {table} where channel_id = {channel} and key = '{key}'".format(table = "data_" + kwargs['type'], channel = channel, key = kwargs['key'])).fetchone()[0]
      except:
        return None
    # in other cases return dictionary with data
    if kwargs.has_key("type"):
      type = [kwargs["type"]]
    else:
      type = ["pedestal_hvon", "pedestal_hvoff", "testpulse", "laser"]
    if kwargs.has_key("key"):
      key = kwargs["key"]
    else:
      key = None
    result = {}
    for t in type:
      if key != None:
        result.update({key : self.getChannelData(channel, key = key, type = t)})
      else:
        keys = [i[0] for i in self.dbh.execute("select distinct key from {0}".format("data_" + t))]
        for k in keys:
          if "hvon" in t:
            kmod = k + "_HVON"
          elif "hvoff" in t:
            kmod = k + "_HVOFF"
          else:
            kmod = k
          result.update({kmod : self.getChannelData(channel, key = k, type = t)})
    return result

  def getPedestalFlags(self, channel):
    """
      Returns flags for pedestal channels
    """
    def PedestalComparison(key, deadlimits, badlimits):
      tmpflags = []
      mean = self.getChannelData(channel, key = 'PED_MEAN_' + key, type = 'pedestal_hvon')
      rms = self.getChannelData(channel, key = 'PED_RMS_' + key, type = 'pedestal_hvon')
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

  def classifyChannels(self):
    """
      Call getPedestalFlags for pedestals or execute sql quiery for compare test pulse,
      laser or pedestal HV OFF channels
    """
    if self.getOption('isClassified') == 1:
      return
    self.dbh.commit()
    def testpulse():
      for key in ("G1", "G6", "G12"):
        sql = "insert or ignore into flags select channel_id, '{0}' from data_testpulse where key = '{1}' and value = 0".format('DTP' + key, 'ADC_MEAN_' + key)
        self.dbh.execute(sql)
        for l in (1, 2):
          avg = self.dbh.execute("select avg(value) from data_testpulse where key = 'ADC_MEAN_{0}' and channel_id like '{1}%'".format(key, l)).fetchone()[0] 
          sql = "insert or ignore into flags select channel_id, '{0}' from data_testpulse where key = '{1}' and value > 0 and value <= 0.5 * {2} and channel_id like '{3}%'".format('STP' + key, 'ADC_MEAN_' + key, avg, l)
          self.dbh.execute(sql)
          sql = "insert or ignore into flags select channel_id, '{0}' from data_testpulse where key = '{1}' and value > 1.5 * {2} and channel_id like '{3}%'".format('LTP' + key, 'ADC_MEAN_' + key, avg, l)
          self.dbh.execute(sql)
    def ped_hvoff():
      # pedestal HV OFF channels problems
      for key in ["G1", "G6", "G12"]:
        sql = "insert or ignore into flags select data_pedestal_hvon.channel_id, '{0}' from data_pedestal_hvon, data_pedestal_hvoff \
               where data_pedestal_hvon.channel_id = data_pedestal_hvoff.channel_id and \
               data_pedestal_hvon.key = data_pedestal_hvoff.key and \
               abs(data_pedestal_hvon.value - data_pedestal_hvoff.value) < 0.2 \
               and data_pedestal_hvon.key = '{1}'".format('BV' + key, 'PED_RMS_' + key)
        self.dbh.execute(sql)
    def laser():
      sql = "insert or ignore into flags select channel_id, 'DLAMPL' from data_laser where key = 'APD_MEAN' and value <= 0"
      self.dbh.execute(sql)
      for l in (1, 2):
        avg = self.dbh.execute("select avg(value) from data_laser where key = 'APD_MEAN' and channel_id like '{0}%'".format(l)).fetchone()[0] 
        sql = "insert or ignore into flags select channel_id, 'SLAMPL' from data_laser where key = 'APD_MEAN' and value < {0} * 0.1 and value > 0 and channel_id like '{1}%'".format(avg, l)
        self.dbh.execute(sql)
        sql = "insert or ignore into flags select dl1.channel_id, 'LLERRO' from data_laser as dl1 \
                                          inner join data_laser as dl2 \
                                        inner join all_channels as ac \
             on \
             dl1.channel_id = dl2.channel_id and \
             dl1.channel_id = ac.channel_id \
             where \
             dl1.key = 'APD_MEAN' and dl2.key = 'APD_RMS' and dl1.value > 0 and dl2.value / dl1.value > \
             case ac.location \
              when 'EB' then 0.2  \
              when 'EE' then 0.05 \
             end"
        self.dbh.execute(sql)
    cur = self.dbh.cursor()
    log.info ("Classify Pedestal HV ON data ...")
    try:
      for c in [ k[0] for k in self.dbh.execute("select channel_id from data_pedestal_hvon")]:
        for f in self.getPedestalFlags(c):
          cur.execute("insert or ignore into flags values ({0}, '{1}')".format(int(c), f))
      self.dbh.commit()
      log.info ("Finished.")
    except:
      log.info("Skipped.")
      self.dbh.rollback()
    log.info ("Classify Test Pulse data ...")
    try:
      testpulse()
      self.dbh.commit()
      log.info ("Finished.")
    except:
      log.info("Skipped.")
      self.dbh.rollback()
    log.info ("Classify Laser data ...")
    try:
      laser()
      self.dbh.commit()
      log.info ("Finished.")
    except:
      log.info("Skipped.")
      self.dbh.rollback()
    log.info ("Classify Pedestal HV OFF data ...")
    try:
      ped_hvoff()
      self.dbh.commit()
      log.info ("Finished.")
    except:
      log.info("Skipped.")
      self.dbh.rollback()
    self.setOption('isClassified', 1)
    self.dbh.commit()

  def getFlagsByChannel(self, channel):
    self.classifyChannels()
    return [c[0] for c in self.dbh.execute("select flag from flags where channel_id = {0}".format(channel))]

  def getChannelsByFlag(self, flags, exp = "and"):
    """
      Returns list of channels which has <flags> (string|list)
      exp = 'or' | 'and'
    """
    self.classifyChannels()
    if flags.__class__ == list:
      str = "flag = " + (" {0} flag = ".format(exp)).join([ "\"{0}\"".format(c) for c in flags])
    else:
      str = "flag = \"{0}\"".format(flags)
    return [c[0] for c in self.cur.execute("select distinct channel_id from flags where {0}".format(str))]

  def Export(self, filename):
    """
      Exports internal database to file 'filename' as sqlite3 DB
    """
    dbout = sqlite3.connect(filename)
    DumpDB(self.dbh, dbout)
    dbout.close()

  def Load(self, filename):
    """
      Load database from sqlite DB located in 'filename'
    """
    self.dbh = sqlite3.connect(":memory:")
    dbin = sqlite3.connect(filename)
    DumpDB(dbin, self.dbh)
    self.dbh.create_function("REGEXP", 2, regexp)
    self.cur = self.dbh.cursor()
  
  def readData(self, source, **kwargs):
    """
      Read pedestal values from database
        source    : connection string to database
        runs       : array of runs which contains data
        type       : run type
        lasertable : table of laser's data
    """
    if not kwargs.has_key("runs"):
      log.error("readData function should be called with 'runs' parameter")
    if not kwargs.has_key("type"):
      log.error("readData function should be called with 'type' parameter")
    if "oracle" not in source:
      self.readDataFromFile(source, kwargs)
      return
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

  def readDataFromFile(self, source, kwargs):
    """
      Read data from file called 'source'
    """
    type = kwargs['type']
    files = kwargs['runs']
    if "pedestal" in type:
      fields = ['PED_MEAN_G1', 'PED_RMS_G1', 'PED_MEAN_G6', 'PED_RMS_G6', 'PED_MEAN_G12', 'PED_RMS_G12']
    elif "testpulse" in type:
      fields = ['ADC_MEAN_G1', 'ADC_MEAN_G6', 'ADC_MEAN_G12', 'ADC_RMS_G1', 'ADC_RMS_G6', 'ADC_RMS_G12']
    elif "laser" in type:
      fields = ['APD_MEAN', 'APD_RMS', 'APD_OVER_PN_MEAN', 'APD_OVER_PN_RMS']
    else:
      log.error("Unsuported type of data: {0}".format(type))
    table = "data_" + type
    for f in files:
      log.info("Reading file '{0}'".format(f))
      fh = open(f, 'r')
      cur = self.dbh.cursor()
      for line in fh.readlines():
        line = line.strip().split()
        channel = line[1]
        for k in xrange(len(fields)):
          cur.execute("insert or replace into {table} values ({channel}, '{key}', {value})".format(table = table, channel = channel, key = fields[k], value = line[k + 2]))
      fh.close()
    self.dbh.commit()

  def printProblematicChannels(self):
    """
      Print problematic channel's data
    """
    print " {0:10s} | {1:40s} | {2:23s}".format("channel", "flags", "info")
    print "-"*80
    for c in self.dbh.execute("select distinct channel_id from flags"):
      c = c[0]
      flags = [i[0] for i in self.dbh.execute("select flag from flags where channel_id = {0}".format(c))]
      info = getChannelInfo(c)
      print " {0:10d} | {1:40s} | {2:23s}".format(c, "+".join(flags), " ".join(["{0}={1}".format(i, info[i])for i in info.keys() if i != "id"]))
    print "-"*80

def DumpSQL(db, filename):
  """
    Dumps database as sql
  """
  f = open(filename, 'w')
  log.info("Dumping database to '{0}' in SQL format.".format(filename))
  for line in db.iterdump():
    f.write('%s\n' % line)
  log.info("Finished.")


def DumpDB(dbin, dbout):
  """
    Copy dbin to dbout (both are sqlite3 connection pointers)
  """
  dbin.text_factory = sqlite3.OptimizedUnicode
  dbout.text_factory = sqlite3.OptimizedUnicode
  cout = dbout.cursor()
  log.info("Starting dump ...")
  for sqlline in dbin.iterdump():
    if sqlline != "COMMIT;": 
      cout.execute(sqlline)
  dbout.commit()
  log.info("Finished.")

def saveHistogram(histogram, filename, plottype):
  """
    Save <histogram> into filename according to <plottype>
    plottype = 'EE' | 'EB'
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

def getChannelInfo(c):
  """
    Return dict with information about location of channels in ECAL
    keys for EB: id, location, SM, TT, iEta, iPhi
    keys for EE: id, location, SM, Dee, iX, iY, iZ
  """
  def getEBInfo(c):
    info = {'id' : c}
    sm = getSM(c)
    info.update({'location' : getSubDetector(c) + "{0:+03d}".format(sm)})
    info.update({"TT" : getTT(c)})
    info.update({"iEta" : getEtaPhi(c)[0]})
    info.update({"iPhi" : getEtaPhi(c)[1]})
    return info
  def getEEInfo(c):
    def iz(c):
      return getXYZ(c)[2]
#      return (-1, 1)[c & 0x4000 > 0]  
    def idee(c):
      x = getXYZ(c)[0]
      y = getXYZ(c)[1]
      if iz(c) == -1:
        x = x + 100
      if x <= 50:
        return 1
      elif x > 50 and x <= 100:
        return 2
      elif x > 100 and x <= 150:
        return 4
      elif x > 150:
        return 3
      else:
        log.error("Cannot get Dee for channel '{0}'".format(c))
    x = getXYZ(c)[0]
    y = getXYZ(c)[1]
    while x > 50:
      x -= 50
    def is1or9():
      return (40 <= x <= 50 and y > 60) or (35 <= x <= 50 and y > 65) or (30 <= x <= 50 and y > 70) or \
             (25 <= x <= 50 and y > 75) or (20 <= x <= 50 and y > 85)
    def is2or8():
      return (not is1or9()) and ((35 <= x <= 50 and y > 50) or (10 <= x <= 50 and y > 55) or (3 <= x <= 50 and y > 60))
    def is3or7():
      return (not is1or9() and not is2or8()) and ((5 <= x <= 10 and y > 25) or (5 <= x <= 20 and y > 30) or \
      (3 <= x <= 30 and y > 35) or (0 <= x <= 35 and y > 40) or (0 <= x <= 10 and y > 55))
    def is4or6():
      return (not is1or9() and not is2or8() and not is3or7()) and ((25 <= x <= 35 and y > 5) or (20 <= x <= 35 and y > 8) or \
      (15 <= x <= 35 and y > 13) or (13 <= x <= 40 and y > 15) or (7 <= x <= 40 and y > 20) or (10 <= x <= 40 and y  > 25) or \
      (20 <= x <= 45 and y > 30) or (30 <= x <= 45 and y > 35) or (35 <= x <= 45 and y > 40))
    def is5():
      return (not is1or9() and not is2or8() and not is3or7() and not is4or6())
    d = {is1or9 : [1, 9], is2or8 : [2, 8], is3or7: [3, 7], is4or6: [4, 6], is5: [5]}
    for f in sorted(d.keys()):
      if f():
        psm = d[f]
        break
    sm = (min(psm), max(psm))[idee(c) == 2 or idee(c) == 3]
    sm = sm * iz(c)
    info = {'id' : c}
    info.update({'location' : getSubDetector(c) + "{0:+03d}".format(sm)})
    info.update({"iX" : getXYZ(c)[0]})
    info.update({"iY" : getXYZ(c)[1]})
    info.update({"iZ" : iz(c)})
    info.update({"Dee": idee(c)})
    return info
  location = getSubDetector(c)
  if location == "EE":
    return getEEInfo(c)
  elif location == "EB":
    return getEBInfo(c)
  else:
    log.error("Cannot determine location for channel '{0}'".format(c))

def getTT(channel):
  """
    Returns TT number for channel
  """
  channel = str(channel)
  l1 = getXtal(channel)
  l2 = getSM(channel)
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

def getSM(channel):
  """
    Returns SM number for EB channel
  """
  eb = int(str(channel)[-6:-4])
  return (eb, 18 - eb)[eb > 18]

def getEtaPhi(channel):
  """
    Return (Eta, Phi) tuple for EB channels
  """
  ch = int(channel) - 1011000000
  xtal = ch % 10000
  sm = (ch - xtal) / 10000
  if sm < 19:
    return ((xtal - 1) / 20, 19 - (xtal - 1) % 20  + (sm - 1) * 20 + 1)
  else:
    return (84 - (xtal - 1) / 20 - 85, (xtal - 1) % 20 + (sm - 19) * 20 + 1)

def getXYZ(channel):
  """
    Return (x, y , -1|1 ) tuple for EE channels
  """
  channel = int(channel) - 2010000000
  side = channel / 1000000
  channel = channel - (side * 1000000)
  y = channel % 1000
  x = channel / 1000
  return (x, y, (1, -1)[side == 0])

def getSubDetector(channel):
  """
    Returns EB|EE detector place of channel
  """
  if str(channel)[0] == "1":
    return "EB"
  else:
    return "EE"

def regexp(expr, item):
  """
    Function for REGEXP sqlite3 operator
  """  
  reg = re.compile(expr)
  return reg.search(item) is not None
