#!/usr/bin/env python
import Data
import log

class PedestalData(Data.Data):

  def __init__(self):
    super(PedestalData, self).__init__()
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
      print "  Cannot parse line\n  '{0}'\n  for 9 fields!"
    if not self.channels.has_key(channelid):
      return False
#      print "  Hmm. It seems channel {0} is not present in list of all channels. Continue ...".format(channelid)
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
    dbh = Database.DB(connstr.split('oracle://')[1])
    for run in sorted(runnum):
      result = dbh.execute("select LOGIC_ID, PED_MEAN_G1, PED_RMS_G1, PED_MEAN_G6, PED_RMS_G6, PED_MEAN_G12, PED_RMS_G12 \
        from MON_PEDESTALS_DAT where IOV_ID=(select IOV_ID from MON_RUN_IOV where RUN_IOV_ID=(select IOV_ID from RUN_IOV where RUN_NUM={0}))".format(run))
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
              log.debug("RUN {0:6s} | Old [mean, RMS] values for gain {1:3s}, channel {2:13d}: {3}".format(run, k, row[0], (row[q], row[q + 1])))
              log.debug("RUN {0:6s} | New [mean, RMS] values for gain {1:3s}, channel {2:13d}: {3}".format(run, k, row[0], values[k]))
            else:
              values[k] = [row[q], row[q + 1]]
            idx += 1
          self.setChannelData(str(row[0]), {'G1': values['G1'], "G6" : values['G6'], "G12" : values['G12']})
    
    dbh.close()
    return result

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
        print "Run number is not specified in readPedestal!"
    else:
      print "Reading Pedestal data ..."
      n = 0
      for line in open(source, 'r').readlines()[1:]:
        if self.readChannel(line):
          n = n + 1
      print "  Done. Processed {0} records.".format(n)
      return n

