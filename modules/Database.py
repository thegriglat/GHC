#!/usr/bin/env python

import cx_Oracle

class DB(object):
  def __init__(self, connstring):
    self.conn = cx_Oracle.connect(connstring)
    self.connstring = connstring

  def getConnParameters(self):
    print "Connection string is '{0}'".format(self.connstring)

  def getVersion(self):
    print self.conn.version

  def execute(self, sql):
    cur = self.conn.cursor()
    try:
      cur.execute(sql)
    except:
      cur = None
    return cur

  def close(self):
    self.conn.close()
