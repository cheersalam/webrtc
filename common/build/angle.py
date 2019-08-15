import os
import subprocess
import shutil
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "angle"

GN_WINDOWS_CONFIG = """
target_cpu="{}"
is_debug={}
clang_use_chrome_plugins=false
enable_precompiled_headers=false
is_component_build=false
angle_enable_vulkan_validation_layers=false
build_angle_gles1_conform_tests=false
build_angle_deqp_tests=false
"""

GN_LINUX_MAC_OS_CONFIG = """
target_cpu="{}"
is_debug={}
clang_use_chrome_plugins=false
enable_precompiled_headers=false
is_component_build=false
"""

LIB_LIST = {"libEGL", "libGLESv1_CM", "libGLESv2"}
WINDOWS_LIB = "angle_util"
LINUX_MACOS_LIB = "libangle_util"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty")
  
def getExtactedFolderPath():
  return os.path.join(getRootPath(), "angle")

def getOutPath(build, arch):
   return os.path.join(getExtactedFolderPath(), "out", build, arch)
  
def getArgsPath(build, arch):
  return os.path.join(getExtactedFolderPath(), "out", build, arch, "args.gn")

def build(arch, build):
  angleDir = getExtactedFolderPath()
  toPath = devtools.getInstallPath(arch)

  target_arch = "32" if "32" in arch.lower() else "64"
  target_cpu = "x86" if target_arch == "32" else "x64"
  is_debug = "false" if "rel" in build.lower() else "true"
  
  if target_arch == "64":
    print "We can build x64, but findAngle.cmake don't support it, update it and remove this line"
    return 
    
  if not os.path.exists(angleDir) or not os.listdir(angleDir):
    try:
      os.mkdir(getRootPath())
    except os.error:
      pass
    
    subprocess.check_call("git clone https://chromium.googlesource.com/angle/angle", cwd=getRootPath(), shell=True)

  subprocess.check_call("git fetch", cwd=angleDir, shell=True)
  subprocess.check_call("git reset --hard 59b1ed4a60fc9cf57c3914eb4851ec94c8df21a9", cwd=angleDir, shell=True)

  subprocess.check_call("python scripts/bootstrap.py", cwd=angleDir, shell=True)
  subprocess.check_call("gclient sync", cwd=angleDir, shell=True)
  
  if "lin" in arch:
    subprocess.check_call("./build/install-build-deps.sh", cwd=angleDir, shell=True)

  try:
    os.makedirs(os.path.dirname(getArgsPath(build, target_cpu)))
  except os.error:
    pass

  GN_CONFIG = "";
  if "wind" in arch:
    GN_CONFIG = GN_WINDOWS_CONFIG
  else:
    GN_CONFIG = GN_LINUX_MAC_OS_CONFIG

  with open(getArgsPath(build, target_cpu), "w") as argsFile:
    argsFile.write(GN_CONFIG.format(target_cpu, is_debug))

  build_path = build + "/" + target_cpu
  subprocess.check_call("gn gen out/" + build_path, cwd=angleDir, shell=True)
  subprocess.check_call("ninja -C out/" + build_path, cwd=angleDir, shell=True)
  
  distutils.dir_util.copy_tree(os.path.join(angleDir, "include"), os.path.abspath(os.path.join(toPath, "include", "angle")))
  distutils.dir_util.copy_tree(os.path.join(angleDir, "src", "common"), os.path.abspath(os.path.join(toPath, "include", "angle", "common")))
  distutils.dir_util.copy_tree(os.path.join(angleDir, "util"), os.path.abspath(os.path.join(toPath, "include", "angle", "util")))
 
  try:
    os.makedirs(os.path.join(toPath, "pdb", "angle", build))
  except os.error as error:
    pass

  try:
    os.makedirs(os.path.join(toPath, "lib", "angle", build))
  except os.error as error:
    pass

  try:
    os.makedirs(os.path.join(toPath, "bin", "angle", build))
  except os.error as error:
    pass
 
  dll_path = os.path.join(toPath, "bin", "angle", build)
  pdb_path = os.path.join(toPath, "pdb", "angle", build)
  lib_path = os.path.join(toPath, "lib", "angle", build)
 
  for libs in LIB_LIST:
    if "wind" in arch:
      shutil.copy(os.path.join(getOutPath(build, target_cpu), libs + ".dll"),     dll_path)
      shutil.copy(os.path.join(getOutPath(build, target_cpu), libs + ".dll.pdb"), pdb_path)
      shutil.copy(os.path.join(getOutPath(build, target_cpu), libs + ".dll.lib"), os.path.join(toPath, "lib"))
    elif "lin" in arch:
      shutil.copy(os.path.join(getOutPath(build, target_cpu), libs + ".TOC"), pdb_path)
      shutil.copy(os.path.join(getOutPath(build, target_cpu), libs + ".so"),  lib_path)
    elif "darwin" in arch:
      shutil.copy(os.path.join(getOutPath(build, target_cpu), libs + ".TOC"),   pdb_path)
      shutil.copy(os.path.join(getOutPath(build, target_cpu), libs + ".dylib"), dll_path)

  if "wind" in arch:
    shutil.copy(os.path.join(getOutPath(build, target_cpu), WINDOWS_LIB + ".dll"),     dll_path)
    shutil.copy(os.path.join(getOutPath(build, target_cpu), WINDOWS_LIB + ".dll.pdb"), pdb_path)
    shutil.copy(os.path.join(getOutPath(build, target_cpu), WINDOWS_LIB + ".dll.lib"), os.path.join(toPath, "lib"))
  else:
    shutil.copy(os.path.join(getOutPath(build, target_cpu), LINUX_MACOS_LIB + ".TOC"), pdb_path)
    shutil.copy(os.path.join(getOutPath(build, target_cpu), LINUX_MACOS_LIB + ".so"),  lib_path)

def clean():
  devtools.rmtree(getExtactedFolderPath())
