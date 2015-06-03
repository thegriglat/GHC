#!/usr/bin/env python

import sys
import argparse

sys.path.append("modules")
import Data
import log

parser = argparse.ArgumentParser()
parser.add_argument('files', metavar="sqlite3db", nargs="+", help = "File(s) to analyse.")
parser.add_argument('-v','--verbose', help = "Enable output of channel data.", dest = "verbose", action = "store_true")
args = parser.parse_args()

def getRMS(value):
  from numpy import mean, sqrt, square
  return sqrt(mean(square(value)))

data = {}

for D in args.files:
  log.info("Reading file " + D + " ...")
  try:
    g = Data.Data()
    g.Load(D)
    data.update({D : g})
    log.info("Finished " + D + ".")
    del g
  except Exception as e:
    log.error(e)

print "=== Compare GHC runs ==="
def getGHCStats(g):
  print "  " + f + " ==="
  print "  Active channels                         :", len(g.getActiveChannels())
  print "  Masked channels                         :", g.numOfInactiveChannels()
  print "  Total Problematic channels              :", g.dbh.execute("select count(distinct channel_id) from flags").fetchone()[0]
  print "  Channels with design performance in G12 :", len(g.getActiveChannels()) - g.dbh.execute("select count(distinct channel_id) from flags where flag REGEXP '([BD]P|V?LR)G12'").fetchone()[0]
  print "  Noisy (2 <= rms <= 6 ADC counts) in G12 :", len(g.getChannelsByFlag("LRG12"))
  print "  Very noisy (rms > 6 ADC counts) in G12  :", len(g.getChannelsByFlag("VLRG12"))
  print "  Pedestal rms ADC counts in G12          :", getRMS([c[0] for c in g.dbh.execute("select value from data_pedestal_hvon where key = 'PED_RMS_G12'")])
  print "  Pedestal rms ADC counts in G6           :", getRMS([c[0] for c in g.dbh.execute("select value from data_pedestal_hvon where key = 'PED_RMS_G6'")])
  print "  Pedestal rms ADC counts in G1           :", getRMS([c[0] for c in g.dbh.execute("select value from data_pedestal_hvon where key = 'PED_RMS_G1'")])
  print "  APD with bad or no connection to HV     :", g.dbh.execute("select count(distinct channel_id) from flags where flag like 'BV%'").fetchone()[0]
  print "  Dead channels due to LVR board problems :", len(g.getChannelsByFlag("DLAMPL"))

for f in data.keys():
  getGHCStats(data[f])

if args.verbose:
  channels_flags = {}
  for f in data.keys():
    g = data[f]
    for c in g.getProblematicChannels():
      flag = g.getFlagsByChannel(c)
      if channels_flags.has_key(c):
        channels_flags[c].update({f : flag})
      else:
        channels_flags[c] = {f : flag}
  for c in channels_flags.keys():
    ch = channels_flags[c]
    for f1 in ch.keys():
      for f2 in ch.keys():
        if f2 == f1:
          continue
        if ch[f1] != ch[f2]:
          # only differences
          def printdata(g, c):
            d = g.getChannelData(c)
            print  "\n".join(["   | {0:20s} = {1}".format(k, d[k]) for k in d.keys()])
          print "="*80
          print "  ==> ", c
          print "  Info: ", ", ".join(["{0}: {1}".format(i, str(Data.getChannelInfo(c)[i])) for i in Data.getChannelInfo(c).keys() if i != "id"])
          print "   in '{0}'                 : ".format(f1) + ", ".join(ch[f1])
          print "   in '{0}'                 : ".format(f2) + ", ".join(ch[f2])
          print "   in '{0}' but '{1}'       : ".format(f1,f2) + ", ".join([i for i in list(set(ch[f1]) - set(ch[f2]))])
          print "   in '{0}' but '{1}'       : ".format(f2,f1) + ", ".join([i for i in list(set(ch[f2]) - set(ch[f1]))])
          print "   union of '{0}' and '{1}' : ".format(f2,f1) + ", ".join([i for i in list(set(ch[f2] + ch[f1]))])
          print "   ==> Data for channel {0} from '{1}' <==".format(c, f1)
          printdata(data[f1], c)
          print "   ==> Data for channel {0} from '{1}' <==".format(c, f2)
          printdata(data[f2], c)
          print "="*80
  
