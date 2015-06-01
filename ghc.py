#!/usr/bin/env python

import os
import sys
import shutil
import argparse

sys.path.append("modules")
import log
import Data

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--dbstr', help="Connection string to DB (oracle://user/pass@db)", dest='dbstr')
parser.add_argument('-pon', help="Pedestal HV ON  runs", dest='pon_runs')
parser.add_argument('-poff',help="Pedestal HV OFF runs", dest='poff_runs')
parser.add_argument('-tp',  help="Test Pulse runs", dest='tp_runs')
parser.add_argument('-l',help="Laser runs", dest='l_runs')
parser.add_argument('-lt', '--lasertable', help="Laser table to use in Oracle DB", dest='lasertable', default = "MON_LASER_BLUE_DAT")
parser.add_argument('-o', '--output', help="Results directory", dest='output')
parser.add_argument('-d', '--dump', help="Dump internal database in sqlite3 database", dest='dump')
parser.add_argument('-ds', '--dumpsql', help="Dump internal database in SQL", dest='dumpsql')
args = parser.parse_args()

if not args.output:
  outputdir = "RESULTS"
else:
  outputdir = args.output
if not os.path.exists(outputdir):
  os.mkdir(outputdir)

if not args.dbstr:
  print "Please specify --dbstr!"
  sys.exit(0)
source = args.dbstr

header = lambda x: "="*((78 - (len(x)/2*2))/2) + " " + x + " " + "="*((78 - len(x))/2)

GHC = Data.Data()
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

GHC.classifyChannels()

if args.dump != None:
  if os.path.exists(args.dump):
    os.remove(args.dump)
  GHC.Export(args.dump)
if args.dumpsql != None:
  if os.path.exists(args.dumpsql):
    os.remove(args.dumpsql)
  Data.DumpSQL(GHC.dbh, args.dumpsql)

print "="*80
print header("PEDESTAL ANALYSIS")
print "="*80
print ""

for d in ["EB", "EE"]:
  print header("PEDESTAL {0} ANALYSIS".format(d))
  print ""
  act = len ([ c for c in GHC.getActiveChannels(type=['pedestal_hvon', 'pedestal_hvoff']) if  Data.getChannelClass(c) == d])
  print "| Number of inactive channels : {0}".format((61200,14648)[d == "EE"] - act)
  print "| Number of active channels   : {0}\n".format(act)
  print "| Statistics of channels by problem classes: "
  print "| {classn:43s} | {empty:5s} | {tags:23s}|".format(classn = "Classes of pedestal problematic channels", empty="", tags="Short name")

  print "-"*80
  shorter = lambda x: len([ c for c in GHC.getChannelsByFlag(x) if Data.getChannelClass(c) == d]) 
  for k in ["G1", "G6", "G12"]:
    print "| {0:43s} | {1:5d} | {2:23s}|".format("Dead pedestal channels", shorter("DP" + k), "DP" + k)
    print "| {0:43s} | {1:5d} | {2:23s}|".format("Pedestal mean outside [170,230]", shorter("BP" + k), "BP" + k)
    print "| {0:43s} | {1:5d} | {2:23s}|".format("Large RMS (noisy channels)", shorter("LR" + k), "LR" + k)
    print "| {0:43s} | {1:5d} | {2:23s}|".format("Very large RMS (very noisy channels)", shorter("VLR" + k), "VLR" + k)
    print "| {0:43s} | {1:5d} | {2:23s}|".format("Bad pedestal and noisy channels", shorter(["BP" + k, "LR" + k]), "BP" + k +"+LR" + k)
    print "| {0:43s} | {1:5d} | {2:23s}|".format("Bad pedestal and very noisy", shorter(["BP" + k,"VLR" + k]), "BP" + k + "+VLR" + k)
    print "-"*80
  del shorter

  print ""

  tpc = 0
  print " Get statistics by FLAGS:"
  for k in ["G1", "G6", "G12"]:
    for i in GHC.PEDESTAL_FLAGS:
      num = GHC.cur.execute("select count( distinct channel_id) from flags where flag = '{0}' and channel_id like '{1}%'".format(i + k, (2,1)[d == "EB"])).fetchone()[0]
      tpc += num
      print "   {0:8s} : {1:5d}".format(i + k, num)
  print ""


print "="*80
print header("TEST PULSE ANALYSIS")
print "="*80
print ""

for d in ("EB", "EE"):
  print header("TEST PULSE {0} ANALYSIS".format(d))
  print ""
  act = len ([ c for c in GHC.getActiveChannels(type = 'testpulse') if  Data.getChannelClass(c) == d])
  print "| Number of inactive channels : {0}".format((61200,14648)[d == "EE"] - act)
  print "| Number of active channels   : {0}\n".format(act)
  print "| Statistics of channels by problem classes: "
  print "| {classn:43s} | {empty:5s} | {tags:23s}|".format(classn = "Classes of Test Pulse problematic channels", empty="", tags="Short name")

  print "-"*80
  shorter = lambda x: len([ c for c in GHC.getChannelsByFlag(x) if Data.getChannelClass(c) == d]) 
  for k in ("G1", "G6", "G12"):
    print "| {0:43s} | {1:5d} | {2:23s}|".format("Dead TP channels", shorter("DTP" + k), "DTP" + k)
    print "| {0:43s} | {1:5d} | {2:23s}|".format("Low TP amplitude", shorter("STP" + k), "STP" + k)
    print "| {0:43s} | {1:5d} | {2:23s}|".format("Large TP amplitude", shorter("LTP" + k), "LTP" + k)
    print "-"*80
  del shorter

  tpc = 0
  print " Get statistics by FLAGS:"
  for k in ("G1", "G6", "G12"):
    for i in GHC.TESTPULSE_FLAGS:
      num = GHC.cur.execute("select count( distinct channel_id) from flags where flag = '{0}' and channel_id like '{1}%'".format(i + k, (2,1)[d == "EB"])).fetchone()[0]
      tpc += num
      print "   {0:8s} : {1:5d}".format(i + k, num)
  print " Total problematic test pulse channels:", tpc


print "="*80 
print header("LASER ANALYSIS")
print "="*80
print ""

for d in ("EB", "EE"):
  print header("LASER {0} ANALYSIS".format(d))
  print ""

  act = len ([ c for c in GHC.getActiveChannels(type = 'laser') if  Data.getChannelClass(c) == d])
  print "| Number of inactive channels : {0}".format((61200,14648)[d == "EE"] - act)
  print "| Number of active channels   : {0}".format(act)

  print " Getting info per error key :"
  shorter = lambda x: len([ c for c in GHC.getChannelsByFlag(x) if Data.getChannelClass(c) == d]) 
  for i in GHC.LASER_FLAGS:
    print "   {0:15s} : {1:5d}".format(i, shorter(i))

for d in ("EB", "EE"):
  pre = "^[BD]P|^V?LR"
  tpre = "^[DSL]TP"
  lre = "^[DS]LAMPL|LLERRO"
  hvre = "^BV"
  getchnum = lambda x: GHC.dbh.execute("select count(distinct channel_id) from flags where channel_id like '{0}' and flag REGEXP {1}".format(
   ("1%", "2%")[d == "EE"], " and flag REGEXP ".join([ "'{0}'".format(i) for i in x])
   )).fetchone()[0]
  print ""
  header("Summary Total Problematic Channels for {0}".format(d))
  print "|  Total problematic channels                  |           * |", tpc
  print "|  Pedestals problems                          |          PE |", getchnum([pre])
  print "|  Test Pulse problems                         |          TP |", getchnum([tpre])
  print "|  Laser problems                              |          LA |", getchnum([lre])
  if d != "EE":
    print "|  High voltage problems                       |          HV |", getchnum([hvre])
  print "|  Pedestals + Test Pulse problems             |       PE+TP |", getchnum([pre, tpre])
  print "|  Pedestals + Laser problems                  |       PE+LA |", getchnum([pre, lre])
  if d != "EE":
    print "|  Pedestals + High voltage problems           |       PE+HV |", getchnum([pre, hvre])
  print "|  Test Pulse + Laser problems                 |       TP+LA |", getchnum([tpre, lre])
  if d != "EE":
    print "|  Test Pulse + High voltage problems          |       TP+HV |", getchnum([tpre, hvre])
    print "|  Laser + High voltage problems               |       LA+HV |", getchnum([lre, hvre])
  print "|  Pedestals + Test Pulse + Laser problems     |    PE+TP+LA |", getchnum([pre, tpre, lre])
  if d != "EE":
    print "|  Pedestals + Test Pulse + HV problems        |    PE+TP+HV |", getchnum([pre, tpre, hvre])
    print "|  Pedestals + Laser + HV problems             |    PE+LA+HV |", getchnum([pre, lre, hvre])
    print "|  Test Pulse  + Laser + HV problems           |    TP+LA+HV |", getchnum([tpre, lre, hvre])
    print "|  Pedestal + Test Pulse + Laser + HV problems | PE+TP+LA+HV |", getchnum([pre, tpre, lre, hvre])


# plotting
print header("Preparing plots ...")
for i in ['pedestals_hvon', 'pedestals_hvoff', 'testpulse', 'laser']:
  if not os.path.exists(outputdir + "/" + i):
      os.mkdir(outputdir + "/" + i)

for d in ("EB", "EE"):
  for rms in (True, False):
    for i in ("G1", "G6", "G12"):
      ### 1D plots
      h = GHC.get1DHistogram(key = "PED_{0}_".format(('MEAN', 'RMS')[rms]) + i, useRMS = rms, type="pedestal_hvon", part = d, name = "Pedestal {0}, gain {1} ({2})".format(('mean', 'RMS')[rms], i, "HV ON"))
      Data.saveHistogram(h, outputdir + "/pedestals_hvon/{0}_{1}_{2}.1D.png".format(i, ("MEAN", "RMS")[rms], d), d)

      h = GHC.get1DHistogram(key = "PED_{0}_".format(('MEAN', 'RMS')[rms]) + i, useRMS = rms, type="pedestal_hvoff", part = d ,name = "Pedestal {0}, gain {1} ({2})".format(('mean', 'RMS')[rms], i, "pedestal_hvoff"))
      Data.saveHistogram(h, outputdir + "/pedestals_hvoff/{0}_{1}_{2}.1D.png".format(i, ("MEAN", "RMS")[rms], d), d)
    
      h = GHC.get1DHistogram(key = "ADC_{0}_".format(('MEAN', 'RMS')[rms]) + i, useRMS = rms, type="testpulse", part = d, name = "Test Pulse {0}, gain {1}".format(('mean', 'RMS')[rms], i))
      Data.saveHistogram(h, outputdir + "/testpulse/{0}_{1}_{2}.1D.png".format(i, ("MEAN", "RMS")[rms], d), d)
      
      ### 2D plots
      h = GHC.get2DHistogram(key = "PED_{0}_".format(('MEAN', 'RMS')[rms]) + i, useRMS = rms, type="pedestal_hvon", part = d, name = "Pedestal {0}, gain {1} ({2})".format(('mean', 'RMS')[rms], i, "HV ON"))
      Data.saveHistogram(h, outputdir + "/pedestals_hvon/{0}_{1}_{2}.2D.png".format(i, ("MEAN", "RMS")[rms], d), d)
      h = GHC.get2DHistogram(key = "PED_{0}_".format(('MEAN', 'RMS')[rms]) + i, useRMS = rms, type="pedestal_hvoff", part = d, name = "Pedestal {0}, gain {1} ({2})".format(('mean', 'RMS')[rms], i, "pedestal_hvoff"))
      Data.saveHistogram(h, outputdir + "/pedestals_hvoff/{0}_{1}_{2}.2D.png".format(i, ("MEAN", "RMS")[rms], d), d)
      h = GHC.get2DHistogram(key = "ADC_{0}_".format(('MEAN', 'RMS')[rms]) + i, useRMS = rms, type="testpulse", part = d, name = "Test Pulse {0}, gain {1}".format(('mean', 'RMS')[rms], i))
      Data.saveHistogram(h, outputdir + "/testpulse/{0}_{1}_{2}.2D.png".format(i, ("MEAN", "RMS")[rms], d), d)

  ### laser plots
    h = GHC.get1DHistogram(key = "APD_{0}".format(('MEAN', 'RMS')[rms]), useRMS = rms, type="laser", part = d, name = "Laser {0}, ({1})".format(('mean', 'RMS')[rms] , args.lasertable))
    Data.saveHistogram(h, outputdir + "/laser/Laser_{0}_{1}.1D.png".format(("MEAN", "RMS")[rms], d), d)
    h = GHC.get1DHistogram(key = "APD_OVER_PN_{0}".format(('MEAN', 'RMS')[rms]), useRMS = rms, type="laser", part = d, name = "APD/PN {0}, ({1})".format(('mean', 'RMS')[rms], args.lasertable))
    Data.saveHistogram(h, outputdir + "/laser/APDPN_{0}_{1}.1D.png".format(("MEAN", "RMS")[rms], d), d)
    h = GHC.get2DHistogram(key = "APD_{0}".format(('MEAN', 'RMS')[rms]), useRMS = rms, type="laser", part = d, name = "Laser {0}, ({1})".format(('mean', 'RMS')[rms] , args.lasertable))
    Data.saveHistogram(h, outputdir + "/laser/Laser_{0}_{1}.2D.png".format(("MEAN", "RMS")[rms], d), d)
    h = GHC.get2DHistogram(key = "APD_OVER_PN_{0}".format(('MEAN', 'RMS')[rms]), useRMS = rms, type="laser", part = d, name = "APD/PN {0}, ({1})".format(('mean', 'RMS')[rms] , args.lasertable))
    Data.saveHistogram(h, outputdir + "/laser/APDPN_{0}_{1}.2D.png".format(("MEAN", "RMS")[rms], d), d)

