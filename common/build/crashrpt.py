import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "crashrpt"
#zipUrl = "http:// .tar.gz"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "crashrpt")

def getWorkingFolderPath():
  return os.path.join(getRootPath(), "crashrpt")

def build(arch, build):
  if "wind" not in arch.lower():
    print name + " is windows only"
    return
  workingDir = getWorkingFolderPath()
  devtools.buildCmake(getWorkingFolderPath(), getRootPath(), [], arch, build, "crashrpt.sln")
  return True
