#!/usr/bin/python
import SocketServer
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

import os
import sys
import cgi

import logging
import hashlib
import zlib
from datetime import datetime


storePath = "./"

class Handler(BaseHTTPRequestHandler):
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

    required = ["log", "md5", "filename", "log_id"]

    for field in required:
      if field not in form:
        self.returnCode(450, "Field " + field + " is missing.")
        return

    logData = form['log'].value
    logHash = form['md5'].value
    logId = form['log_id'].value
    logFilename = form['filename'].value

    if 'X-Real-IP' in self.headers:
      clientIp = self.headers['X-Real-IP']
    else:
      clientIp = str(self.client_address[0])

    m = hashlib.md5()
    m.update(logData)

    if len(logHash) != 32:
      self.returnCode(450, "MD5 hash value has wrong length.")
      return

    if m.hexdigest() != logHash:
      self.returnCode(450, "Log have wrong md5.")
      return

    folder = os.path.join(storePath, timenowstr)
    if not os.path.exists(folder):
      os.mkdir(folder)

    filename = clientIp
    if "unknown" in logId:
      filename += "-" + logFilename
    else:
      filename += "-" + logId

    filename += ".data"

    filepath = os.path.join(folder, filename)
    with open (filepath, "w") as logFile:
       logFile.write(logData)

    self.returnCode(200, "OK")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  """Handle requests in a separate thread."""

if __name__ == '__main__':
  server = ThreadedHTTPServer(('127.0.0.1', 65080), Handler)
  server.serve_forever()