import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "FreeType"
#zipUrl = "http:// .tar.gz"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "freetype")

def getWorkingFolderPath():
  return os.path.join(getRootPath(), "freetype")

def findFreeTypeZip(rootDir):
  for root, dirs, files in os.walk(rootDir):
    for f in files:
      if "freetype" in f and ".tar.bz2" in f:
        return os.path.join(root, f)
  raise Exception("No freetype .tar.bz2 found")

def fixFileStruct(rootDir, targetDir):
  for root, dirs, files in os.walk(rootDir):
    for d in dirs:
      if "freetype-" in d:
        shutil.move(os.path.join(root, d), targetDir)
        return True
  raise Exception("Failed to find extracted " + name + "folder")

def build(arch, build):
  workingDir = getWorkingFolderPath()
  if not os.path.isdir(workingDir):
    print "Extract FreeType"
    bz2 = findFreeTypeZip(getRootPath())
    tar = bz2[:-4]
    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), bz2]
    proc = subprocess.call(unzipcmd)
    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), tar]
    proc = subprocess.call(unzipcmd)
    fixFileStruct(getRootPath(), getWorkingFolderPath())

  devtools.buildCmake(os.path.join(workingDir), getRootPath(), [], arch, build, "freetype.sln")

  return True
