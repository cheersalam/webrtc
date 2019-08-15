import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "curl"
#zipUrl = "http:// .tar.gz"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "curl")

def getWorkingFolderPath():
  return os.path.join(getRootPath(), "curl")

def build(arch, build):
  workingDir = getWorkingFolderPath()
  params = ["-DBUILD_TESTING=OFF", "-DBUILD_CURL_EXE=OFF","-DCMAKE_USE_OPENSSL=ON", "-DBUILD_CURL_TESTS=OFF", "-DCMAKE_USE_LIBSSH2=OFF", "-DCURL_WINDOWS_SSPI=OFF", "-DCURL_STATICLIB=ON", "-DHTTP_ONLY=ON"]
  if "dar" in arch:
#    params.append("-DENABLE_ARES=ON")
    params.append("-DENABLE_THREADED_RESOLVER=ON")
  devtools.buildCmake(os.path.join(workingDir), getRootPath(), params, arch, build, "curl.sln")
  return True
