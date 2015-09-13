#!/usr/bin/env python

import os
import sys
import shutil
import argparse
import datetime

startts = datetime.datetime.now()
sys.path.append("modules")
import log
import Data

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--dbstr', help="Connection string to DB (oracle://user/pass@db). Don't use this if you want to read files.", dest='dbstr', default = "files")
parser.add_argument('-pon', help="Pedestal HV ON  runs numbers or list of files", dest='pon_runs')
parser.add_argument('-poff',help="Pedestal HV OFF runs numbers or list of files", dest='poff_runs')
parser.add_argument('-tp',  help="Test Pulse runs numbers or list of files", dest='tp_runs')
parser.add_argument('-l',help="Laser runs or list of files", dest='l_runs')
parser.add_argument('-lt', '--lasertable', help="Laser table to use in Oracle DB", dest='lasertable', default = "MON_LASER_BLUE_DAT", metavar = "TABLE")
parser.add_argument('-o', '--output', help="Results directory", dest='output', metavar = "DIRECTORY")
parser.add_argument('-i', '--import', help="Import DB from sqlite3", dest='importdb', metavar = "DB")
parser.add_argument('-d', '--dump', help="Dump internal database in sqlite3 database", dest='dump', metavar = "DB")
parser.add_argument('-ds', '--dumpsql', help="Dump internal database in SQL", dest='dumpsql', metavar = "SQL")
parser.add_argument('-f', '--format', help="Image format", dest='imgformat', default = "png", metavar = "FORMAT")
parser.add_argument('-v', '--verbose', help="Be more verbose", action="store_true", default=False, dest='verbose')
parser.add_argument('-np', '--no-plots', help="Don't make plots", action="store_true", default=False, dest='noplots')
args = parser.parse_args()

format = args.imgformat

if not args.output:
  outputdir = "RESULTS"
else:
  outputdir = args.output
if not os.path.exists(outputdir):
  os.mkdir(outputdir)

header = lambda text, level = 1: "h{1}. {0}".format(text, level)

GHC = Data.Data()
if args.importdb == None:
  if args.dbstr == "files":
    log.info ("!!! The data will be readed from files !!!")
  source = args.dbstr

  GHC.readAllChannels("data/EB_all_ch.txt")
  GHC.readAllChannels("data/EE_all_ch.txt")
  if args.pon_runs is not None:
    GHC.readData(source, runs=args.pon_runs.split(), type="pedestal_hvon")
  if args.poff_runs is not None:
    GHC.readData(source, runs=args.poff_runs.split(), type="pedestal_hvoff")

  if args.tp_runs is not None:
    GHC.readData(source, runs=args.tp_runs.split(), type="testpulse")
  if args.l_runs is not None:
    GHC.readData(source, runs=args.l_runs.split(), type="laser", lasertable=args.lasertable)
else:
  GHC.Load(args.importdb)

GHC.classifyChannels()

if args.dump != None:
  if os.path.exists(args.dump):
    os.remove(args.dump)
  GHC.Export(args.dump)
if args.dumpsql != None:
  if os.path.exists(args.dumpsql):
    os.remove(args.dumpsql)
  Data.DumpSQL(GHC.dbh, args.dumpsql)

print ""
print header("PEDESTAL ANALYSIS")
# description of error types
print """
<pre>
Description of errors for EB
  Dead pedestal  (DP)  :
    Gain 1 : MEAN <= 1 or RMS <= 0.2
    Gain 6 : MEAN <= 1 or RMS <= 0.4
    Gain 12: MEAN <= 1 or RMS <= 0.5
  Bad pedestal   (BP)  :
    abs(MEAN - 200) >= 30 and MEAN > 1
  Large RMS      (LR)  :
    Gain 1 : (not (MEAN <= 1 or RMS <= 0.2)) and (RMS >= 1.1 and RMS < 3 and MEAN > 1)
    Gain 6 : (not (MEAN <= 1 or RMS <= 0.4)) and (RMS >= 1.3 and RMS < 4 and MEAN > 1)
    Gain 12: (not (MEAN <= 1 or RMS <= 0.5)) and (RMS >= 2.1 and RMS < 6 and MEAN > 1)
  Very Large RMS (VLR) :
    Gain 1 : (not (MEAN <= 1 or RMS <= 0.2)) and (RMS > 3 and MEAN > 1)
    Gain 6 : (not (MEAN <= 1 or RMS <= 0.4)) and (RMS > 4 and MEAN > 1)
    Gain 12: (not (MEAN <= 1 or RMS <= 0.5)) and (RMS > 6 and MEAN > 1)

Description of errors for EE
  Dead pedestal  (DP)  :
    Gain 1 : MEAN <= 1 or RMS <= 0.2
    Gain 6 : MEAN <= 1 or RMS <= 0.4
    Gain 12: MEAN <= 1 or RMS <= 0.5
  Bad pedestal   (BP)  :
    abs(MEAN - 200) >= 30 and MEAN > 1
  Large RMS      (LR)  :
    Gain 1 : (not (MEAN <= 1 or RMS <= 0.2)) and (RMS >= 1.5 and RMS < 4 and MEAN > 1)
    Gain 6 : (not (MEAN <= 1 or RMS <= 0.4)) and (RMS >= 2.0 and RMS < 5 and MEAN > 1)
    Gain 12: (not (MEAN <= 1 or RMS <= 0.5)) and (RMS >= 3.2 and RMS < 7 and MEAN > 1)
  Very Large RMS (VLR) :
    Gain 1 : (not (MEAN <= 1 or RMS <= 0.2)) and (RMS > 4 and MEAN > 1)
    Gain 6 : (not (MEAN <= 1 or RMS <= 0.4)) and (RMS > 5 and MEAN > 1)
    Gain 12: (not (MEAN <= 1 or RMS <= 0.5)) and (RMS > 7 and MEAN > 1)


Description of HV OFF errors:
  Bad Voltage for G12 (BV):
    abs(MEAN(HVON) - MEAN(HVOFF)) < 0.2 and 170 <= MEAN (HVON) <= 230
</pre>
"""

for d in ["EB", "EE"]:
  if args.pon_runs is None:
    continue
  print header("PEDESTAL {0} ANALYSIS".format(d), 2)
  print ""
  act = GHC.numOfActiveChannels(d, type=['pedestal_hvon', 'pedestal_hvoff'])
  print " Number of missed channels   : {0}".format((61200,14648)[d == "EE"] - act)
  print " Number of active channels   : {0}\n".format(act)
  print "Statistics of channels by problem classes"
  print ""
  print "|_. {classn:41s} |_. {empty:3s} |_. {tags:21s} |".format(classn = "Classes of pedestal problematic channels", empty="", tags="Short name")

  shorter = lambda x: len([ c for c in GHC.getChannelsByFlag(x) if Data.getSubDetector(c) == d]) 
  for k in ["G1", "G6", "G12"]:
    print "| {0:43s} | {1:5d} | {2:23s} |".format("Dead pedestal channels", shorter("DP" + k), "DP" + k)
    print "| {0:43s} | {1:5d} | {2:23s} |".format("Pedestal mean outside [170,230]", shorter("BP" + k), "BP" + k)
    print "| {0:43s} | {1:5d} | {2:23s} |".format("Large RMS (noisy channels)", shorter("LR" + k), "LR" + k)
    print "| {0:43s} | {1:5d} | {2:23s} |".format("Very large RMS (very noisy channels)", shorter("VLR" + k), "VLR" + k)
    print "| {0:43s} | {1:5d} | {2:23s} |".format("Bad pedestal and noisy channels", shorter(["BP" + k, "LR" + k]), "BP" + k +"+LR" + k)
    print "| {0:43s} | {1:5d} | {2:23s} |".format("Bad pedestal and very noisy", shorter(["BP" + k,"VLR" + k]), "BP" + k + "+VLR" + k)
  del shorter

  print ""

  tpc = 0
  print "h3. Statistics by FLAGS:\n"
  print "|_. Flag |_. Number of channels |"
  for k in ["G1", "G6", "G12"]:
    for i in GHC.PEDESTAL_FLAGS:
      num = GHC.cur.execute("select count( distinct channel_id) from flags where flag = '{0}' and channel_id like '{1}%'".format(i + k, (2,1)[d == "EB"])).fetchone()[0]
      tpc += num
      print "| {0:8s} | {1:5d} |".format(i + k, num)
  print ""


print header("TEST PULSE ANALYSIS")
# errors description
print """
<pre>
Dead TestPulse          (DTP):
  MEAN = 0

Low TestPulse amplitude (STP):
  AVG = average mean for each subdetector (EB, EE)
  MEAN > 0 and MEAN < 0.5 * AVG

Large TP amplitude      (LTP):
  MEAN > 1.5 * AVG
</pre>

"""

for d in ("EB", "EE"):
  if args.tp_runs is None:
    continue
  print header("TEST PULSE {0} ANALYSIS".format(d), 2)
  print ""

  act = GHC.numOfActiveChannels(d, type='testpulse')
  print " Number of missed channels   : {0}".format((61200,14648)[d == "EE"] - act)
  print " Number of active channels   : {0}\n".format(act)
#  print "p. Statistics of channels by problem classes: "
  print ""
  print "|_. {classn:41s} |_. {empty:3s} |_. {tags:21s} |".format(classn = "Classes of Test Pulse problematic channels", empty="", tags="Short name")

  shorter = lambda x: len([ c for c in GHC.getChannelsByFlag(x) if Data.getSubDetector(c) == d]) 
  for k in ("G1", "G6", "G12"):
    print "| {0:43s} | {1:5d} | {2:23s} |".format("Dead TP channels", shorter("DTP" + k), "DTP" + k)
    print "| {0:43s} | {1:5d} | {2:23s} |".format("Low TP amplitude", shorter("STP" + k), "STP" + k)
    print "| {0:43s} | {1:5d} | {2:23s} |".format("Large TP amplitude", shorter("LTP" + k), "LTP" + k)
  print ""
  del shorter

  tpc = 0
  print "h3. Statistics by FLAGS:\n"
  print "|_. Flag |_. Number of channels |"
  for k in ("G1", "G6", "G12"):
    for i in GHC.TESTPULSE_FLAGS:
      num = GHC.cur.execute("select count( distinct channel_id) from flags where flag = '{0}' and channel_id like '{1}%'".format(i + k, (2,1)[d == "EB"])).fetchone()[0]
      tpc += num
      print "| {0:8s} | {1:5d} |".format(i + k, num)
  print ""

print ""
print header("LASER ANALYSIS")
# errors description
print """
<pre>
  DLAMPL: MEAN <= 0
  SLAMPL: MEAN > 0 and MEAN < AVG * 0.1         # AVG per subdetector
  LLERRO: MEAN > AVG * 0.1 and RMS / MEAN > 0.1 # AVG per subdetector
</pre>
"""

for d in ("EB", "EE"):
  if args.l_runs is None:
    continue
  print ""
  print header("LASER {0} ANALYSIS".format(d), 2)
  print ""

  act = GHC.numOfActiveChannels(d, type='laser')
  print " Number of missed channels   : {0}".format((61200,14648)[d == "EE"] - act)
  print " Number of active channels   : {0}".format(act)

  print "\nh3. Statistic by FLAG :\n"
  print "|_. Flag |_. Number of channels |"
  shorter = lambda x: len([ c for c in GHC.getChannelsByFlag(x) if Data.getSubDetector(c) == d]) 
  for i in GHC.LASER_FLAGS:
    print "| {0:15s} | {1:5d} |".format(i, shorter(i))

for d in ("EB", "EE"):
  pre = "^[BD]P|^V?LR"
  tpre = "^[DSL]TP"
  lre = "^[DS]LAMPL|LLERRO"
  hvre = "^BV"
  def getchnum (x):
    all = [pre, tpre, lre, hvre]
    rall = list(set(all) - set(x))
    if len(rall) == 0:
      return 0
    # at least philosophy
    sql = "select count(distinct channel_id) from flags where channel_id like '{loc}' and channel_id in {exsql} and channel_id not in (select channel_id from missed_channels)".format(loc = ("1%", "2%")[d == "EE"],
           exsql = " and channel_id in ".join(["(select channel_id from flags where flag REGEXP '{0}')".format(i) for i in x]))
    return GHC.dbh.execute(sql).fetchone()[0]
  print ""
  print header("Summary Total Problematic Channels for {0} (\"AT LEAST\" meaning)".format(d))
  print ""
  print "|_. Problem classes                            |_. Number of channels |"
  print "|  Total problematic channels                  |           * |", GHC.dbh.execute("select count(distinct channel_id) from flags where channel_id like '{loc}' and channel_id not in (select channel_id from missed_channels)".format(loc = ('2%','1%')[d == "EB"])).fetchone()[0], "|"
  print "|  Pedestals problems                          |          PE |", getchnum([pre]), "|"
  print "|  Test Pulse problems                         |          TP |", getchnum([tpre]), "|"
  print "|  Laser problems                              |          LA |", getchnum([lre]), "|"
  if d != "EE":
    print "|  High voltage problems                       |          HV |", getchnum([hvre]), "|"
  print "|  Pedestals + Test Pulse problems             |       PE+TP |", getchnum([pre, tpre]), "|"
  print "|  Pedestals + Laser problems                  |       PE+LA |", getchnum([pre, lre]), "|"
  if d != "EE":
    print "|  Pedestals + High voltage problems           |       PE+HV |", getchnum([pre, hvre]), "|"
  print "|  Test Pulse + Laser problems                 |       TP+LA |", getchnum([tpre, lre]), "|"
  if d != "EE":
    print "|  Test Pulse + High voltage problems          |       TP+HV |", getchnum([tpre, hvre]), "|"
    print "|  Laser + High voltage problems               |       LA+HV |", getchnum([lre, hvre]), "|"
  print "|  Pedestals + Test Pulse + Laser problems     |    PE+TP+LA |", getchnum([pre, tpre, lre]), "|"
  if d != "EE":
    print "|  Pedestals + Test Pulse + HV problems        |    PE+TP+HV |", getchnum([pre, tpre, hvre]), "|"
    print "|  Pedestals + Laser + HV problems             |    PE+LA+HV |", getchnum([pre, lre, hvre]), "|"
    print "|  Test Pulse  + Laser + HV problems           |    TP+LA+HV |", getchnum([tpre, lre, hvre]), "|"
    print "|  Pedestal + Test Pulse + Laser + HV problems | PE+TP+LA+HV |", getchnum([pre, tpre, lre, hvre]), "|"
  print ""


if args.verbose:
  GHC.printProblematicChannels()

if not args.noplots:
# plotting
#print header("Preparing plots ...")
  for i in ['pedestals_hvon', 'pedestals_hvoff', 'testpulse', 'laser']:
    if not os.path.exists(outputdir + "/" + i):
        os.mkdir(outputdir + "/" + i)

  for d in ("EB", "EE"):
    for rms in (True, False):
      for i in ("G1", "G6", "G12"):
        ### 1D plots
        h = GHC.get1DHistogram(key = "PED_{0}_".format(('MEAN', 'RMS')[rms]) + i, useRMS = rms, type="pedestal_hvon", part = d, name = "Pedestal {0}, gain {1} ({2})".format(('mean', 'RMS')[rms], i, "HV ON"))
        Data.saveHistogram(h, outputdir + "/pedestals_hvon/{0}_{1}_{2}.1D.{3}".format(i, ("MEAN", "RMS")[rms], d, format), d)
  
        h = GHC.get1DHistogram(key = "PED_{0}_".format(('MEAN', 'RMS')[rms]) + i, useRMS = rms, type="pedestal_hvoff", part = d ,name = "Pedestal {0}, gain {1} ({2})".format(('mean', 'RMS')[rms], i, "pedestal_hvoff"))
        Data.saveHistogram(h, outputdir + "/pedestals_hvoff/{0}_{1}_{2}.1D.{3}".format(i, ("MEAN", "RMS")[rms], d, format), d)
      
        h = GHC.get1DHistogram(key = "ADC_{0}_".format(('MEAN', 'RMS')[rms]) + i, useRMS = rms, type="testpulse", part = d, name = "Test Pulse {0}, gain {1}".format(('mean', 'RMS')[rms], i))
        Data.saveHistogram(h, outputdir + "/testpulse/{0}_{1}_{2}.1D.{3}".format(i, ("MEAN", "RMS")[rms], d, format), d)
        
        ### 2D plots
        h = GHC.get2DHistogram(key = "PED_{0}_".format(('MEAN', 'RMS')[rms]) + i, useRMS = rms, type="pedestal_hvon", part = d, name = "Pedestal {0}, gain {1} ({2})".format(('mean', 'RMS')[rms], i, "HV ON"))
        Data.saveHistogram(h, outputdir + "/pedestals_hvon/{0}_{1}_{2}.2D.{3}".format(i, ("MEAN", "RMS")[rms], d, format), d)
        h = GHC.get2DHistogram(key = "PED_{0}_".format(('MEAN', 'RMS')[rms]) + i, useRMS = rms, type="pedestal_hvoff", part = d, name = "Pedestal {0}, gain {1} ({2})".format(('mean', 'RMS')[rms], i, "pedestal_hvoff"))
        Data.saveHistogram(h, outputdir + "/pedestals_hvoff/{0}_{1}_{2}.2D.{3}".format(i, ("MEAN", "RMS")[rms], d, format), d)
        h = GHC.get2DHistogram(key = "ADC_{0}_".format(('MEAN', 'RMS')[rms]) + i, useRMS = rms, type="testpulse", part = d, name = "Test Pulse {0}, gain {1}".format(('mean', 'RMS')[rms], i))
        Data.saveHistogram(h, outputdir + "/testpulse/{0}_{1}_{2}.2D.{3}".format(i, ("MEAN", "RMS")[rms], d, format), d)
  
    ### laser plots
      h = GHC.get1DHistogram(key = "APD_{0}".format(('MEAN', 'RMS')[rms]), useRMS = rms, type="laser", part = d, name = "Laser {0}, ({1})".format(('mean', 'RMS')[rms] , args.lasertable))
      Data.saveHistogram(h, outputdir + "/laser/Laser_{0}_{1}.1D.{2}".format(("MEAN", "RMS")[rms], d, format), d)
      h = GHC.get1DHistogram(key = "APD_OVER_PN_{0}".format(('MEAN', 'RMS')[rms]), useRMS = rms, type="laser", part = d, name = "APD/PN {0}, ({1})".format(('mean', 'RMS')[rms], args.lasertable))
      Data.saveHistogram(h, outputdir + "/laser/APDPN_{0}_{1}.1D.{2}".format(("MEAN", "RMS")[rms], d, format), d)
      h = GHC.get2DHistogram(key = "APD_{0}".format(('MEAN', 'RMS')[rms]), useRMS = rms, type="laser", part = d, name = "Laser {0}, ({1})".format(('mean', 'RMS')[rms] , args.lasertable))
      Data.saveHistogram(h, outputdir + "/laser/Laser_{0}_{1}.2D.{2}".format(("MEAN", "RMS")[rms], d, format), d)
      h = GHC.get2DHistogram(key = "APD_OVER_PN_{0}".format(('MEAN', 'RMS')[rms]), useRMS = rms, type="laser", part = d, name = "APD/PN {0}, ({1})".format(('mean', 'RMS')[rms] , args.lasertable))
      Data.saveHistogram(h, outputdir + "/laser/APDPN_{0}_{1}.2D.{2}".format(("MEAN", "RMS")[rms], d, format), d)
  
endts = datetime.datetime.now()
print "\np. Elapsed time:", str(endts - startts)
