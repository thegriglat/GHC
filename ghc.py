#!/usr/bin/env python

import os
import sys
import shutil
import argparse

sys.path.append("modules")
import log
import Data

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', help="Results directory (default: RESULTS)", dest='output')
parser.add_argument('-d', '--dbdump', help="Dump internal database", dest='dbdump')
parser.add_argument('-c', '--dbstr', help="Connection string to DB (oracle://user/pass@db)", dest='dbstr')
parser.add_argument('-pon', help="Pedestal HV ON runs", dest='pon_runs')
parser.add_argument('-poff',help="Pedestal HV OFF runs)", dest='poff_runs')
parser.add_argument('-tp',  help="Test Pulse runs", dest='tp_runs')
parser.add_argument('-l',help="Laser runs", dest='l_runs')
parser.add_argument('-lt', '--lasertable', help="Laser table", dest='lasertable', default = "MON_LASER_BLUE_DAT")

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

GHC = Data.Data()
GHC.readAllChannels("data/EB_all_ch.txt")
GHC.readAllChannels("data/EE_all_ch.txt")

#GHC.readData(source, runs=runs, type="pedestal_hvoff")

if args.pon_runs:
  GHC.readData(source, runs=args.pon_runs.split(), type="pedestal_hvon")
if args.poff_runs:
  GHC.readData(source, runs=args.poff_runs.split(), type="pedestal_hvoff")

if args.tp_runs:
  GHC.readData(source, runs=args.tp_runs.split(), type="testpulse")
if args.l_runs:
  GHC.readData(source, runs=args.l_runs.split(), type="laser", lasertable=args.lasertable)

GHC.classifyChannels()

if args.dbdump != None:
  GHC.Export(args.dbdump)

print " ========================="
print " === PEDESTAL ANALYSIS ==="
print " ========================="

for d in ["EB", "EE"]:
  print " === PEDESTAL {0} ANALYSIS ===".format(d)

  act = len ([ c for c in GHC.getActiveChannels(type=['pedestal_hvon', 'pedestal_hvoff']) if  Data.getChannelClass(c) == d])
  print "Number of inactive channels : {0}".format((61200,14648)[d == "EE"] - act)
  print "Number of active channels   : {0}".format(act)

  print "Statistics of channels by problem classes: "
  print "{classn:45s} | {empty:5s} | {tags:12s}".format(classn = "Classes of pedestal problematic channels", empty="", tags="Short name")

  print "-----------------------------------------------------------------------------------------------------------"
  shorter = lambda x: len([ c for c in GHC.getChannelsByFlag(x) if Data.getChannelClass(c) == d]) 
  for k in ["G1", "G6", "G12"]:
    print "{0:45s} | {1:5d} | {2:12s}".format("Dead pedestal channels", shorter("DP" + k), "DP" + k)
    print "{0:45s} | {1:5d} | {2:12s}".format("Pedestal mean outside [170,230]", shorter("BP" + k), "BP" + k)
    print "{0:45s} | {1:5d} | {2:12s}".format("Large RMS (noisy channels)", shorter("LR" + k), "LR" + k)
    print "{0:45s} | {1:5d} | {2:12s}".format("Very large RMS (very noisy channels)", shorter("VLR" + k), "VLR" + k)
    print "{0:45s} | {1:5d} | {2:12s}".format("Bad pedestal and noisy channels", shorter(["BP" + k, "LR" + k]), "BP" + k +"+LR" + k)
    print "{0:45s} | {1:5d} | {2:12s}".format("Bad pedestal and very noisy", shorter(["BP" + k,"VLR" + k]), "BP" + k + "+VLR" + k)
    print "-----------------------------------------------------------------------------------------------------------"
  del shorter

  print ""

  tpc = 0
  print "Get statistics by FLAGS:"
  for k in ["G1", "G6", "G12"]:
    for i in GHC.PEDESTAL_FLAGS:
      num = GHC.cur.execute("select count( distinct channel_id) from flags where flag = '{0}' and channel_id like '{1}%'".format(i + k, (2,1)[d == "EB"])).fetchone()[0]
      tpc += num
      print "  {0:8s} : {1:5d}".format(i + k, num)
  print "Total problematic pedestal channels:", tpc

  print ""


print " =========================="
print " === TESTPULSE ANALYSIS ==="
print " =========================="

for d in ("EB", "EE"):
  print "=== TEST PULSE {0} ANALYSIS ===".format(d)
  act = len ([ c for c in GHC.getActiveChannels(type = 'testpulse') if  Data.getChannelClass(c) == d])
  print "Number of inactive channels : {0}".format((61200,14648)[d == "EE"] - act)
  print "Number of active channels   : {0}".format(act)

  print "Statistics of channels by problem classes: "
  print "{classn:45s} | {empty:5s} | {tags:12s}".format(classn = "Classes of Test Pulse problematic channels", empty="", tags="Short name")

  print "-----------------------------------------------------------------------------------------------------------"
  shorter = lambda x: len([ c for c in GHC.getChannelsByFlag(x) if Data.getChannelClass(c) == d]) 
  for k in ("G1", "G2", "G12"):
    print "{0:45s} | {1:5d} | {2:12s}".format("Dead TP channels", shorter("DTP" + k), "DTP" + k)
    print "{0:45s} | {1:5d} | {2:12s}".format("Low TP amplitude", shorter("STP" + k), "STP" + k)
    print "{0:45s} | {1:5d} | {2:12s}".format("Large TP amplitude", shorter("LTP" + k), "LTP" + k)
    print "-----------------------------------------------------------------------------------------------------------"
  del shorter

  tpc = 0
  print "Get statistics by FLAGS:"
  for k in ("G1", "G6", "G12"):
    for i in GHC.TESTPULSE_FLAGS:
      num = GHC.cur.execute("select count( distinct channel_id) from flags where flag = '{0}' and channel_id like '{1}%'".format(i + k, (2,1)[d == "EB"])).fetchone()[0]
      tpc += num
      print "  {0:8s} : {1:5d}".format(i + k, num)
  print "Total problematic test pulse channels:", tpc



print " ======================"
print " === LASER ANALYSIS ==="
print " ======================"

for D in ("EB", "EE"):
  print "=== LASER {0} ANALYSIS ===".format(d)
  act = len ([ c for c in GHC.getActiveChannels(type = 'laser') if  Data.getChannelClass(c) == d])
  print "Number of inactive channels : {0}".format((61200,14648)[d == "EE"] - act)
  print "Number of active channels   : {0}".format(act)

  print "Getting info per error key :"
  shorter = lambda x: len([ c for c in GHC.getChannelsByFlag(x) if Data.getChannelClass(c) == d]) 
  for i in GHC.LASER_FLAGS:
    print "{0:15s} : {1:5d}".format(i, shorter(i))


# plotting
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

