#!/usr/bin/env python

import sys
import argparse

sys.path.append("modules")
import Data
import log

parser = argparse.ArgumentParser()
parser.add_argument('files', metavar="sqlite3db", nargs="+", help = "File(s) to analyse.")
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
  print "  Pedestal rms ADC counts in G12          :", getRMS([c[0] for c in g.dbh.execute("select value from data_pedestal_hvon where key = 'PED_RMS_G12'").fetchall()])
  print "  Pedestal rms ADC counts in G6           :", getRMS([c[0] for c in g.dbh.execute("select value from data_pedestal_hvon where key = 'PED_RMS_G6'").fetchall()])
  print "  Pedestal rms ADC counts in G1           :", getRMS([c[0] for c in g.dbh.execute("select value from data_pedestal_hvon where key = 'PED_RMS_G1'").fetchall()])
  print "  APD with bad or no connection to HV     :", g.dbh.execute("select count(distinct channel_id) from flags where flag like 'BV%'").fetchone()[0]
  print "  Dead channels due to LVR board problems :", len(g.getChannelsByFlag("DLAMPL"))

for f in data.keys():
  getGHCStats(data[f])
  
