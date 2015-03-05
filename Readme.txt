# GHC
Good Health Check for ECAL (testing)

It is an effort of reimplementation of Good Healt Check system for CERN CMS ECAL detector.

Structure of the project:
.
|-- data                                        # directory with exported dat files
|   |-- EB_all_ch.txt                           # mainly used for example data
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
|-- modules                                     # directory with Python modules used for data analysis
|   |-- Data.py
|   |-- Data.pyc
|   |-- LaserBlue.py
|   |-- LaserBlue.pyc
|   |-- Pedestal.py
|   |-- Pedestal.pyc
|   |-- TestPulse.py
|   `-- TestPulse.pyc
|-- laser_blue.py                               # Python scripts which used modules and call analysis functions
|-- pedestals_EB.py
|-- pedestals_EE.py
`-- test_pulse.py

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
  

