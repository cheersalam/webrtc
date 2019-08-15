import os
from common import devtools

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "googletest")

def build(arch, build):
  devtools.buildCmake(getRootPath(), getRootPath(), ["-DCMAKE_CXX_FLAGS=/w", "-DCMAKE_DEBUG_POSTFIX=d"], arch, build, "gtest.sln")
  return True

