import os
import subprocess
import shutil
import urllib
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "openssl"
#zipUrl = "http:// .tar.gz"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "openssl")

def getWorkingFolderPath():
  return os.path.join(getRootPath(), "openssl")

def findZip(rootDir):
  for root, dirs, files in os.walk(rootDir):
    for f in files:
      if "openssl" in f and "tar.gz" in f:
        return os.path.join(root, f)
  raise Exception("No openssl .7z found")

def fixFileStruct(rootDir, targetDir):
  for root, dirs, files in os.walk(rootDir):
    for d in dirs:
      if "openssl-" in d:
        shutil.move(os.path.join(root, d), targetDir)
        return True
  raise Exception("Failed to find extracted " + name + "folder")

def build(arch, build):
  workingDir = getWorkingFolderPath()
  if not os.path.isdir(workingDir):
    print "Extract openssl"
    gz = findZip(getRootPath())
    tar = gz[:-3]
    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), gz]
    proc = subprocess.call(unzipcmd)
    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), tar]
    proc = subprocess.call(unzipcmd)
    fixFileStruct(getRootPath(), workingDir)

  newwd = os.path.join(workingDir, "..", arch)

  devtools.rmtree(newwd)
  shutil.copytree(workingDir, newwd)
  workingDir = newwd

  if "wind" in arch:
    if "Debug" in build:
      print "no debug build for openssl"
      return
    print "perl"
    buildtype = "VC-WIN32"
    asmcommand = "do_nasm.bat"
    if "64" in arch:
      buildtype = "VC-WIN64A"
      asmcommand = "do_win64a.bat"

    perlcmd = ["perl.exe", "Configure", buildtype, "--prefix=" + devtools.getInstallPath(arch), "--openssldir=" + devtools.getInstallPath(arch), "enable-static-engine", "no-shared", "enable-hw"]
    proc = subprocess.call(perlcmd, cwd=workingDir, env=os.environ.copy())
    devtools.failIfReturnCodeNotZero(proc)

#    print "do nasm"
#    domscmd = [os.path.abspath(os.path.join(workingDir, "ms", asmcommand))]
#    proc = subprocess.call(domscmd, cwd=workingDir, env=os.environ.copy())
#    devtools.failIfReturnCodeNotZero(proc)

    print "building " + name
    devenvcmd = ["nmake.exe", "-f", os.path.abspath(os.path.join(workingDir, "makefile"))]
    proc = subprocess.call(devenvcmd, cwd=workingDir, env=os.environ.copy())
    devtools.failIfReturnCodeNotZero(proc)

    devenvcmd = ["nmake.exe", "-f", os.path.abspath(os.path.join(workingDir, "makefile")), "install_sw", "install_ssldirs"]
    proc = subprocess.call(devenvcmd, cwd=workingDir, env=os.environ.copy())
    devtools.failIfReturnCodeNotZero(proc)
  elif "lin" in arch:
    print "perl"
    perlcmd = [os.path.abspath(os.path.join(workingDir, "config"))]

    perlcmd.append("--prefix=" + devtools.getInstallPath(arch))
    print perlcmd
    proc = subprocess.call(perlcmd, cwd=workingDir, env=os.environ.copy())
    devtools.failIfReturnCodeNotZero(proc)

    print "building " + name
    devenvcmd = ["make"]
    proc = subprocess.call(devenvcmd, cwd=workingDir, env=os.environ.copy())
    devtools.failIfReturnCodeNotZero(proc)

    devenvcmd = ["make",  "install"]
    proc = subprocess.call(devenvcmd, cwd=workingDir, env=os.environ.copy())
    devtools.failIfReturnCodeNotZero(proc)
  elif "darwin" in arch:
    print "perl"
    perlcmd = ["perl", os.path.abspath(os.path.join(workingDir, "Configure"))]

    if "x86_32" in arch:
      perlcmd.append("darwin-i386-cc")
      archname = "i386"
    if "x86_64" in arch:
      perlcmd.append("darwin64-x86_64-cc")
      archname = "x86_64"

    perlcmd.append("--prefix=" + devtools.getInstallPath(arch))
    print perlcmd
    proc = subprocess.call(perlcmd, cwd=workingDir, env=os.environ.copy())
    devtools.failIfReturnCodeNotZero(proc)

    sedcmd = ["sed", "-ie", 's!^CFLAG=!CFLAG=-isysroot ' + devtools.getMacosSDK()  + ' -arch ' + archname + ' -mmacosx-version-min=' + devtools.getMacosSDKVersion() + ' !', os.path.abspath(os.path.join(workingDir, "Makefile"))]
    print sedcmd
    proc = subprocess.call(sedcmd, cwd=workingDir, env=os.environ.copy())
    devtools.failIfReturnCodeNotZero(proc)

    print "building " + name
    devenvcmd = ["make"]
    proc = subprocess.call(devenvcmd, cwd=workingDir, env=os.environ.copy())
    devtools.failIfReturnCodeNotZero(proc)

    devenvcmd = ["make",  "install"]
    proc = subprocess.call(devenvcmd, cwd=workingDir, env=os.environ.copy())
    devtools.failIfReturnCodeNotZero(proc)

  return True
