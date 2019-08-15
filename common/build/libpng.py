import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "LibPNG zLib"
#zipUrl = "http:// .tar.gz"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "libpng")

def getWorkingFolderPath():
  return os.path.join(getRootPath(), "libpng")

def findLibpngZip(rootDir):
  for root, dirs, files in os.walk(rootDir):
    for f in files:
      if "libpng" in f and ".tar.gz" in f:
        return os.path.join(root, f)
  raise Exception("No libpng .tar.gz found")

def findZlibZip(rootDir):
  for root, dirs, files in os.walk(rootDir):
    for f in files:
      if "zlib" in f and ".tar.gz" in f:
        return os.path.join(root, f)
  raise Exception("No zlib .tar.gz found")

def fixFileStruct(rootDir, targetDir):
  for root, dirs, files in os.walk(rootDir):
    for d in dirs:
      if "libpng-" in d:
        shutil.move(os.path.join(root, d), targetDir)
        return True
  raise Exception("Failed to find extracted " + name + "folder")

def build(arch, build):
  workingDir = getWorkingFolderPath()
  if not os.path.isdir(workingDir):
    print "Extract Libpng"
    gz = findLibpngZip(getRootPath())
    tar = gz[:-3]
    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), gz]
    proc = subprocess.call(unzipcmd)
    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), tar]
    proc = subprocess.call(unzipcmd)
    fixFileStruct(getRootPath(), getWorkingFolderPath())

    print "Extract zlib"
    gz = findZlibZip(getRootPath())
    tar = gz[:-3]
    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), gz]
    proc = subprocess.call(unzipcmd)
    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), tar]
    proc = subprocess.call(unzipcmd)

  devtools.buildCmake(os.path.join(getRootPath(), "zlib-1.2.8"), getRootPath(), [], arch, build, "zlib.sln")
  devtools.buildCmake(os.path.join(getRootPath(), "libpng"), getRootPath(), ["-DPNG_SHARED=OFF"], arch, build, "libpng.sln")
  return True
