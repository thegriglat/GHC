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
  
# pedestallimits in the following format 
#
# mean < dead_limit_mean OR rms <= dead_limit_rms                     ~> DP**
# mean > dead_limit_mean and bad_limit_rms_1 <= rms < bad_limit_rms_2 ~> LR**
# mean > dead_limit_mean and rms > bad_limit_rms_2                    ~> VLR**
# mean > dead_limit_mean ad 170 <= mean <= 230                        ~> BP**
#
# limits = {
#   "G1"  : (
#     [ dead_limit_mean, dead_limit_rms  ],
#     [ bad_limit_rms_1, bad_limit_rms_2 ]
#   ) ,
#   "G6"  : ...,
#   "G12" : ...
# }

