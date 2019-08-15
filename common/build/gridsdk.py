import os
import subprocess
import shutil
from common import devtools
from common.find import sevenz

name = "NVIDIA GRID SDK"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "grid-sdk")

def getExtactedFolderPath():
  return os.path.join(getRootPath(), "sdk")

def findGridSdkZip(root):
  for root, dirs, files in os.walk(root):
    for f in files:
      if "grid-sdk" in f and ".zip" in f:
        return os.path.join(root, f)
  raise Exception("No grid sdk zip found")

def build(arch, build):
  path = None

  if "wind" in arch.lower():
    path = os.path.join(getRootPath(), "win", "NvFBC")

  if "linux" in arch.lower():
    path = os.path.join(getRootPath(), "linux", "NvFBC")

  if path == None:
    print "grid sdk is not supported on this platform"
    return

  toPath = devtools.getInstallPath(arch)
  devtools.copyWindowsFiles(path, os.path.abspath(os.path.join(toPath, "include", "NvFBC")), ".h")
  devtools.copyWindowsFiles(os.path.join(path, "..", "NvEncodeAPI"), os.path.abspath(os.path.join(toPath, "include", "NvEncodeAPI")), ".h")
  print "copied"

def clean():
  devtools.rmtree(getExtactedFolderPath())
