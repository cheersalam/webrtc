import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "glfw"
#zipUrl = "http:// .tar.gz"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "glfw")

def getWorkingFolderPath():
  return os.path.join(getRootPath(), "glfw")

def findZip(rootDir):
  for root, dirs, files in os.walk(rootDir):
    for f in files:
      if "glfw" in f and ".zip" in f:
        return os.path.join(root, f)
  raise Exception("No glfw .zip found")

def fixFileStruct(rootDir, targetDir):
  for root, dirs, files in os.walk(rootDir):
    for d in dirs:
      if "glfw-" in d:
        shutil.move(os.path.join(root, d), targetDir)
        return True
  raise Exception("Failed to find extracted " + name + "folder")

def build(arch, build):
  workingDir = getWorkingFolderPath()
  if not os.path.isdir(workingDir):
    print "Extract glfw"
    zp = findZip(getRootPath())
    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), zp]
    proc = subprocess.call(unzipcmd)
    fixFileStruct(getRootPath(), getWorkingFolderPath())

  devtools.buildCmake(os.path.join(workingDir), getRootPath(), ["-DUSE_MSVC_RUNTIME_LIBRARY_DLL=OFF", "-DGLFW_USE_RETINA=OFF"], arch, build, "GLFW.sln")
  return True
