#!/usr/bin/env python

import os
import sys
import shutil
import argparse

sys.path.append("modules")
from Laser import *

if not os.path.exists("RESULTS"):
  os.mkdir("RESULTS")

parser = argparse.ArgumentParser()
parser.add_argument('runs', metavar="RUN", nargs="+", help = "Run(s) to analyse. Use '-' for reading from stdin")
parser.add_argument('-c', '--dbstr', help="Connection string to DB (oracle://user/pass@db)", dest='dbstr')
parser.add_argument('-t', '--table', help="Table name of Laser data in DB (e.g. MON_LASER_IRED_DAT)", dest='table')
args = parser.parse_args()

if args.runs == ['-']:
    source = sys.stdin
else:
    runs = args.runs
    if args.dbstr is None:
      print "Please specify --dbstr!"
      sys.exit(0)
    source = args.dbstr

print "=== LASER BLUE ==="
DataEB = LaserData()
DataEE = LaserData()
DataEB.readAllChannels("data/EB_all_ch.txt")
DataEE.readAllChannels("data/EE_all_ch.txt")

DataEB.readLaser(source, runnum = runs)
DataEE.readLaser(source, runnum = runs)

if args.table:
  DataEB.setOption("LaserDBtable", args.table)
  DataEE.setOption("LaserDBtable", args.table)

for D in (DataEB, DataEE):
  print "    === LASER {0} ANALYSIS ===".format(("EE","EB")[D == DataEB])
  print "Number of inactive channels : {0}".format(len(D.findInactiveChannels()))

  print "List of available keys: ", D.getDataKeys()

  print "Getting info per error key :"
  for i in D.LASER_FLAGS:
    print "{0:15s} : {1:5d}".format(i, len(D.getChannelsByFlag(i)))

  if not os.path.exists("RESULTS/laser_blue"):
    os.mkdir("RESULTS/laser_blue")
  for i in D.getDataKeys():
    for j in (True, False):
      if i == "Laser":
        dimx =  ((0, 6000), (0, 200))[j]
      else:
        dimx =  ((0, 5), (0, 0.1))[j]
      h = D.get1DHistogram(i, dimx, j)
      Data.saveHistogram(h, "RESULTS/laser_blue/{0}{1}_{2}.1D.pdf".format(i.replace("/", "."), ("", "_RMS")[j], ("EE","EB")[D == DataEB]))
      del h
      h = D.get2DHistogram(i, j, plottype="endcap")
      Data.saveHistogram(h, "RESULTS/laser_blue/{0}{1}_{2}.2D.pdf".format(i.replace("/","."), ("", "_RMS")[j], ("EE","EB")[D == DataEB]), plottype = "endcap")
  
  print "=== END LASER BLUE {0} ===".format(("EE","EB")[D == DataEB])

