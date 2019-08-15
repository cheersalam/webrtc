import os
import sys
import shutil
import distutils.dir_util
import subprocess
import find.sevenz as sevenz
import platform
import urllib2

g_msvsVersion = "2013"

def downloadFile(url, file_name):
  u = urllib2.urlopen(url)
  meta = u.info()
  file_size = 1
  try:
    file_size = int(meta.getheaders("Content-Length")[0])
  except:
    print "Unknown downloading size"
  print "Downloading: %s Bytes: %s" % (file_name, file_size)

  f = open(file_name, 'wb')
  file_size_dl = 0
  block_sz = 32*1024
  while True:
    buffer = u.read(block_sz)
    if not buffer:
      break

    file_size_dl += len(buffer)
    f.write(buffer)
    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
    status = status + chr(8)*(len(status)+1)
    print status,

  f.close()

def getMacosSDK():
  return "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.8.sdk"

def getMacosSDKVersion():
  return "10.8"

def rmtree(folder):
  import errno, os, stat, shutil

  def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
      os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO)
      func(path)
    else:
      raise
  try:
    shutil.rmtree(folder, ignore_errors=False, onerror=handleRemoveReadonly)
  except:
    print "rmtree fail " + folder


def patchFile(filePath, pattern, subst):
    import tempfile
    fh, absPath = tempfile.mkstemp()
    newFile = open(absPath, 'w')
    oldFile = open(filePath)
    for line in oldFile:
        newFile.write(line.replace(pattern, subst))
    newFile.close()
    os.close(fh)
    oldFile.close()

    os.remove(filePath)
    shutil.move(absPath, filePath)

def isExecutableInPath(name):
  import subprocess
  import platform
  cmd = "where" if platform.system() == "Windows" else "which"
  try:
    devnull = open(os.devnull)
    proc = subprocess.Popen([cmd, name], stdout=devnull, stderr=devnull)
    proc.communicate()
    proc.wait()
    if(proc.returncode == 0):
      return True
  except OSError as e:
    if e.errno == os.errno.ENOENT:
      return False
  return False

def updateModuleCmd(module):
  if isExecutableInPath(module.exe):
    module.cmd = module.exe
    return
  else:
    for path in module.paths:
      exepath = os.path.join(path, module.exe)
      if os.path.isfile(exepath):
        module.cmd = exepath
        return
  raise Exception("No module found: " + module.exe + "\n" + module.helpMessage)

def initModules():
  updateModuleCmd(sevenz)

def signFile(path, certPath, password):
  paths = [
    "C:\\Program Files (x86)\\Windows Kits\\10\\bin\\10.0.17134.0\\x86\\signtool.exe",
    "C:\\Program Files (x86)\\Windows Kits\\8.1\\bin\\x86\\signtool.exe"
  ]

  for p in paths:
    if os.path.exists(p):
      break

  patchCmd = [p,
              "sign",
              "/t",
              "http://timestamp.globalsign.com/scripts/timstamp.dll",
              "/f",
              os.path.abspath(certPath),
              "/p",
              password,
              "/d",
              os.path.abspath(path),
              os.path.abspath(path)]
  proc = subprocess.call(patchCmd, env=os.environ.copy())

def getInstallPath(arch):
  return os.path.abspath(os.path.join(rootDir, "3rdparty", "build-" + arch.lower()))

def copyWindowsFiles(fromDir, toDir, ext):
  for root, dirs, files in os.walk(fromDir):
    for f in files:
      arch = ""
      build = ""
      if "Win32" in root:
        arch = "Win32"
      if "x64" in root:
        arch = "x64"
      if "Debug" in root:
        build = "Debug"
      if "Release" in root or "RelWithDebInfo" in root:
        build = "Release"

      if f.endswith(ext):
        if not os.path.isdir(toDir):
          os.makedirs(toDir)
        try:
          shutil.copy(os.path.join(root, f), toDir)
        except:
          print "failed to copy, I hope it is already exists :)"

def failIfReturnCodeNotZero(retcode):
  if retcode != 0:
    raise Exception("Return code is not valid " + str(retcode))

def get3rdpartyInstallPath(arch):
  arch = arch.lower()
  return os.path.abspath(getInstallPath(arch))

def getTmpPath(root, arch, build):
  return os.path.join(root, "tmp-" + arch.lower() + "-" + build)

def copy2dir(src, dst):
  obj = os.path.join(dst, os.path.basename(src))
  if os.path.exists(obj) or os.path.islink(obj):
    if os.path.isdir(obj):
      if os.path.islink(obj):
        os.unlink(obj)
      else:
        shutil.rmtree(obj)
    else:
      if os.path.islink(obj):
        os.unlink(obj)
      else:
        os.remove(obj)

  if os.path.islink(src):
    linkto = os.readlink(src)
    os.symlink(linkto, obj)
  else:
    shutil.copy(src, obj)
    print "file copy: " + obj

def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise

def findAndCopy(froot, cfiles):
  for root, dirs, files in os.walk(froot):
    for f in files:
      for cf in cfiles:
        if cf['name'] in f and cf['ext'] in f:
          out = cf['path']
          if 'save_folders' in cf:
            out = os.path.join(out, os.path.relpath(root, froot))

          if not os.path.exists(out):
            mkdir_p(out)
          copy2dir(os.path.join(root, f), out)

def buildMacOsPackage(root, arch, build, outpath):
  if "darwin" in arch:
    print "building macos dmg package..."
    cpackcmd = ["cpack", "--verbose", "--debug"]
    folder = getTmpPath(root, arch, build)
    proc = subprocess.call(cpackcmd, cwd=folder, env=os.environ.copy())
    failIfReturnCodeNotZero(proc)

    tdir = os.path.dirname(outpath)
    if not os.path.exists(tdir):
      os.mkdir(tdir)
    shutil.copy(os.path.join(root, "buildproject", "LiquidSkyClient.dmg"), outpath)

def changeIdMacOsDLyb(folderPath, filePath, newid):
  intcmd = ["install_name_tool", "-id"]
  intcmd.append(newid)
  intcmd.append(filePath)

  print "[change id] RUN INTool at " + folderPath
  print intcmd
  proc = subprocess.call(intcmd, cwd=folderPath, env=os.environ.copy())
  failIfReturnCodeNotZero(proc)

def changeRpathMacOsDLyb(folderPath, filePath, rpath):
  intcmd = ["install_name_tool", "-add_rpath"]
  intcmd.append(rpath)
  intcmd.append(filePath)

  print "[change rpath] RUN INTool at " + folderPath
  print intcmd
  proc = subprocess.call(intcmd, cwd=folderPath, env=os.environ.copy())
  #failIfReturnCodeNotZero(proc)

def changeDepsMacOsDLyb(folderPath, filePathDold, filePathDnew, filePath):
  intcmd = ["install_name_tool", "-change"]
  intcmd.append(filePathDold)
  intcmd.append(filePathDnew)
  intcmd.append(filePath)

  print "[dep] RUN INTool at " + folderPath
  print intcmd
  proc = subprocess.call(intcmd, cwd=folderPath, env=os.environ.copy())
  failIfReturnCodeNotZero(proc)

def changeIDMacOSFFmpegLybs(arch, depArchs):
  if "darwin" in arch:
    folderPath = os.path.join(getInstallPath(arch), "lib")

    names = ["libavutil.dylib", "libavcodec.dylib", "libavformat.dylib", "libswscale.dylib"]
    lnames = ["libavutil.55.dylib", "libavcodec.57.dylib", "libavformat.57.dylib", "libswscale.4.dylib"]

    prefixNewId = "@rpath/"
    newRPath = "@loader_path/"
    newDep = "@loader_path/"

    for name in names :
      print "----------------------------"
      print name

      path = os.path.join(folderPath, name)

      changeIdMacOsDLyb(folderPath, path, prefixNewId + name)
      changeRpathMacOsDLyb(folderPath, path, newRPath)

      for darch in depArchs:
        print "---- " + darch
        depFolderPath = os.path.join(getInstallPath(darch), "lib")

        index = 0
        for lname in lnames :
          newname = names[index]
          index = index + 1
          print "-------- find change: " + lname + " to " + newname
          changeDepsMacOsDLyb(folderPath, os.path.join(depFolderPath, lname), os.path.join(newDep, newname), path)

def prepareMacOSFFmpegLybs(arch, depArchs):
  if "darwin" in arch:
    folderPath = os.path.join(getInstallPath(arch), "lib")

    names = ["libavutil.dylib", "libavcodec.dylib", "libavformat.dylib", "libswscale.dylib"]
    lnames = ["libavutil.55.dylib", "libavcodec.57.dylib", "libavformat.57.dylib", "libswscale.4.dylib"]

    for name in names :
      print "----------------------- preparing..."
      print name

      path = os.path.join(folderPath, name)
      changeIdMacOsDLyb(folderPath, path, path)

      for darch in depArchs:
        print "---- " + darch
        depFolderPath = os.path.join(getInstallPath(darch), "lib")

        index = 0
        for lname in lnames :
          newname = names[index]
          index = index + 1
          print "-------- find change: " + lname + " to " + newname
          changeDepsMacOsDLyb(folderPath, os.path.join(depFolderPath, lname), os.path.join(depFolderPath, newname), path)


def buildCmake(cmakeFilePath, rootTmpPath, extraFlagsList, arch, build, slnname, ignoreInstallPrefix = False, writeBuildArchitecture = False, build8 = False, package = False, install=True):
  arch = arch.lower()

  tmpPath = getTmpPath(rootTmpPath, arch, build)

  if build8:
    tmpPath += "-8"

  if not os.path.isdir(tmpPath):
    os.makedirs(tmpPath)
  else:
    rmtree(tmpPath)
    os.makedirs(tmpPath)

  print "cmake"
  cmakecmd = ["cmake", os.path.abspath(cmakeFilePath)]

  if writeBuildArchitecture:
    if "32" in arch:
      cmakecmd.append("-DCMAKE_BUILD_ARCHITECTURE=x86")
    if "64" in arch:
      cmakecmd.append("-DCMAKE_BUILD_ARCHITECTURE=x64")

  cmakecmd.append("-DCMAKE_PREFIX_PATH=" + get3rdpartyInstallPath(arch))

  for flag in extraFlagsList:
    cmakecmd.append(flag)

  if not ignoreInstallPrefix:
    cmakecmd.append("-DCMAKE_INSTALL_PREFIX=" + get3rdpartyInstallPath(arch))

  if "wind" in arch:
    if "32" in arch:
      arch = "Win32"
    if "64" in arch:
      arch = "x64"

    cmakecmd.append("-G")

    if "2013" in g_msvsVersion:
      if "64" not in arch:
        cmakecmd.append("Visual Studio 12 2013")
      else:
        cmakecmd.append("Visual Studio 12 2013 Win64")

      cmakecmd.append("-T")
      if build8:
        cmakecmd.append("v120")
      else:
        cmakecmd.append("v120_xp")

    if "2015" in g_msvsVersion:
      if "64" not in arch:
        cmakecmd.append("Visual Studio 14 2015")
      else:
        cmakecmd.append("Visual Studio 14 2015 Win64")

      cmakecmd.append("-T")
      if build8:
        cmakecmd.append("v140")
      else:
        cmakecmd.append("v140_xp")

    if "2017" in g_msvsVersion:
      if "64" not in arch:
        cmakecmd.append("Visual Studio 15 2017")
      else:
        cmakecmd.append("Visual Studio 15 2017 Win64")

      cmakecmd.append("-T")
      cmakecmd.append("v141")

      if build8:
        cmakecmd.append("-DBUILD_CLIENT=FALSE")
      else:
        cmakecmd.append("-DBUILD_CLIENT=TRUE")

    proc = subprocess.call(cmakecmd, cwd=tmpPath, env=os.environ.copy())
    failIfReturnCodeNotZero(proc)

    if slnname == None:
      return
    print "building"
    devenvcmd = ["cmake", "--build", os.path.abspath(tmpPath), "--config", build, "--target", "ALL_BUILD"]
    print devenvcmd
    p = subprocess.Popen(devenvcmd, env=os.environ.copy(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    print output
    print err
    failIfReturnCodeNotZero(p.returncode)

    if not install:
      return
      
    print "install"
    devenvcmd = ["cmake", "--build", os.path.abspath(tmpPath), "--config", build, "--target", "INSTALL"]
    print devenvcmd
    p = subprocess.Popen(devenvcmd, env=os.environ.copy(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    print output
    print err
    failIfReturnCodeNotZero(p.returncode)

  elif "linux" in arch or "darwin" in arch:
    if build8:
      return

    cmakecmd.append("-DCMAKE_POSITION_INDEPENDENT_CODE=YES")

    if "linux" in arch:
      cmakecmd.append("-DCMAKE_CXX_FLAGS='-std=c++11 -fPIC -fvisibility=hidden'")

    if "darwin" in arch:
      cmakecmd.append("-DCMAKE_CXX_FLAGS='-std=c++11 -stdlib=libc++ -fPIC -fvisibility=hidden'")
      cmakecmd.append("-DCMAKE_XCODE_ATTRIBUTE_CLANG_CXX_LANGUAGE_STANDARD=c++11")
      cmakecmd.append("-DCMAKE_XCODE_ATTRIBUTE_CLANG_CXX_LIBRARY=libc++")
    if "darwin" in arch:
      cmakecmd.append("-DCMAKE_OSX_DEPLOYMENT_TARGET=" + getMacosSDKVersion())

    cmakecmd.append("-DCMAKE_BUILD_TYPE=" + build)

    cmakearchs = list()
    if ("x86_32" in arch) or ("uni" in arch):
      cmakearchs.append("i386")
    if ("x86_64" in arch) or ("uni" in arch):
      cmakearchs.append("x86_64")

    print cmakearchs
    if len(cmakearchs) > 0:
      cmakecmd.append("-DCMAKE_OSX_ARCHITECTURES=" + ";".join(cmakearchs))

    if "darwin" in arch and slnname == "xcode":
      cmakecmd.append("-G")
      cmakecmd.append("Xcode")
      print cmakecmd
      proc = subprocess.call(cmakecmd, cwd=tmpPath, env=os.environ.copy())
      failIfReturnCodeNotZero(proc)
      return

    print cmakecmd
    proc = subprocess.call(cmakecmd, cwd=tmpPath, env=os.environ.copy())

    from multiprocessing import cpu_count
    cpuCount = cpu_count()
    if cpuCount > 8:
      cpuCount = 8
    multiCoreParam = "-j" + str(cpuCount)

    print "building"
    devenvcmd = ["cmake", "--build", os.path.abspath(tmpPath), "--target", "all", "--", multiCoreParam]
    print devenvcmd
    p = subprocess.Popen(devenvcmd, env=os.environ.copy(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    print output
    print err
    failIfReturnCodeNotZero(p.returncode)

    print "install"
    devenvcmd = ["cmake", "--build", os.path.abspath(tmpPath), "--target", "install"]
    print devenvcmd
    p = subprocess.Popen(devenvcmd, env=os.environ.copy(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    print output
    print err
    failIfReturnCodeNotZero(p.returncode)

    if package:
      print "package"
      devenvcmd = ["cmake", "--build", os.path.abspath(tmpPath), "--target", "package"]
      print devenvcmd
      p = subprocess.Popen(devenvcmd, env=os.environ.copy(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      output, err = p.communicate()
      print output
      print err
      failIfReturnCodeNotZero(p.returncode)


def mergeLibs(ios, isim, iuni ):
  iosLib = os.path.abspath(os.path.join(ios, "lib"))
  isimLib = os.path.abspath(os.path.join(isim, "lib"))
  iuniLib = os.path.abspath(os.path.join(iuni, "lib"))

  simFiles = list()
  iosFiles = list()

  for root, dirs, files in os.walk(isimLib):
    for f in files:
      if f.endswith(".a") or f.endswith(".dylib"):
        simFiles.append(f)

  for root, dirs, files in os.walk(isimLib):
    for f in files:
      if f.endswith(".a") or f.endswith(".dylib"):
        iosFiles.append(f)

  simFiles.sort()
  iosFiles.sort()

  if not os.path.isdir(iuniLib):
    os.makedirs(iuniLib)

  if os.path.isdir(os.path.join(ios, "include")):
    distutils.dir_util.copy_tree(os.path.join(ios, "include"), os.path.join(iuni, "include"))

  for sf in simFiles:
    print sf
    if sf not in iosFiles:
      raise Exception(sf)
    toFile = os.path.abspath(os.path.join(iuniLib, sf))

    if os.path.isfile(toFile):
      os.remove(toFile)
    f1 = os.path.abspath(os.path.join(iosLib, sf))
    f2 = os.path.abspath(os.path.join(isimLib, sf))
    if f1.endswith(".a"):
      mergeLibsCmd = ["libtool", "-static", "-o", toFile, f1, f2]
      proc = subprocess.call(mergeLibsCmd, env=os.environ.copy())
    else:
      mergeBinCmd = ["lipo", "-create", f1, f2, "-output", toFile]
      proc = subprocess.call(mergeBinCmd, env=os.environ.copy())

def mergeFile(filename, f1, f2, fo):
  print filename
  fod = os.path.join(fo, os.path.dirname(filename))
  if not os.path.isdir(fod):
    os.makedirs(fod)

  ff1 = os.path.join(f1, filename)
  ff2 = os.path.join(f2, filename)
  ffo = os.path.join(fo, filename)

  if os.path.isfile(ffo):
    os.remove(ffo)

  mergeBinCmd = ["lipo", "-create", ff1, ff2, "-output", ffo]
  proc = subprocess.call(mergeBinCmd, env=os.environ.copy())

def copyReplace(f1, f2):
  if os.path.isfile(f2):
    os.remove(f2)

  shutil.copy(f1, f2)
