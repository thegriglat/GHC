# GHC
Good Health Check for ECAL (testing)

It is an effort of reimplementation of Good Healt Check system for CERN CMS ECAL detector.

# How to use
to run data analysis use filename of pipe.
For example:
  cat data/MON_LASER_BLUE.dat | ./laser_blue.py
or
  ./laser_blue.py data/MON_LASER_BLUE.dat

./pedestal.py -h

Free feel to change python scripts for your needs.

# Documentation
execute
  pydoc modules/*
  

