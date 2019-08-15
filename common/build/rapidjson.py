import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "rapidjson"
#zipUrl = "http:// .tar.gz"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "rapidjson")

def getWorkingFolderPath():
  return os.path.join(getRootPath(), "rapidjson")

def build(arch, build):
  devtools.buildCmake(getWorkingFolderPath(), getRootPath(), [], arch, build, "rapidjson.sln")
  return True
