import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "u2ec"
#zipUrl = "http:// .tar.gz"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "u2ec")

def getWorkingFolderPath():
  return os.path.join(getRootPath())

def build(arch, build):

  devtools.buildCmake(getWorkingFolderPath(), getRootPath(), [], arch, build, "u2ec.sln")
  return True
