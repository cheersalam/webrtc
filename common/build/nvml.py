import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "nvml"
#zipUrl = "http:// .tar.gz"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "nvml")

def getWorkingFolderPath():
  return getRootPath()

def build(arch, build):
  devtools.buildCmake(getWorkingFolderPath(), getRootPath(), [], arch, build, "nvml.sln")
  return True
