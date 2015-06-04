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
  * dbschema.sql
  * setup.sh
  * utils/check_db.sh
  * utils/export_from_db.sh

Modules
-------

To get more info about inner structure of modules run `PYTHONPATH=modules pydoc modules/*.py`

### Data.py  

The *Data.py* module provides basic data structure and functions for all scripts.

### log.py ###

This modules print INFO or DEBUG messages and raise RuntimeError if it is needed.

Scripts
-------

Each script has command line option parser, so -h option will give you some useful information.

### ghc.py ###

This is main script which uses Data module and provide userful output.

<pre>
usage: ghc.py [-h] [-c DBSTR] [-pon PON_RUNS] [-poff POFF_RUNS] [-tp TP_RUNS]
              [-l L_RUNS] [-lt TABLE] [-o DIRECTORY] [-i DB] [-d DB] [-ds SQL]
              [-f FORMAT] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -c DBSTR, --dbstr DBSTR
                        Connection string to DB (oracle://user/pass@db). Don't
                        use this if you want to read files.
  -pon PON_RUNS         Pedestal HV ON runs numbers or list of files
  -poff POFF_RUNS       Pedestal HV OFF runs numbers or list of files
  -tp TP_RUNS           Test Pulse runs numbers or list of files
  -l L_RUNS             Laser runs or list of files
  -lt TABLE, --lasertable TABLE
                        Laser table to use in Oracle DB
  -o DIRECTORY, --output DIRECTORY
                        Results directory
  -i DB, --import DB    Import DB from sqlite3
  -d DB, --dump DB      Dump internal database in sqlite3 database
  -ds SQL, --dumpsql SQL
                        Dump internal database in SQL
  -f FORMAT, --format FORMAT
                        Image format
  -v, --verbose         Be more verbose
</pre>
 
The following rules are used for assign some flags to channels:

How to use
==========

**for new data base**

    source setup.sh

**Example of analyse GHC28**

    python ghc.py -h
    python ghc.py -v -ds GHC.dump.sql -d GHC.sqlite3 -o results -lt MON_LASER_IRED_DAT -c 'oracle://user/pass@db' -poff "238609 238610 238600" -pon "238566 238569 238594" -tp "238577 238574 238581" -l 238724

You should see various output about channels.
