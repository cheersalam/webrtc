import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "glew"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "glew")

def build(arch, build):
  glewDir = os.path.join(getRootPath(), "glew")
  devtools.buildCmake(glewDir, getRootPath(), [], arch, build, "GLEW.sln")
  return True

