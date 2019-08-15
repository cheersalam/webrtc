import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "cef"

win32url     = "https://crash.liquidsky.tv/cef/cef_binary_3.3683.1890.g68189dc_windows32.tar.bz2"
darwinx64url = "https://crash.liquidsky.tv/cef/cef_binary_3.2924.1538.gbfdeccd_macosx64.tar.bz2"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "cef")

def fixFileStruct(rootDir):
  for root, dirs, files in os.walk(rootDir):
    for d in dirs:
      if "cef_binary_" in d:
        shutil.move(os.path.join(rootDir, d), os.path.join(rootDir, d.split("_")[-1]))
        return True
  raise Exception("Failed to find extracted cef folder")

def cefFixSDK():
  f = open(os.path.join(getRootPath(), "macosx64", "cmake", "cef_variables.cmake"), "rb")
  lines = f.readlines()
  for i,line in enumerate(lines):
    if "CEF_TARGET_SDK" in line: break
  f.close()
  lines[i] = line.replace("10.7", "10.8")
  buf = "\n".join(lines)
  f = open(os.path.join(getRootPath(), "macosx64", "cmake", "cef_variables.cmake"), "wb")
  f.write(buf)
  f.close()

def build(arch, build):
  bzname = ""
  tarname = ""
  foldername = ""
  url = ""

  if "wind" in arch:
    bzname = os.path.join(getRootPath(), "windows32.tar.bz2")
    tarname = os.path.join(getRootPath(), "windows32.tar")
    foldername = os.path.join(getRootPath(), "windows32")
    url = win32url
  elif "dar" in arch and "64" in arch:
    bzname = os.path.join(getRootPath(), "darwin64.tar.bz2")
    tarname = os.path.join(getRootPath(), "darwin64.tar")
    foldername = os.path.join(getRootPath(), "darwin64")
    url = darwinx64url
  else:
    raise "Not Implemented"

  if not os.path.isdir(foldername):
    if not os.path.isfile(tarname):
      if not os.path.isfile(bzname):
        devtools.downloadFile(url, bzname)

      unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), bzname]
      proc = subprocess.call(unzipcmd)
      devtools.failIfReturnCodeNotZero(proc)

    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), tarname]
    proc = subprocess.call(unzipcmd)
    devtools.failIfReturnCodeNotZero(proc)
    fixFileStruct(getRootPath())
  
  if "dar" in arch and "64" in arch:
    cefFixSDK()

  return True
