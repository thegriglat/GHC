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
parser.add_argument('-c', '--dbstr', help="Connection string to DB (oracle://user/pass@db)", dest='dbstr')
parser.add_argument('-pon', help="Pedestal HV ON runs", dest='pon_runs')
parser.add_argument('-poff',help="Pedestal HV OFF runs)", dest='poff_runs')
parser.add_argument('-tp',  help="Test Pulse runs", dest='tp_runs')
parser.add_argument('-l',help="Laser runs", dest='l_runs')
parser.add_argument('-lt', '--lasertable', help="Laser table", dest='lasertable')
args = parser.parse_args()

if not args.output:
  outputdir = "RESULTS"
else:
  outputdir = args.output
if not os.path.exists(outputdir):
  os.mkdir(outputdir)

if args.dbstr is None:
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

print " === PEDESTAL ANALYSIS ==="
print "=== {0} ANALYSIS ===".format(("EE", "EB")[D == DataEB])
act = len ([ c for c in GHC.getActiveChannels() if  Data.getChannelClass(c) == "EB"])
print "Number of inactive channels : {0}".format(61200 - act)
print "Number of active channels   : {0}".format(act)

print "Statistics of channels by problem classes: "
print "{classn:45s} | {empty:5s} | {tags:12s}".format(classn = "Classes of pedestal problematic channels", empty="", tags="Short name")

print "-----------------------------------------------------------------------------------------------------------"
shorter = GHC.getChannelsByFlag
for k in ["G1", "G6", "G12"]:
  print "{0:45s} | {1:5d} | {2:12s}".format("Dead pedestal channels", len(shorter("DP" + k)), "DP" + k)
  print "{0:45s} | {1:5d} | {2:12s}".format("Pedestal mean outside [170,230]", len(shorter("BP" + k)), "BP" + k)
  print "{0:45s} | {1:5d} | {2:12s}".format("Large RMS (noisy channels)", len(shorter("LR" + k)), "LR" + k)
  print "{0:45s} | {1:5d} | {2:12s}".format("Very large RMS (very noisy channels)", len(shorter("VLR" + k)), "VLR" + k)
  print "{0:45s} | {1:5d} | {2:12s}".format("Bad pedestal and noisy channels", len(shorter(["BP" + k, "LR" + k])), "BP" + k +"+LR" + k)
  print "{0:45s} | {1:5d} | {2:12s}".format("Bad pedestal and very noisy", len(shorter(["BP" + k,"VLR" + k])), "BP" + k + "+VLR" + k)
  print "-----------------------------------------------------------------------------------------------------------"
del shorter

print ""

tpc = 0
print "Get statistics by FLAGS:"
for k in ["G1", "G6", "G12"]:
  for i in GHC.PEDESTAL_FLAGS:
    num = GHC.cur.execute("select count( distinct channel_id) from flags where flag = '{0}'".format(i + k)).fetchone()[0]
    print "  {0:8s} : {1:5d}".format(i + k, num)
print "Total problematic pedestal channels:", tpc

i = 1/0
print ""
if not os.path.exists(outputdir + "/pedestals"):
  os.mkdir(outputdir + "/pedestals")
for i in activekeys:
  for j in (True, False):
    h = D.get1DHistogram(i, None,  j)
    Data.saveHistogram(h, outputdir + "/pedestals/{0}{1}_EB.1D.pdf".format(i, ("", "_RMS")[j])) 
    del h
    plttype = ("barrel", "endcap")[D == DataEE]
    h = D.get2DHistogram(i, j, plottype = plttype)
    Data.saveHistogram(h, outputdir + "/pedestals/{0}{1}_{2}.2D.pdf".format(i, ("", "_RMS")[j],("EE","EB")[D == DataEB]), plttype) 
    del h
print "    === END PEDESTALS {0} ===".format(("EE", "EB")[D == DataEB])

if args.json:
  log.info ("Save json file " + args.json + ' ...')
  sumdict = {}
  sumdict.update(DataEB.getChannels())
  sumdict.update(DataEE.getChannels())
  Data.jsonExport(sumdict, open(args.json, 'w'))
