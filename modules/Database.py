#!/usr/bin/env python

import log

class OracleDB(object):
  def __init__(self, connstring):
    import cx_Oracle
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

class SqliteDB(object):
  def __init__(self, database):
    import sqlite3
    self.dbh = sqlite3.connect(database)
    self.database = database
  def execute(self, sql):
    try:
      cur = self.dbh.execute(sql)
      return cur
    except Exception as e:
      log.error("Cannot execute SQL query '" + sql + "'. Error: " + str(e))
  def close(self):
    self.dbh.close()
