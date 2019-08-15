import os
import subprocess
import shutil
import multiprocessing
from common import devtools
from common.find import sevenz

name = "boost"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "boost")

def getExtactedFolderPath():
  return os.path.join(getRootPath(), "boost")

def findBoostZip(root):
  for root, dirs, files in os.walk(root):
    for f in files:
      if "boost" in f and ".7z" in f:
        return os.path.join(root, f)

  raise Exception("No boost zip found")

def fixBoostFileStruct(rootDir, targetDir):
  for root, dirs, files in os.walk(rootDir):
    for d in dirs:
      if "boost_" in d:
        shutil.move(os.path.join(targetDir, d), os.path.join(targetDir, "boost"))
        return True
  raise Exception("Failed to find extracted boost folder")
        

def build(arch, build):
  archl = arch.lower()
  installPath = devtools.getInstallPath(arch)
  if "ios" in archl:
    buildscript = os.path.join(getRootPath(), "ios-build", "build-libstdc++.sh")
    print buildscript
    proc = subprocess.call([os.path.abspath(buildscript), os.path.abspath(installPath)])
  else:
    if not os.path.isdir(getExtactedFolderPath()):
      print "Extract boost"
      try:
        findBoostZip(getRootPath())
      except:
        url = 'https://dl.bintray.com/boostorg/release/1.70.0/source/boost_1_70_0.7z'
        fname = os.path.join(getRootPath(), url.rsplit('/', 1)[1])

        devtools.downloadFile(url, fname)

      unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getRootPath(), findBoostZip(getRootPath())]
      proc = subprocess.call(unzipcmd)
      fixBoostFileStruct(getRootPath(), getRootPath())
    if "wind" in archl:
      bjam_name = "bjam.exe"
      if "2013" in devtools.g_msvsVersion:
        toolset_name = "--toolset=msvc-12.0"
      elif "2015" in devtools.g_msvsVersion:
        toolset_name = "--toolset=msvc-14.0"
      elif "2017" in devtools.g_msvsVersion:
        toolset_name = "--toolset=msvc-14.1"
      else:
        raise Exception("unknown msvs version")

      bootstrap_name = "bootstrap.bat"
    elif "lin" in archl or "dar" in archl:
      bjam_name = "bjam"
      toolset_name = ""
      bootstrap_name = "bootstrap.sh"

    if "dar" in archl:
      toolset_name="--toolset=clang"
      sdk = devtools.getMacosSDKVersion()
      sdkPath = "/Developer/SDKs/MacOSX" + sdk + ".sdk"
      if os.path.isdir(sdkPath):
        print "mac os x " + sdk + " sdk exists"
      else:
        print "please place mac os x " + sdk + " sdk to /Deveveloper"

    bjam = os.path.join(getExtactedFolderPath(), bjam_name)
    if not os.path.isfile(bjam):
      proc = subprocess.call([os.path.abspath(os.path.join(getExtactedFolderPath(), bootstrap_name))], cwd=getExtactedFolderPath(), env=os.environ.copy())

    libdir = os.path.join(getExtactedFolderPath(), "stage", "lib")

    boostlibs = ["thread", "system", "atomic", "date_time", "filesystem", "chrono", "coroutine", "context"]

    buildBoost = [os.path.abspath(bjam), "-q"]
    buildBoost.append(toolset_name)
    buildBoost.append("variant=" + build.lower())
    buildBoost.append("link=static")
    buildBoost.append("runtime-link=static")
    buildBoost.append("define=BOOST_NO_RTTI")
    buildBoost.append("define=BOOST_EXCEPTION_DISABLE")
    buildBoost.append("define=BOOST_REGEX_NO_LIB")

    if "x86" in archl:
      buildBoost.append("architecture=x86")
    elif "arm" in archl:
      buildBoost.append("architecture=arm")

    if "64" in archl:
      buildBoost.append("address-model=64")
    elif "32" in archl or "386" in archl:
      buildBoost.append("address-model=32")

    if "dar" in archl:
      sdk = devtools.getMacosSDKVersion()
      buildBoost.append("macosx-version=" + sdk)
      buildBoost.append("macosx-version-min=" + sdk)

    if "lin" in archl:
      buildBoost.append("cxxflags=-fPIC")

    if "dar" in archl:
      buildBoost.append("cflags=-mmacosx-version-min=" + sdk)
#      buildBoost.append("mflags=-mmacosx-version-min=" + sdk)
#      buildBoost.append("mmflags=-mmacosx-version-min=" + sdk)
      buildBoost.append("cxxflags=-fvisibility=hidden -std=c++11 -stdlib=libc++ -mmacosx-version-min=" + sdk)
      buildBoost.append("linkflags=-stdlib=libc++ -mmacosx-version-min=" + sdk)

    buildBoost.append("-j" + str(multiprocessing.cpu_count()))
    for lib in boostlibs:
      buildBoost.append("--with-" + lib)
    buildBoost.append("--prefix=" + installPath)
    buildBoost.append("--build-dir=" + os.path.abspath(os.path.join(devtools.rootDir, "3rdparty", "tmp")))
    buildBoost.append("install")
    print buildBoost
    proc = subprocess.call(buildBoost, cwd=getExtactedFolderPath(), env=os.environ.copy())


def clean():
  devtools.rmtree(getExtactedFolderPath())
