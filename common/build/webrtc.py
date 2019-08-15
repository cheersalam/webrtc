import os
import re
import pdb
import subprocess
import shutil
import multiprocessing
from common import devtools
from common.find import sevenz

name = "webrtc"

GN_CONFIG = """
target_cpu="{}"
rtc_use_h264=true
rtc_enable_protobuf=false
is_official_build={}
rtc_build_examples=false
rtc_include_tests=false
"""

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "webrtc")

def getSrcPath():
  return os.path.join(getRootPath(), "src")

def getOutPath(arch):
  return os.path.join(getSrcPath(), "out", arch)

def getArgsPath(arch):
  return os.path.join(getSrcPath(), "out", arch, "args.gn")

def mergetree(src, dst, filter, transform=None):
  transform = transform if transform != None else lambda s: s
  for dirpath, dirnames, filenames in os.walk(src, False):
    for name in filenames:
      origin = os.path.join(dirpath, name)
      if not filter(origin):
        continue
      origin = os.path.abspath(origin)
      destination = os.path.relpath(origin, src)
      destination = os.path.join(dst, destination)
      destination = transform(destination)
      try:
        os.makedirs(os.path.dirname(destination))
      except os.error:
        pass
      shutil.copy(origin, destination)

def build(arch, build):
  archl = arch.lower()
  target_arch = "32" if "32" in archl else "64"
  target_cpu = "x86" if target_arch == "32" else "x64"
  installPath = devtools.getInstallPath(arch)
  #if not os.path.exists(getSrcPath()):
   # subprocess.check_call("fetch --nohooks webrtc", cwd=getRootPath(), shell=True)
   # subprocess.check_call("git checkout -b release refs/remotes/branch-heads/68", cwd=getSrcPath(), shell=True)

  subprocess.check_call("gclient sync", shell=True)
  subprocess.call("git apply --ignore-whitespace ../probeoverflowfix.patch", cwd=getSrcPath(), shell=True)
  subprocess.call("git apply --ignore-whitespace ../disableframedropping.patch", cwd=getSrcPath(), shell=True)
  subprocess.call("git apply --ignore-whitespace ../disableaudioprocessing.patch", cwd=getSrcPath(), shell=True)
  subprocess.call("git apply --ignore-whitespace ../exposejitter.patch", cwd=getSrcPath(), shell=True)
  subprocess.call("git apply --ignore-whitespace ../disablepacing.patch", cwd=getSrcPath(), shell=True)
  subprocess.call("git apply --ignore-whitespace ../fasterprobing.patch", cwd=getSrcPath(), shell=True)

  try:
    os.makedirs(os.path.dirname(getArgsPath(target_arch)))
  except os.error:
    pass

  try:
    os.makedirs(os.path.dirname(getArgsPath(target_arch + "d")))
  except os.error:
    pass

  with open(getArgsPath(target_arch), "w") as argsFile:
    argsFile.write(GN_CONFIG.format(target_cpu, "true"))

  with open(getArgsPath(target_arch + "d"), "w") as argsFile:
    argsFile.write(GN_CONFIG.format(target_cpu, "false"))
  
  subprocess.check_call("gn gen out/" + target_arch, cwd=getSrcPath(), shell=True)
  subprocess.check_call("ninja -C out/" + target_arch, cwd=getSrcPath(), shell=True)
  
  subprocess.check_call("gn gen out/" + target_arch + "d", cwd=getSrcPath(), shell=True)
  subprocess.check_call("ninja -C out/" + target_arch + "d", cwd=getSrcPath(), shell=True)

  regex = re.compile(r".*\.lib$")
  mergetree(os.path.join(getOutPath(target_arch), "obj"), os.path.join(installPath, "lib"), 
    regex.match)

  regex = re.compile(r".*\.lib$")
  mergetree(os.path.join(getOutPath(target_arch) + "d", "obj"), os.path.join(installPath, "lib"), 
    regex.match, lambda n: "d".join(os.path.splitext(n)))

  regex = re.compile(r".*\.h$")
  mergetree(getSrcPath(), os.path.join(installPath, "include"), 
    lambda n: regex.match(n) and "third_party" not in n)
