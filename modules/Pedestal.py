#!/usr/bin/env python
import Data
import log

class PedestalData(Data.Data):

  def __init__(self, database = ":memory:"):
    super(PedestalData, self).__init__(database)
    self.runtype = "pedestal"
    self.description = "Pedestal"
    self.channels = {}

  def readData(self, source):
    return self.readPedestal(source)    
  
  def getChannelFlags(self, channel):
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
    data = self.channels[channel]["data"]
    flags = []
    if self.getOption("pedestallimits") != None:
      limits = self.getOption("pedestallimits")
    else:
      limits = {"G1" : ((1, 0.2), (1.1, 3)), "G6" : ((1, 0.4), (1.3, 4)), "G12" : ((1, 0.5), (2.1, 6))}
    flags += PedestalComparison("G1", limits["G1"][0], limits["G1"][1])
    flags += PedestalComparison("G6", limits["G6"][0], limits["G6"][1])
    flags += PedestalComparison("G12", limits["G12"][0], limits["G12"][1])
    return list(set(flags))

  def readChannel(self, str):
    """
      Read channel data from string
    """
    str = str.strip()
    try:
      IOV_ID, channelid, gain1, rms1, gain6, rms6, gain12, rms12, taskstatus = str.split()
    except:
      log.error( "  Cannot parse line\n  '{0}'\n  for 9 fields!")
    if not self.channels.has_key(channelid):
      return False
      log.debug("  Hmm. It seems channel {0} is not present in list of all channels. Continue ...".format(channelid))
    else:
      self.setChannelData(channelid, {"G1": [float(gain1), float(rms1)], "G6" : [float(gain6), float(rms6)], "G12" : [float(gain12), float(rms12)]})
      return True

  def readPedestalsDB(self, connstr, runnum):
    """
      Read pedestal values from database
        connstr : connection string to database
        runnum  : array of runs which contains data
    """
    import Database
    log.info("Trying to connect to Oracle")
    dbh = Database.OracleDB(connstr.split('oracle://')[1])
    log.info("OK")
    log.info("Exporting data from Oracle to inner DB ...")
    for run in sorted(runnum):
      log.info("Process run " + str(run) + " ...")
      result = dbh.execute("select LOGIC_ID, PED_MEAN_G1, PED_RMS_G1, PED_MEAN_G6, PED_RMS_G6, PED_MEAN_G12, PED_RMS_G12 \
        from MON_PEDESTALS_DAT where IOV_ID=(select IOV_ID from MON_RUN_IOV where RUN_IOV_ID=(select IOV_ID from RUN_IOV where RUN_NUM={0}))".format(run))
      self.dbh.execute("insert into runs values ({0}, 'pedestal')".format(int(run)))
      for row in result:
        self.dbh.execute("insert into data values ({0}, {1}, 'PED_MEAN_G1', {2})".format(int(run), int(row[0]),  row[1]))
        self.dbh.execute("insert into data values ({0}, {1}, 'PED_RMS_G1', {2})".format(int(run), int(row[0]),   row[2]))
        self.dbh.execute("insert into data values ({0}, {1}, 'PED_MEAN_G6', {2})".format(int(run), int(row[0]),  row[3]))
        self.dbh.execute("insert into data values ({0}, {1}, 'PED_RMS_G6', {2})".format(int(run), int(row[0]),   row[4]))
        self.dbh.execute("insert into data values ({0}, {1}, 'PED_MEAN_G12', {2})".format(int(run), int(row[0]), row[5]))
        self.dbh.execute("insert into data values ({0}, {1}, 'PED_RMS_G12', {2})".format(int(run), int(row[0]),  row[6]))
    dbh.close()

  def readPedestal(self, source = None, **kwargs):
    """
      Switch-function for readin pedestal data.
        source : filename or oracle://<connection string>
        kwargs : runnum, ...
    """
    if  "oracle://" in source:
      if kwargs.has_key('runnum'):
        self.readPedestalsDB(source, kwargs['runnum'])
      else:
        log.error( "Run number is not specified in readPedestal!")
    else:
      log.info( "Reading Pedestal data ...")
      n = 0
      for line in open(source, 'r').readlines()[1:]:
        if self.readChannel(line):
          n = n + 1
      log.info( "Done. Processed {0} records.".format(n))
      return n

