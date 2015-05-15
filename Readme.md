Good Health Check
=================

This documentation is prepared for Good Health Check (GHC) utilities. It can be used for
solving problems with channels in CMS ECAL detector.

Good Health Check structure
---------------------------
GHC is written in Python and has modular structure. The **modules** directory has Python GHC modules that is used by Python GHC scripts. At the moment the following modules are available:

  * Data.py
  * Pedestal.py
  * TestPulse.py
  * Laser.py
  * Database.py
  * log.py

These modules are used by GHC python scripts which do analysis and make plots. The following scripts are available:

  * pedestals.py
  * test_pulse.py
  * laser.py
  * compare.py

Also there are some additional files that helps to use GHC:

  * tnsnames.ora
  * setup.sh
  * utils/check_db.sh
  * utils/export_from_db.sh

Modules
-------

To get more info about inner structure of modules run `pydoc modules/*`

### Data.py  

The *Data.py* module provides basic data structure and functions for all scripts. Other modules such as *Pedestal.py*, *TestPulse.py* and *Laser.py* import *Data.py* module and override some functions that are specific to pedestal/test pulse/laser runs (for example, import from data base). Also it renders TH1F and TH2F ROOT histograms to files.

### Pedestal.py, TestPulse.py, Laser.py ###

These modules uses *Data.py* modules and override some run-specific function such as importing from database, procedure for comparing data values and marks channels.

### Database.py ###

This module provide simple access to Oracle DB and give simple function to fetch data from the one.

### log.py ###

This modules only print INFO or DEBUG messages.

Scripts
-------

Each script has command line option parser, so -h option will give you some useful information. Most of scripts can export data in JSON format (`-j` or `-jo` options).

    -o OUTPUT, --output OUTPUT is directory for output plots
    -c DBSTR, --dbstr DBSTR is string used for connection for Oracle DB. It likes *oracle://user/pass@db*
    -j JSON, --json JSON is file name of output JSON file

### pedestals.py ###

There are two arguments which sense for pedestals comparison (*not stable yet*): `-bl` (barrel limits) and `-el` (endcap limits)
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

    ./pedestals.py -j testp.json -c 'oracle://cms_ecal_r/3c4l_r34d3r@int2r_lb' -o results 238566 238569 238594

You should see the following output:

<pre>
=== PEDESTALS ===
INFO:  Getting list of all channels ...
INFO:  Done. Processed 61200 records.
INFO:  Getting list of all channels ...
INFO:  Done. Processed 14648 records.
=== EB ANALYSIS ===
Number of inactive channels : 354
Number of active channels   : 60846
Data are available for the gain G1
Data are available for the gain G12
Data are available for the gain G6
Statistics of channels by problem classes: 
Classes of pedestal problematic channels      |       | Short name  
-----------------------------------------------------------------------------------------------------------
Dead pedestal channels                        |    44 | DPG1        
Pedestal mean outside [170,230]               |     9 | BPG1        
Large RMS (noisy channels)                    |     4 | LRG1        
Very large RMS (very noisy channels)          |     3 | VLRG1       
Bad pedestal and noisy channels               |     0 | BPG1+LRG1   
Bad pedestal and very noisy                   |     0 | BPG1+VLRG1  
-----------------------------------------------------------------------------------------------------------
Dead pedestal channels                        |    57 | DPG12       
Pedestal mean outside [170,230]               |    11 | BPG12       
Large RMS (noisy channels)                    | 60764 | LRG12       
Very large RMS (very noisy channels)          |     9 | VLRG12      
Bad pedestal and noisy channels               |     3 | BPG12+LRG12 
Bad pedestal and very noisy                   |     2 | BPG12+VLRG12
-----------------------------------------------------------------------------------------------------------
Dead pedestal channels                        |    51 | DPG6        
Pedestal mean outside [170,230]               |    13 | BPG6        
Large RMS (noisy channels)                    |    31 | LRG6        
Very large RMS (very noisy channels)          |     8 | VLRG6       
Bad pedestal and noisy channels               |     0 | BPG6+LRG6   
Bad pedestal and very noisy                   |     1 | BPG6+VLRG6  
-----------------------------------------------------------------------------------------------------------

Get statistics by FLAGS:
  DPG1     :    44
  BPG1     :     9
  LRG1     :     4
  VLRG1    :     3
  DPG12    :    57
  BPG12    :    11
  LRG12    : 60764
  VLRG12   :     9
  DPG6     :    51
  BPG6     :    13
  LRG6     :    31
  VLRG6    :     8
Total problematic pedestal channels: 61004

Info in <TCanvas::Print>: pdf file results/pedestals/G1_RMS_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G1_RMS_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G1_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G1_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G12_RMS_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G12_RMS_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G12_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G12_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G6_RMS_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G6_RMS_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G6_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G6_EB.2D.pdf has been created
=== END PEDESTALS EB ===
=== EE ANALYSIS ===
Number of inactive channels : 100
Number of active channels   : 14548
Data are available for the gain G1
Data are available for the gain G12
Data are available for the gain G6
Statistics of channels by problem classes: 
Classes of pedestal problematic channels      |       | Short name  
-----------------------------------------------------------------------------------------------------------
Dead pedestal channels                        |     1 | DPG1        
Pedestal mean outside [170,230]               |     2 | BPG1        
Large RMS (noisy channels)                    |     0 | LRG1        
Very large RMS (very noisy channels)          |     0 | VLRG1       
Bad pedestal and noisy channels               |     0 | BPG1+LRG1   
Bad pedestal and very noisy                   |     0 | BPG1+VLRG1  
-----------------------------------------------------------------------------------------------------------
Dead pedestal channels                        |     2 | DPG12       
Pedestal mean outside [170,230]               |     3 | BPG12       
Large RMS (noisy channels)                    |    17 | LRG12       
Very large RMS (very noisy channels)          |     2 | VLRG12      
Bad pedestal and noisy channels               |     0 | BPG12+LRG12 
Bad pedestal and very noisy                   |     0 | BPG12+VLRG12
-----------------------------------------------------------------------------------------------------------
Dead pedestal channels                        |     3 | DPG6        
Pedestal mean outside [170,230]               |     2 | BPG6        
Large RMS (noisy channels)                    |    12 | LRG6        
Very large RMS (very noisy channels)          |     0 | VLRG6       
Bad pedestal and noisy channels               |     0 | BPG6+LRG6   
Bad pedestal and very noisy                   |     0 | BPG6+VLRG6  
-----------------------------------------------------------------------------------------------------------

Get statistics by FLAGS:
  DPG1     :     1
  BPG1     :     2
  LRG1     :     0
  VLRG1    :     0
  DPG12    :     2
  BPG12    :     3
  LRG12    :    17
  VLRG12   :     2
  DPG6     :     3
  BPG6     :     2
  LRG6     :    12
  VLRG6    :     0
Total problematic pedestal channels: 44

Info in <TCanvas::Print>: pdf file results/pedestals/G1_RMS_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G1_RMS_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G1_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G1_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G12_RMS_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G12_RMS_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G12_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G12_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G6_RMS_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G6_RMS_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G6_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/pedestals/G6_EE.2D.pdf has been created
    === END PEDESTALS EE ===
INFO:  Save json file testp.json ...
</pre>

**for Test Pulse runs 238577 238574 238581 (GHC28)**

    ./test_pulse.py -j testt.json -c 'oracle://cms_ecal_r/3c4l_r34d3r@int2r_lb' -o results 238577 238574 238581

<pre>
=== TEST PULSE ===
INFO:  Getting list of all channels ...
INFO:  Done. Processed 61200 records.
INFO:  Getting list of all channels ...
INFO:  Done. Processed 14648 records.
=== TEST PULSE EB ANALYSIS ===
Number of inactive channels : 354
Number of active channels   : 60846
Data are available for the gain G1
Data are available for the gain G12
Data are available for the gain G6
Statistics of channels by problem classes: 
Classes of Test Pulse problematic channels    |       | Short name  
-----------------------------------------------------------------------------------------------------------
Dead TP channels                              |    44 | DTPG1       
Low TP amplitude                              |    54 | STPG1       
Large TP amplitude                            |     6 | LTPG1       
-----------------------------------------------------------------------------------------------------------
Dead TP channels                              |    49 | DTPG12      
Low TP amplitude                              |    65 | STPG12      
Large TP amplitude                            |     2 | LTPG12      
-----------------------------------------------------------------------------------------------------------
Dead TP channels                              |    74 | DTPG6       
Low TP amplitude                              |    85 | STPG6       
Large TP amplitude                            |     3 | LTPG6       
-----------------------------------------------------------------------------------------------------------
Get statistics by FLAGS:
  DTPG1    :    44
  STPG1    :    54
  LTPG1    :     6
  DTPG12   :    49
  STPG12   :    65
  LTPG12   :     2
  DTPG6    :    74
  STPG6    :    85
  LTPG6    :     3
Total problematic test pulse channels: 382
Info in <TCanvas::Print>: pdf file results/test_pulse/G1_RMS_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G1_RMS_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G1_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G1_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G12_RMS_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G12_RMS_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G12_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G12_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G6_RMS_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G6_RMS_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G6_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G6_EB.2D.pdf has been created
=== END TEST PULSE EB ===
=== TEST PULSE EE ANALYSIS ===
Number of inactive channels : 100
Number of active channels   : 14548
Data are available for the gain G1
Data are available for the gain G12
Data are available for the gain G6
Statistics of channels by problem classes: 
Classes of Test Pulse problematic channels    |       | Short name  
-----------------------------------------------------------------------------------------------------------
Dead TP channels                              |     1 | DTPG1       
Low TP amplitude                              |     1 | STPG1       
Large TP amplitude                            |     2 | LTPG1       
-----------------------------------------------------------------------------------------------------------
Dead TP channels                              |     1 | DTPG12      
Low TP amplitude                              |     1 | STPG12      
Large TP amplitude                            |     0 | LTPG12      
-----------------------------------------------------------------------------------------------------------
Dead TP channels                              |     3 | DTPG6       
Low TP amplitude                              |     3 | STPG6       
Large TP amplitude                            |     0 | LTPG6       
-----------------------------------------------------------------------------------------------------------
Get statistics by FLAGS:
  DTPG1    :     1
  STPG1    :     1
  LTPG1    :     2
  DTPG12   :     1
  STPG12   :     1
  LTPG12   :     0
  DTPG6    :     3
  STPG6    :     3
  LTPG6    :     0
Total problematic test pulse channels: 12
Info in <TCanvas::Print>: pdf file results/test_pulse/G1_RMS_EE.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G1_RMS_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G1_EE.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G1_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G12_RMS_EE.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G12_RMS_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G12_EE.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G12_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G6_RMS_EE.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G6_RMS_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G6_EE.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/test_pulse/G6_EE.2D.pdf has been created
=== END TEST PULSE EE ===
INFO:  Saving json file testt.json ...
</pre>

**for laser run 238724**

    ./laser.py -t MON_LASER_IRED_DAT -c 'oracle://cms_ecal_r/3c4l_r34d3r@int2r_lb' -o results 238724

<pre>
=== LASER ===
INFO:  Getting list of all channels ...
INFO:  Done. Processed 61200 records.
INFO:  Getting list of all channels ...
INFO:  Done. Processed 14648 records.
    === LASER EB ANALYSIS ===
Number of inactive channels : 654
List of available keys:  ['APD/PN', 'Laser']
Getting info per error key :
DLAMPL          :    51
SLAMPL          :    42
LLERRO          :   909
Info in <TCanvas::Print>: pdf file results/laser/APD.PN_RMS_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/APD.PN_RMS_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/APD.PN_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/APD.PN_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/Laser_RMS_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/Laser_RMS_EB.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/Laser_EB.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/Laser_EB.2D.pdf has been created
=== END LASER EB ===
=== LASER EE ANALYSIS ===
Number of inactive channels : 100
List of available keys:  ['APD/PN', 'Laser']
Getting info per error key :
DLAMPL          :     2
SLAMPL          :    46
LLERRO          :    25
Info in <TCanvas::Print>: pdf file results/laser/APD.PN_RMS_EE.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/APD.PN_RMS_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/APD.PN_EE.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/APD.PN_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/Laser_RMS_EE.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/Laser_RMS_EE.2D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/Laser_EE.1D.pdf has been created
Info in <TCanvas::Print>: pdf file results/laser/Laser_EE.2D.pdf has been created
=== END LASER EE ===
</pre>

**use summary.py to get summary table**

    ./compare.py -s *.json

<pre>
INFO:  Reading file testl.json ...
INFO:  Finished testl.json.
INFO:  Reading file testp.json ...
INFO:  Finished testp.json.
INFO:  Reading file testt.json ...
INFO:  Finished testt.json.
INFO:  Trasform data structure ...
INFO:  Finished.
=== Summary Total Problematic Channels ===
  Total problematic channels                  : 60918
  Pedestals problems only                     : 83
  Test Pulse problems only                    : 102
  Laser problems only                         : 1017
  Pedestals + Test Pulse problems only        : 111
  Pedestals + Laser problems only             : 1037
  Test Pulse + Laser problems only            : 1053
  Pedestals + Test Pulse + Laser problems only: 111
</pre>

**we also can merge some .json files into the one which will represent entire GHC run**

    ./compare.py -jo ped_tp_las.json *.json

<pre>
INFO:  Reading file testl.json ...
INFO:  Finished testl.json.
INFO:  Reading file testp.json ...
INFO:  Finished testp.json.
INFO:  Reading file testt.json ...
INFO:  Finished testt.json.
INFO:  Trasform data structure ...
INFO:  Finished.
INFO:  Writing merged data to file ped_tp_las.json ...
INFO:  Finished.
</pre>

Then (I hope, !not tested!) it is possible to compare two GHC runs by `./compare.py -G GHC27.json GHC28.json`

    ./compare.py -G ped_tp_las.json ped_tp_las.json

<pre>
INFO:  Reading file ped_tp_las.json ...
INFO:  Finished ped_tp_las.json.
INFO:  Reading file ped_tp_las.json ...
INFO:  Finished ped_tp_las.json.
=== Compare GHC runs ===
  ped_tp_las.json ===
  Active channels                         :
  Masked channels                         : 93
  Total Problematic channels              : 60918
  Channels with design performance in G12 : 14986
  Noisy (2 <= rms <= 6 ADC counts) in G12   : 60781
  Very noisy (rms > 6 ADC counts) in G12  : 11
  => Please select name of pedestal tag:
  => Possible values are: testp.json testt.json testl.json
  : testp.json
  Pedestal rms ADC counts in G12          : 2.67719657431
  Pedestal rms ADC counts in G6           : 1.79015845835
  Pedestal rms ADC counts in G1           : 0.598705061519
  APD with bad or no connection to HV     : 88
  Dead channels due to LVR board problems : 53
  ped_tp_las.json ===
  Active channels                         :
  Masked channels                         : 93
  Total Problematic channels              : 60918
  Channels with design performance in G12 : 14986
  Noisy (2 <= rms <= 6 ADC counts) in G12   : 60781
  Very noisy (rms > 6 ADC counts) in G12  : 11
  => Please select name of pedestal tag:
  => Possible values are: testp.json testt.json testl.json
  : testp.json
  Pedestal rms ADC counts in G12          : 2.67719657431
  Pedestal rms ADC counts in G6           : 1.79015845835
  Pedestal rms ADC counts in G1           : 0.598705061519
  APD with bad or no connection to HV     : 88
  Dead channels due to LVR board problems : 53
</pre>
