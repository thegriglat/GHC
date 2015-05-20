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
        sum += self.getChannel(c)["data"][gain][0]
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
    if not self.getChannels().has_key(channelid):
      return False
    else:
      self.setChannelData(channelid, {"Laser": [float(gain12), float(rms12)], "APD/PN" : [float(APD_OVER_PN_MEAN), float(APD_OVER_PN_RMS)]})
      self.channels[channelid]["active"] = True
      return True
  
  def readLaserDB(self, connstr, runnum):
    """
      Read test pulse values from database
        connstr : connection string to database
        runnum  : array of runs which contains data
    """
    import Database
    dbh = Database.DB(connstr.split('oracle://')[1])
    table = self.getOption("LaserDBTable")
    table = (table, "MON_LASER_IRED_DAT")[table == None]
    for run in runnum:
      result = dbh.execute("select LOGIC_ID, APD_MEAN, APD_RMS, APD_OVER_PN_MEAN, APD_OVER_PN_RMS \
        from {0} where IOV_ID=(select IOV_ID from MON_RUN_IOV where RUN_IOV_ID=(select IOV_ID from RUN_IOV where RUN_NUM={1}))".format(table, run))
      for row in result:
        if self.getChannels().has_key(str(row[0])):
          values = {}
          data = self.channels[str(row[0])]["data"]
          idx = 1
          for k in ('Laser', 'APD/PN'):
            q = 2 * idx - 1
            if data.has_key(k):
              values[k] = [(data[k][0], row[q])[row[q] != -1.0],
                           (data[k][1], row[q + 1])[row[q + 1] != -1.0]
                          ]
            else:
              values[k] = [row[q], row[q + 1]]
            idx += 1
          self.setChannelData(str(row[0]), {'Laser': values['Laser'], "APD/PN" : values['APD/PN']})
    dbh.close()
    return result

  def readLaser(self, source = None, **kwargs):
    if  "oracle://" in source:
      if kwargs.has_key('runnum'):
        self.readLaserDB(source, kwargs['runnum'])
      else:
        log.error( "Run number is not specified in readLaser!")
    else:
      log.info ("Reading Laser blue data ...")
      n = 0
      for line in source.readlines():
        if self.readChannel(line):
          n = n + 1
      log.info( "Done. Processed {0} records.".format(n))
      return n


