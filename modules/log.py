#!/usr/bin/env python

import os

def debug(str):
  if os.environ.get('DEBUG') != None and os.environ.get('DEBUG') != 0:
    print "DEBUG: ", str
