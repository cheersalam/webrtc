#!/usr/bin/env python
import os
import sys
import shutil
import zipfile
import xml.etree.ElementTree as etree
from slacker import Slacker


def we_are_frozen():
  return hasattr(sys, "frozen")

def module_path():
  encoding = sys.getfilesystemencoding()
  if we_are_frozen():
    return os.path.dirname(unicode(sys.executable, encoding))
  return os.path.dirname(unicode(__file__, encoding))

unsortedDir = "/home/crashs/crashs/unsorted/"
storageDir = "/home/crashs/crashs/"

def extractData(fn):
  with zipfile.ZipFile(fn) as zf:
    for zn in zf.namelist():
      if zn == "crashrpt.xml":
        with zf.open(zn) as cf:
          tree = etree.parse(cf)
          root = tree.getroot()
          appname = root.find("AppName").text
          appversion = root.find("AppVersion").text
          strOut = u"[{}][{}][{}]".format(appname, appversion, os.path.basename(fn))
          emailel = root.find("UserEmail")
          if emailel != None and emailel.text != None:
            strOut = u"{} from [{}]".format(strOut, emailel.text)
          usertextel = root.find("ProblemDescription")
          if usertextel != None and usertextel.text != None:
            strOut = u"{}, said: [{}]".format(strOut, usertextel.text)
          return strOut

def checkUnsorted():
  slackMessage = ""

  for root, dirs, files in os.walk(unsortedDir):
    for fo in files:
      if ".zip" in fo:
        print "processing " + fo
        try:
          appname = ""
          version = ""
          crFilename = "crashrpt.xml"

          fu = os.path.join(root, fo)
          with zipfile.ZipFile(fu) as zf:
            zipdata = zf.read(crFilename)
            tree = etree.fromstring(zipdata)

            appname = tree.find("AppName").text
            version = tree.find("AppVersion").text

          print "move to /" + appname + "/" + version

          appFolder = os.path.join(storageDir, appname)
          if not os.path.exists(appFolder):
            os.mkdir(appFolder)

          versionFolder = os.path.join(appFolder, version)
          if not os.path.exists(versionFolder):
            os.mkdir(versionFolder)

          slackMessage += extractData(fu).encode('ascii', 'ignore')
          slackMessage += "\n"

          shutil.move(fu, os.path.join(versionFolder, fo))

        except:
          print "failed to process " + fo
  return slackMessage

message = checkUnsorted()

print message
if len(message) > 0:
  slack = Slacker('change here')
  slack.chat.post_message('#crashs', message)