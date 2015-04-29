#!/usr/bin/env python

import cx_Oracle
import log

class DB(object):
  def __init__(self, connstring):
    self.conn = cx_Oracle.connect(connstring)
    self.connstring = connstring

  def getConnParameters(self):
    log.info( "Connection string is '{0}'".format(self.connstring))

  def getVersion(self):
    log.info( self.conn.version)

  def execute(self, sql):
    cur = self.conn.cursor()
    log.debug("try to execute sql query\n  " + sql + "\n")
    try:
      log.debug
      cur.execute(sql)
      log.debug("success")
    except:
      log.debug("failed")
      cur = None
    return cur

  def close(self):
    log.debug("closing db connection")
    self.conn.close()
    log.debug("connection closed")
