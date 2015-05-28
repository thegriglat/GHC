Good Health Check
=================

This documentation is prepared for Good Health Check (GHC) utilities. It can be used for
solving problems with channels in CMS ECAL detector.

Good Health Check structure
---------------------------
GHC is written in Python and has modular structure. The **modules** directory has Python GHC modules that is used by Python GHC scripts. At the moment the following modules are available:

  * Data.py
  * log.py

These modules are used by GHC python scripts which do analysis and make plots. The following scripts are available:

  * ghc.py
  * compare.py

Also there are some additional files that helps to use GHC:

  * tnsnames.ora
  * setup.sh
  * utils/check_db.sh
  * utils/export_from_db.sh

Modules
-------

To get more info about inner structure of modules run `PYTHONPATH=modules pydoc modules/*.py`

### Data.py  

The *Data.py* module provides basic data structure and functions for all scripts.

### log.py ###

This modules only print INFO or DEBUG messages.

Scripts
-------

Each script has command line option parser, so -h option will give you some useful information.

### ghc.py ###

This is main script which uses Data module and provide userful output 
The following rules are used for assign some flags to channels:

<pre>
  Channel is assigned by the following rules: 

  mean < dead_limit_mean OR rms <= dead_limit_rms                     ~> DP**
  mean > dead_limit_mean and bad_limit_rms_1 <= rms < bad_limit_rms_2 ~> LR**
  mean > dead_limit_mean and rms > bad_limit_rms_2                    ~> VLR**
  mean > dead_limit_mean ad 170 <= mean <= 230                        ~> BP**

  limits = {
    "G1"  : (
      [ dead_limit_mean, dead_limit_rms  ],
      [ bad_limit_rms_1, bad_limit_rms_2 ]
    ) ,
    "G6"  : ...,
    "G12" : ...
  }
</pre>


How to use
==========

**for new data base**

    source setup.sh

**for pedestal analysis of runs 238566 238569 238594 (GHC28)**

    python ghc.py -h
    python ghc.py -ds GHC.dump.sql -o results2 -lt MON_LASER_IRED_DAT -c 'oracle://user/pass@db' -poff "238566 238569 238594" -pon "238566 238569 238594" -tp "238577 238574 238581" -l 238724

You should see various output about channels.
