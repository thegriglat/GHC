# GHC
Good Health Check for ECAL (testing)

It is an effort of reimplementation of Good Healt Check system for CERN CMS ECAL detector.

Structure of the project:
.
|-- data
|   |-- EB_all_ch.txt
|   |-- EE_all_channels.txt
|   |-- EE_all_ch.txt
|   |-- MON_LASER_BLUE.dat
|   |-- MON_PEDESTALS.dat
|   |-- MON_PEDESTALS_DAT-60343-content.dat
|   |-- MON_PEDESTALS_HV_OFF.dat
|   |-- MON_PN_MGPA_DAT-60342-content.dat
|   |-- MON_PULSE_SHAPE_DAT-60342-content.dat
|   |-- MON_RUN_DAT-60342-content.dat
|   |-- MON_RUN_DAT-60343-content.dat
|   |-- MON_TEST_PULSE.dat
|   `-- MON_TEST_PULSE_DAT-60342-content.dat
|-- modules
|   |-- Data.py
|   |-- LaserBlue.py
|   |-- Pedestal.py
|   `-- TestPulse.py
|-- laser_blue.py
|-- pedestals_EB.py
|-- pedestals_EE.py
|-- test_pulse.py
`-- Readme.txt

6 directories, 70 files

# How to use
to run data analysis use filename of pipe.
For example:
  cat data/MON_LASER_BLUE.dat | ./laser_blue.py
or
  ./laser_blue.py data/MON_LASER_BLUE.dat

Free feel to change python scripts for your needs.

# Documentation
execute
  pydoc modules/*
  

