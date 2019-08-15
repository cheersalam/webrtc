import os
import subprocess
import shutil
import distutils.dir_util
from common import devtools
from common.find import sevenz

name = "ffmpeg"

def getRootPath():
  return os.path.join(devtools.rootDir, "3rdparty", "ffmpeg")

def getExtactedFolderPath():
  return os.path.join(getRootPath(), "ffmpeg")

def getWorkingFolderPath():
  return os.path.join(getRootPath(), "ffmpeg")


def findGridSdkZip(root):
  for root, dirs, files in os.walk(root):
    for f in files:
      if "ffmpeg" in f and ".7z" in f:
        return os.path.join(root, f)
  raise Exception("No ffmpeg 7z found")

def build(arch, build):
  if "wind" in arch:
    print "Extract ffmpeg"
    unzipcmd = [sevenz.cmd, "x", "-y", "-o" + getExtactedFolderPath(), findGridSdkZip(getRootPath())]
    proc = subprocess.call(unzipcmd)

    ffmpegDir = getExtactedFolderPath();
    toPath = devtools.getInstallPath(arch)
    distutils.dir_util.copy_tree(os.path.join(ffmpegDir, "include"), os.path.abspath(os.path.join(toPath, "include")))
    devtools.copyWindowsFiles(os.path.join(ffmpegDir, "bin"), os.path.abspath(os.path.join(toPath, "bin")), ".dll")
    devtools.copyWindowsFiles(os.path.join(ffmpegDir, "bin"), os.path.abspath(os.path.join(toPath, "lib")), ".lib")
    devtools.copyWindowsFiles(os.path.join(ffmpegDir), os.path.abspath(os.path.join(toPath, "pdb", "ffmpeg")), ".pdb")
  elif "lin" in arch or "dar" in arch:
    workingDir = getWorkingFolderPath()
    if not os.path.isdir(workingDir):
      print "Extract ffmpeg"
      bz = findbz(getRootPath())
      unzipcmd = ["tar", "jxvf", bz, "-C", getRootPath()]
      proc = subprocess.call(unzipcmd)
      devtools.failIfReturnCodeNotZero(proc)
    shutil.copytree(workingDir, os.path.join(workingDir, "..", arch))
    workingDir = os.path.join(workingDir, "..", arch)

    print "configure"
    perlcmd = ["./configure", "--disable-bzlib", "--disable-iconv", "--disable-lzma", "--disable-sdl", "--disable-xlib", "--disable-zlib", "--disable-yasm", "--disable-avfilter", "--disable-avdevice", "--disable-swresample",
      "--disable-ffmpeg", "--disable-ffprobe", "--disable-ffserver", "--disable-ffplay", "--disable-static", "--enable-shared", "--disable-everything", "--enable-hwaccels",
      "--enable-decoder=h264", "--enable-decoder=h264_vdpau", "--enable-vaapi", "--enable-muxer=matroska", "--enable-demuxer=matroska", "--enable-demuxer=mpegts", "--enable-parser=h264", "--enable-protocol=file", "--prefix=" + devtools.getInstallPath(arch)]

    extra = []

    if "darwin" in arch and "x86_32" in arch:
      extra = ["--sysroot=" + devtools.getMacosSDK(), "--extra-cflags=\"-arch\ i386\ -DDMACOSX_DEPLOYMENT_TARGET=" + devtools.getMacosSDKVersion()
        + "\ -mmacosx-version-min=" + devtools.getMacosSDKVersion() + "\"",
        "--extra-ldflags=\"-arch\ i386\ -isysroot\ " + devtools.getMacosSDK() + "\ -mmacosx-version-min=" + devtools.getMacosSDKVersion() + "\"",
        "--arch=x86_32", "--target-os=darwin", "--enable-cross-compile"]

    if "darwin" in arch and "x86_64" in arch:
      extra = ["--sysroot=" + devtools.getMacosSDK(), "--extra-cflags=\"-arch\ x86_64\ -DDMACOSX_DEPLOYMENT_TARGET=" + devtools.getMacosSDKVersion()
      + "\ -mmacosx-version-min=" + devtools.getMacosSDKVersion() + "\"",
      "--extra-ldflags=\"-arch\ x86_64\ -isysroot\ " + devtools.getMacosSDK() + "\ -mmacosx-version-min=" + devtools.getMacosSDKVersion() +  "\"",
      "--arch=x86_64", "--target-os=darwin", "--enable-cross-compile"]
    for e in extra:
      perlcmd.append(e)

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

    if "darwin" in arch:
      folderPath = os.path.join(devtools.getInstallPath(arch), "lib")
      names = ["libavutil.dylib", "libavcodec.dylib", "libavformat.dylib", "libswscale.dylib"]
      lnames = ["libavutil.55.dylib", "libavcodec.57.dylib", "libavformat.57.dylib", "libswscale.4.dylib"]

      prefixNewId = "@rpath/"
      newRPath = "@loader_path/"
      newDep = "@loader_path/"

      for n in names:
        print "----------------------- preparing... " + n

        path = os.path.join(folderPath, n)
        devtools.changeIdMacOsDLyb(folderPath, path, prefixNewId + n)
        devtools.changeRpathMacOsDLyb(folderPath, path, newRPath)

        index = 0
        for lname in lnames :
          newname = names[index]
          index = index + 1
          print "-------- find change: " + lname + " to " + newname
          devtools.changeDepsMacOsDLyb(folderPath, os.path.join(folderPath, lname), os.path.join(newDep, newname), path)


def clean():
  devtools.rmtree(getExtactedFolderPath())
