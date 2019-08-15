#!/usr/bin/python

import SimpleHTTPServer
import SocketServer
import logging
import cgi
import hashlib
from datetime import datetime

import os
import sys

storePath = "/home/crashs/crashs/unsorted/"

if len(sys.argv) > 2:
  PORT = int(sys.argv[2])
  I = sys.argv[1]
elif len(sys.argv) > 1:
  PORT = int(sys.argv[1])
  I = ""
else:
  PORT = 64080
  I = ""

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(self):
    logging.warning("======= GET STARTED =======")
    logging.warning(self.headers)
    self.returnCode(404, "Not found")
#    SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

  def returnCode(self, code, text):
    self.send_response(int(code), text)
    self.send_header('Content-Type', 'text/plain; charset=utf-8')
    self.end_headers()
    self.wfile.write(str(code) + " " + text)
    self.finish()

  def do_POST(self):
    form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type'], })
    timenow = datetime.now()
    timenowstr = timenow.strftime('%Y%m%d')

    if 'md5' not in form:
      self.returnCode(450, "MD5 hash is missing.")
      return

    crashHash = form['md5'].value

    if len(crashHash) != 32:
      self.returnCode(450, "MD5 hash value has wrong length.")
      return

    if 'crashguid' not in form:
      self.returnCode(450, "Crash GUID missing.")
      return

    crashGuid = form['crashguid'].value

    if len(crashGuid) != 36:
      self.returnCode(450, "Crash GUID has wrong length.")
      return

    crashData = form['crashrpt'].value

    m = hashlib.md5()
    m.update(crashData)

    if m.hexdigest() != crashHash:
      self.returnCode(450, "Crash have wrong md5.")
      return

    filename = timenowstr + "-" + crashGuid + ".zip"
    filepath = os.path.join(storePath, filename)
    with open (filepath, "a+") as logFile:
       logFile.write(crashData)

    self.returnCode(200, "OK")

Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)
httpd.serve_forever()
