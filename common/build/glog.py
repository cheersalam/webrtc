import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "glog"
#zipUrl = "http:// .tar.gz"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "glog")

def getWorkingFolderPath():
  return os.path.join(getRootPath(), "glog")

def build(arch, build):
  devtools.buildCmake(getWorkingFolderPath(), getRootPath(), [], arch, build, "google-glog.sln")
  return True
