#!/usr/bin/env python

import os
import sys
import json
import urllib
import urllib2
import subprocess
import hashlib
import logging

def we_are_frozen():
  return hasattr(sys, "frozen")

def module_path():
  encoding = sys.getfilesystemencoding()
  if we_are_frozen():
    return os.path.dirname(unicode(sys.executable, encoding))
  return os.path.dirname(unicode(__file__, encoding))

def extractVersion(ver):
  ver, com, hsh = ver.split("-")
  v1, v2, v3 = ver.split(".")
  return (((int(v1) * 1000) + int(v2)) * 1000 + int(v3)) * 1000 + int(com)

def checkVersion(ve):
  try:
    extractVersion(ve)
    return True
  except:
    return False

addAvaliableParams = {
  "streamer-linux" : ["package_as_filename_patch", "product", "package", "branch", "version", "is_deb", "preinstall", "url", "filename", "md5"],
  "player-win"     : ["package_as_filename_patch", "product", "package", "branch", "version", "url", "filename", "md5", "may_be_modified", "may_be_removed", "should_be_removed"],
  "player-mac"     : ["package_as_filename_patch", "product", "package", "branch", "version", "url", "filename", "md5", "may_be_modified", "may_be_removed", "should_be_removed", "access_mode"],
  "streamer-win"   : ["package_as_filename_patch", "product", "package", "branch", "version", "url", "filename", "md5", "may_be_modified", "may_be_removed", "should_be_removed"],
}

class UpdateApi:
  def __init__(self, url = "http://10.8.0.1:58080/updater"):
    self.url = url

  def doGet(self, url, values):
    valenc = urllib.urlencode(values)
    req = urllib2.Request(url + "?" + valenc)
    logging.debug("GET Request:" + req.get_full_url())
    resp = urllib2.urlopen(req)
    data = resp.read()
    logging.debug(data)
    j = json.loads(data)
    return j

  def doPost(self, url, values):
    valenc = urllib.urlencode(values)
    req = urllib2.Request(url + "?" + valenc, {})
    logging.debug("POST Request:" + req.get_full_url())
    resp = urllib2.urlopen(req)
    j = json.loads(resp.read())
    return j

  def add(self, params):
    required = [ "product", "package", "version", "filename", "md5" ]
    for r in required:
      if r not in params.keys():
        raise Exception("Error, no " + r + " field")

    if not checkVersion(params["version"]):
      raise Exception("Version format is bad")

    d = dict()
    pr = params["product"]
    prod = None
    for k in addAvaliableParams.keys():
      if k == pr:
        prod = k
        break

      m = hashlib.md5()
      m.update(k + "_liquidsky")
      if m.hexdigest() == pr:
        prod = k
        break
    if prod == None:
      raise Exception("unknown product")

    for p in addAvaliableParams[prod]:
      if p in params.keys():
        d[p] = params[p]

    self.doGet(self.url + "/add.json", d)

  def head(self, params):
    headAvaliableParams = ["product", "package", "branch", "version"]
    required = [ "product", "package", "branch", "version" ]
    for r in required:
      if r not in params.keys():
        raise Exception("Error, no " + r + " field")

    if not checkVersion(params["version"]):
      raise Exception("Version format is bad")

    d = dict()
    for p in headAvaliableParams:
      if p in params.keys():
        d[p] = params[p]

    self.doGet(self.url + "/head.json", d)

  def save(self):
    self.doGet(self.url + "/save.json", dict())

  def checkUpdate(self, params):
    required = [ "product", "branch", "version" ]
    for r in required:
      if r not in params.keys():
        raise Exception("Error, no " + r + " field")

    if not checkVersion(params["version"]):
      raise Exception("Version format is bad")

    d = dict()
    for p in required:
      if p in params.keys():
        d[p] = params[p]

    return self.doGet(self.url + "/check_update.json", d)



