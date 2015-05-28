#!/usr/bin/env python

import os

def debug(str):
  """
    Prints debug message
  """
  if os.environ.get('DEBUG') != None and os.environ.get('DEBUG') != 0:
    print "DEBUG: ", str

def info(str):
  """
    Prints info message
  """
  print "INFO: ", str

def error(str):
  """
    Raise RuntimeError with str
  """
  raise RuntimeError(str)
