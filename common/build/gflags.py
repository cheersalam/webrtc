import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "gflags"
#zipUrl = "http:// .tar.gz"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "gflags", "gflags")

def build(arch, build):
  devtools.buildCmake(getRootPath(), getRootPath(), ["-DGFLAGS_BUILD_SHARED_LIBS=OFF", "-DGFLAGS_BUILD_STATIC_LIBS=ON", "-DBUILD_gflags_LIB=ON", "-DBUILD_gflags_nothreads_LIB=OFF", "-DGFLAGS_INSTALL_HEADERS=ON", "-DGFLAGS_INSTALL_SHARED_LIBS=OFF", "-DGFLAGS_INSTALL_STATIC_LIBS=ON"], arch, build, "gflags.sln")
  return True
