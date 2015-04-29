#!/usr/bin/env python

import Data

class TestPulseData(Data.Data):

  def __init__(self):
    super(TestPulseData, self).__init__()
    self.runtype = "testpulse"
    self.description = "Test Pulse"
    self.average = {}

  def readData(self, source):
    return self.readTestPulse(source)    
  
  def getChannelFlags(self, channel):
    data = self.channels[channel]["data"]
    flags = []
    for i in ('1', '6', '12'):
      if data["G" + i][0] <= 0:
        flags.append("DTPG" + i)
      if data["G" + i][0] / self.getAvgGain("G" + i) <= 0.5:
        flags.append("STPG" + i)
      if data["G" + i][0] / self.getAvgGain("G" + i) > 1.5:
        flags.append("LTPG" + i)
    return list(set(flags))

  def getAvgGain(self, gain):
    """
      Returns average  value for <gain>. The function caches results.
    """
    if self.average.has_key(gain):
      return self.average[gain]
    else:
      sum = 0
      ach = self.getActiveChannels()
      for c in ach:
        sum += self.channels[c]["data"][gain][0]
      self.average[gain] = sum / float(len(ach))
      return self.average[gain]

  def readChannel(self, str):
    str = str.strip()
    try:
      IOV_ID, channelid, gain1, gain6, gain12, rms1, rms6, rms12, taskstatus = str.split()
    except:
      log.error( "  Cannot parse line\n  '{0}'\n  for 9 fields!")
    if not self.channels.has_key(channelid):
      return False
    else:
      self.setChannelData(channelid, {"G1": [float(gain1), float(rms1)], "G6" : [float(gain6), float(rms6)], "G12" : [float(gain12), float(rms12)]})
      return True
    
  def readTestPulseDB(self, connstr, runnum):
    """
      Read test pulse values from database
        connstr : connection string to database
        runnum  : array of runs which contains data
    """
    import Database
    dbh = Database.DB(connstr.split('oracle://')[1])
    for run in runnum:
      result = dbh.execute("select LOGIC_ID, ADC_MEAN_G1, ADC_RMS_G1, ADC_MEAN_G6, ADC_RMS_G6, ADC_MEAN_G12, ADC_RMS_G12 \
        from MON_TEST_PULSE_DAT where IOV_ID=(select IOV_ID from MON_RUN_IOV where RUN_IOV_ID=(select IOV_ID from RUN_IOV where RUN_NUM={0}))".format(run))
      for row in result:
        if self.channels.has_key(str(row[0])):
          values = {}
          data = self.channels[str(row[0])]["data"]
          idx = 1
          for k in ('G1', 'G6', 'G12'):
            q = 2 * idx - 1
            if data.has_key(k):
              values[k] = [(data[k][0], row[q])[row[q] != -1.0],
                           (data[k][1], row[q + 1])[row[q + 1] != -1.0]
                          ]
            else:
              values[k] = [row[q], row[q + 1]]
            idx += 1
          self.setChannelData(str(row[0]), {'G1': values['G1'], "G6" : values['G6'], "G12" : values['G12']})

    dbh.close()
    return result


  def readTestPulse(self, source = None, **kwargs):
    if  "oracle://" in source:
      if kwargs.has_key('runnum'):
        self.readTestPulseDB(source, kwargs['runnum'])
      else:
        log.error( "Run number is not specified in readTestPulse!")
    else:
      log.info( "Reading Test Pulse data ...")
      n = 0
      for line in open(source, 'r').readlines()[1:]:
        if self.readChannel(line):
          n = n + 1
      log.info( "  Done. Processed {0} records.".format(n))
      return n

