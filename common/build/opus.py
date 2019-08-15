import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "opus"
zipUrl = "https://github.com/xiph/opus/archive/v1.3.1.tar.gz"
patches = ["opus.patch"]

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", name)

def getWorkingFolderPath():
  return os.path.join(getRootPath(), name)

def findZip(rootDir):
  for root, dirs, files in os.walk(rootDir):
    for f in files:
      if name in f and "tar.gz" in f:
        return os.path.join(root, f)
  raise Exception("No " + name + "*.tar.gz found")

def fixFileStruct(rootDir, targetDir):
  for root, dirs, files in os.walk(rootDir):
    for d in dirs:
      if (name + "-") in d:
        shutil.move(os.path.join(root, d), targetDir)
        return True
  raise Exception("Failed to find extracted " + name + "folder")

def getSources():
  workingDir = getWorkingFolderPath()
  if not os.path.isdir(workingDir):
    try:
      fname = findZip(getRootPath())
    except:
      url = zipUrl
      fname = os.path.join(getRootPath(), url.rsplit('/', 1)[1])
      devtools.downloadFile(url, fname)

    print "Extract: " + name
    tar = fname[:-3]
    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), fname]
    proc = subprocess.call(unzipcmd)
    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), tar]
    proc = subprocess.call(unzipcmd)
    fixFileStruct(getRootPath(), workingDir)

    print "Patching: " + name
    for patch in patches:
      print "Patching: " + patch
      patchcmd = ["python", os.path.join(devtools.rootDir, "common", "patch.py"), "-d", workingDir, os.path.join(devtools.rootDir, "common", "build", patch)]
      proc = subprocess.call(patchcmd)

def build(arch, build):
  getSources()

  devtools.buildCmake(getWorkingFolderPath(), getRootPath(), ["-DCMAKE_DEBUG_POSTFIX=d"], arch, build, "opus.sln")
  return True
