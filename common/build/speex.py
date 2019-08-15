import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "speex"
#zipUrl = "http:// .tar.gz"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "speex")

def build(arch, build):
  devtools.buildCmake(getRootPath(), getRootPath(), [], arch, build, "speex.sln")
  return True
