#!/usr/bin/env python
import os
import sys
import time
import glob
import socket
import shutil
import distutils
import subprocess
import platform
import argparse
import getpass
import ConfigParser
from os.path import expanduser
from email.Utils import formatdate
import common.devtools as devtools
import common.find.sevenz as sevenz
import common.res_pack as respack
import common.build.gridsdk as gridsdk
import common.build.boost as boost
import common.build.glew as glew
import common.build.ffmpeg as ffmpeg
import common.build.freetype as freetype
import common.build.libpng as libpng
import common.build.crashrpt as crashrpt
import common.build.openssl as openssl
import common.build.speex as speex
import common.build.glfw as glfw
import common.build.protobuf as protobuf
import common.build.opus as opus
import common.build.curl as curl
import common.build.dht as dht
import common.build.rapidjson as rj
import common.build.nvml as nvml
import common.build.gflags as gflags
import common.build.cef as cef
import common.build.u2ec as u2ec
import common.build.nvapi as nvapi
import common.build.webrtc as webrtc
import common.build.gtest as gtest
import common.build.angle as angle

def we_are_frozen():
  return hasattr(sys, "frozen")

def module_path():
  encoding = sys.getfilesystemencoding()
  if we_are_frozen():
    return os.path.dirname(unicode(sys.executable, encoding))
  return os.path.dirname(unicode(__file__, encoding))

devtools.rootDir = module_path()
devtools.initModules()
pfm = platform.system().lower()

builds = list()
archs = list()
deparchs = list()
extraargs = list()

g_outdirname = "buildproject"

allPlatforms = ["windows-x86_32", "windows-x86_64", "linux-x86_64", "linux-x86_32", "darwin-x86_64"]
all3rdpartyLibs = [
  ("boost"    , { "build" : boost.build,    "platforms" : allPlatforms }),
  ("glew"     , { "build" : glew.build,     "platforms" : allPlatforms }),
  ("gridsdk"  , { "build" : gridsdk.build,  "platforms" : allPlatforms }),
  ("ffmpeg"   , { "build" : ffmpeg.build,   "platforms" : ["windows-x86_32", "darwin-x86_64", "linux-x86_64", "linux-x86_32"] }),
  ("freetype" , { "build" : freetype.build, "platforms" : allPlatforms }),
  ("libpng"   , { "build" : libpng.build,   "platforms" : allPlatforms }),
  ("crashrpt" , { "build" : crashrpt.build, "platforms" : ["windows-x86_32", "windows-x86_64"] }),
  ("openssl"  , { "build" : openssl.build,  "platforms" : allPlatforms }),
  ("speex"    , { "build" : speex.build,    "platforms" : allPlatforms }),
  ("glfw"     , { "build" : glfw.build,     "platforms" : allPlatforms }),
  ("protobuf" , { "build" : protobuf.build, "platforms" : allPlatforms }),
  ("opus"     , { "build" : opus.build,     "platforms" : allPlatforms }),
  ("curl"     , { "build" : curl.build,     "platforms" : allPlatforms }),
  ("dht"      , { "build" : dht.build,      "platforms" : allPlatforms }),
  ("rj"       , { "build" : rj.build,       "platforms" : allPlatforms }),
  ("nvml"     , { "build" : nvml.build,     "platforms" : allPlatforms }),
  ("cef"      , { "build" : cef.build,      "platforms" : ["windows-x86_32", "darwin-x86_64"] }),
  ("gflags"   , { "build" : gflags.build,   "platforms" : allPlatforms }),
  ("u2ec"     , { "build" : u2ec.build,     "platforms" : ["windows-x86_32", "windows-x86_64"] }),
  ("nvapi"    , { "build" : nvapi.build,    "platforms" : ["windows-x86_32", "windows-x86_64"] }),
  ("webrtc"   , { "build" : webrtc.build,   "platforms" : ["windows-x86_32"] }),
  ("gtest"    , { "build" : gtest.build,    "platforms" : ["windows-x86_32", "windows-x86_64"] }),
  ("angle"    , { "build" : angle.build,    "platforms" : ["windows-x86_32"] }),
]

EXCLUDE_FROM_SERVER = set(["angle"])

def prepareArgs():
  global builds
  global archs
  global deparchs
  global extraargs
  if "wind" in pfm:
    builds = ["Debug", "Release"]
    extraargs = []
    if "LSBUILD" not in os.environ:
      print "Please use vars*.bat for correct build enviroment"
      exit(-1)
    else:
      if "64" in os.environ["LSBUILD"]:
        archs = ["windows-x86_64"]
      else:
        archs = ["windows-x86_32"]
    if "LSMSVS" in os.environ:
      devtools.g_msvsVersion = os.environ["LSMSVS"]

  elif "lin" in pfm:
    builds = ["Release"]
    extraargs = ["-DLINUX=1", "-D_OPENSSL_VERSION=1.0.0"]
    if "64" in platform.architecture()[0]:
      archs = ["linux-x86_64"]
    elif "32" in platform.architecture()[0]:
      archs = ["linux-x86_32"]
  elif "dar" in pfm:
    builds = ["Release"]
    extraargs = ["-DMACOS=1", "-D_OPENSSL_VERSION=1.0.0"]
    deparchs = ["darwin-x86_64"]
    archs = ["darwin-x86_64"]

def clean():
  devtools.rmtree(os.path.join(module_path(), "buildproject"))
  devtools.rmtree(os.path.join(module_path(), "buildproject-zip"))

def build3rdparty(libnames, serverOnly):
  prepareArgs()

  for buildType in builds:
    for arch in archs:
      for lib in all3rdpartyLibs:
        name, info = lib
        if serverOnly and name in EXCLUDE_FROM_SERVER:
          continue
        if "all" in libnames or name in libnames:
          if arch in info["platforms"]:
            print "Building: " + name
            info["build"](arch, buildType)
          else:
            print "Skip: " + name

def gitDescribe():
  cmd = ["git", "describe", "--tags", "--long"]
  cwd = os.path.abspath(module_path())
  out = subprocess.check_output(cmd, shell=False, cwd=cwd)
  out = out.split("\n", 1)[0]
  return out


def buildproject(whatbuild, productversion, serverOnly):
  prepareArgs()

  dodevelop = "debug" in whatbuild
  dorelease = "release" in whatbuild
  dotest = "test" in whatbuild

  solutionName = "liquidsky.sln"
  if ("dproject" in whatbuild):
    solutionName = "xcode"

  if dotest:
    dorelease = dotest

  for arch in archs:
    buildtype = "build"
    outdirname = g_outdirname
    if len(archs) > 1:
      outdirname += arch
    outdir = os.path.abspath(os.path.join(module_path(), outdirname))
    args = ["-DCMAKE_INSTALL_PREFIX=" + outdir]
    for a in extraargs:
      args.append(a)

    args.append("-DPRODUCT_VERSION=" + productversion)

    if dotest:
      args.append("-DDEBUG_CONSOLE=1")

    if dodevelop:
      args.append("-DDEBUG_CONSOLE=1")
      if not serverOnly:
        devtools.buildCmake(devtools.rootDir, devtools.rootDir, args, arch, buildtype, None, True, True, False)
      devtools.buildCmake(devtools.rootDir, devtools.rootDir, args, arch, buildtype, None, True, True, True)

    if dorelease:
      args.append("-DGIT_DESCRIBE_VERSION=\"" + gitDescribe() + "\"")
      buildtype = "Release"
      if not serverOnly:
        devtools.buildCmake(devtools.rootDir, devtools.rootDir, args, arch, buildtype, solutionName, True, True, False, package = True)
      devtools.buildCmake(devtools.rootDir, devtools.rootDir, args, arch, buildtype, solutionName, True, True, True, package = True)

    if ("dproject" in whatbuild):
      ar = arch.lower()
      tmpPath = devtools.getTmpPath(devtools.rootDir, ar, buildtype)
      cefDebug = os.path.join(module_path(), "3rdparty", "cef", "macosx64", "Debug")
      cefRelease = os.path.join(module_path(), "3rdparty", "cef", "macosx64", "Release")
      playerDebug = os.path.join(tmpPath, "Debug", "LiquidSky.app", "Contents", "Frameworks")
      playerRelease = os.path.join(tmpPath, "Release", "LiquidSky.app", "Contents", "Frameworks")
      cfiles = [ { 'name' : "", 'ext' : "", 'path' : playerDebug, 'save_folders' : True } ]
      devtools.findAndCopy(cefDebug, cfiles)
      cfiles = [ { 'name' : "", 'ext' : "", 'path' : playerRelease, 'save_folders' : True } ]
      devtools.findAndCopy(cefRelease, cfiles)

def prepareResources():
  print "Start prepare resources"

  prepareArgs()
  if len(archs) > 1:
    print "Invalid arch"
    exit(-1)

  arch = archs[0]

  installPath3rdparty = devtools.getInstallPath(arch)
  outdir = os.path.abspath(os.path.join(module_path(), g_outdirname))
  linuxsharedlib = os.path.join(outdir, "shared", "usr", "lib", "LiquidSky")
  winplayerlib   = os.path.join(outdir, "player", "lib")
  winstreamer    = os.path.join(outdir, "streamer")
  cfiles = [
    { 'name' : "avcodec",         'ext'  : ".dll", 'path' : winstreamer},
    { 'name' : "avcodec",         'ext'  : ".dll", 'path' : winplayerlib},
    { 'name' : "avformat",        'ext'  : ".dll", 'path' : winstreamer},
    { 'name' : "avformat",        'ext'  : ".dll", 'path' : winplayerlib},
    { 'name' : "avutil",          'ext'  : ".dll", 'path' : winstreamer},
    { 'name' : "avutil",          'ext'  : ".dll", 'path' : winplayerlib},
    { 'name' : "swscale",         'ext'  : ".dll", 'path' : winstreamer},
    { 'name' : "swscale",         'ext'  : ".dll", 'path' : winplayerlib},
    { 'name' : "u2ec",            'ext'  : ".dll", 'path' : winstreamer},
    { 'name' : "CrashSender.",     'ext' : ".exe", 'path' : winstreamer},
    { 'name' : "crashrpt_lang",   'ext' : ".ini", 'path' : winstreamer},
    { 'name' : "app-sender",      'ext' : ".exe", 'path' : winstreamer},
    { 'name' : "process-monitor", 'ext' : ".exe", 'path' : winstreamer},
    { 'name' : "usb-service",     'ext' : ".exe", 'path' : winstreamer},
    { 'name' : "pdb",             'ext' : ".pdb", 'path' : os.path.join(outdir, "pdb")},
  ]
  devtools.findAndCopy(installPath3rdparty, cfiles)

  if arch == "windows-x86_32":
    cefReleaseDir = os.path.join(module_path(), "3rdparty", "cef", "windows32", "Release")
    cfiles = [
      { 'name' : "chrome_elf",         'ext'  : ".dll", 'path' : winplayerlib},
      { 'name' : "d3dcompiler_43",     'ext'  : ".dll", 'path' : winplayerlib},
      { 'name' : "d3dcompiler_47",     'ext'  : ".dll", 'path' : winplayerlib},
      { 'name' : "libcef",             'ext'  : ".dll", 'path' : winplayerlib},
      { 'name' : "widevinecdmadapter", 'ext'  : ".dll", 'path' : winplayerlib},
      { 'name' : "bin",                'ext'  : ".bin", 'path' : winplayerlib },
    ]
    devtools.findAndCopy(cefReleaseDir, cfiles)

    angleReleaseDir = os.path.join(installPath3rdparty, "bin", "angle", "Release")
    cfiles = [
      { 'name' : "angle_util",   'ext'  : ".dll", 'path' : winplayerlib},
      { 'name' : "libEGL",       'ext'  : ".dll", 'path' : winplayerlib},
      { 'name' : "libGLESv1_CM", 'ext'  : ".dll", 'path' : winplayerlib},
      { 'name' : "libGLESv2",    'ext'  : ".dll", 'path' : winplayerlib},
    ]
    devtools.findAndCopy(angleReleaseDir, cfiles)

    cefResourcesDir = os.path.join(module_path(), "3rdparty", "cef", "windows32", "Resources")
    cfiles = [
      { 'name' : "", 'ext' : "", 'path' : winplayerlib, 'save_folders' : True },
    ]
    devtools.findAndCopy(cefResourcesDir, cfiles)

    imagesDir = os.path.join(module_path(), "testdata", "images")
    cfiles = [
      { 'name' : "", 'ext' : "png", 'path' : os.path.join(winplayerlib, "images"), 'save_folders' : True },
    ]
    devtools.findAndCopy(imagesDir, cfiles)

    usbDriverDir = os.path.join(module_path(), "3rdparty", "u2ec")
    cfiles = [
      { 'name' : "usb_driver", 'ext' : "msi", 'path' : winplayerlib},
    ]
    devtools.findAndCopy(usbDriverDir, cfiles)
 
#+      copytree(os.path.join(module_path(), "testdata", "localhost"), os.path.join(outdir, "player", "localhost"))

  if "wind" in pfm:
    cfiles = [
       { 'name' : "pdb",  'ext' : ".pdb", 'path' : os.path.join(outdir, "pdb")},
    ]
    buildtype = "Release"
    buildPath = devtools.getTmpPath(devtools.rootDir, arch, buildtype)
    devtools.findAndCopy(buildPath, cfiles)
    devtools.findAndCopy(buildPath + "-8", cfiles)

  print "Resources were successfully copied"

#  print "not include pack for now TODO: build bot option"
  if "wind" in pfm:
    outputResourceFile = os.path.join(winplayerlib, "localhost.pack")

  if "dar" in pfm:
    outputResourceFile = os.path.join(outdir, "LiquidSky.app", "Contents", "Resources", "localhost.pack")

  respack.packFolder(outputResourceFile, os.path.join(module_path(), "testdata", "localhost_devel", "localhost"), "localhost")
  print "Pack file created"    

def sign(password):
  devtools.signFile(os.path.join(module_path(), "buildproject", "player", "LiquidSkyClient.exe"), os.path.join(expanduser("~"), ".cert", "client_cert.pfx"), password)
  #devtools.signFile(os.path.join(module_path(), "buildproject", "player", "quickreset.exe"), os.path.join(expanduser("~"), ".cert", "client_cert.pfx"), password)

  dlls = [
    "logging.dll",
    "LiquidSky.exe"
    "render-ffmpeg.dll",
    "UsbHelper.exe"
    "render-ffmpeg-hw.exe"
    "avcodec-57.dll",
    "avformat-57.dll",
    "avutil-55.dll",
    "swscale-4.dll",
    "angle_util.dll", 
    "libEGL.dll",     
    "libGLESv1_CM.dll",
    "libGLESv2.dll",  
  ]

  for d in dlls:
    devtools.signFile(os.path.join(module_path(), "buildproject", "player", "lib", d), os.path.join(expanduser("~"), ".cert", "client_cert.pfx"), password)

  dlls = [
    "avcodec-57.dll",
    "avformat-57.dll",
    "avutil-55.dll",
    "swscale-4.dll",
    "osk.exe", 
    "osk-monitor.exe",
    "streamer.exe",
    "streamer-service.exe",
    "CrashSender.exe",
    "vmhelper.dll",
    "logging.dll",
    "storagetool.exe",
    "setuptool.exe",
    "changelang.exe",
    "app-sender.exe",
    "process-monitor.exe",
    "usb-service.exe",
  ]

  for d in dlls:
    devtools.signFile(os.path.join(module_path(), "buildproject", "streamer", d), os.path.join(expanduser("~"), ".cert", "client_cert.pfx"), password)

def dist(version):
  releaseDirPath = os.path.join(module_path(), "buildproject")
  zipPath = os.path.join(module_path(), "buildproject-zip")

  def CreateIfNotExists(directory):
    if not os.path.exists(directory):
      os.makedirs(directory)

  CreateIfNotExists(zipPath)

  if "wind" in pfm:
    streamerDir = os.path.join(releaseDirPath, "streamer")
    playerDir   = os.path.join(releaseDirPath, "player")
    pdbDir      = os.path.join(releaseDirPath, "pdb")

    zipcmd = [sevenz.cmd, "a", os.path.abspath(os.path.join(zipPath, version + "-player")) + ".7z", os.path.abspath(playerDir)]
    proc = subprocess.call(zipcmd)

    zipcmd = [sevenz.cmd, "a", os.path.abspath(os.path.join(zipPath, version + "-streamer")) + ".7z", os.path.abspath(streamerDir)]
    proc = subprocess.call(zipcmd)

    zipcmd = [sevenz.cmd, "a", os.path.abspath(os.path.join(zipPath, version + "-pdb")) + ".7z", os.path.abspath(pdbDir)]
    proc = subprocess.call(zipcmd)

  if "dar" in pfm:
    prepareArgs()
    outfile = os.path.join(zipPath, version + "-" + "LiquidSkyClient.dmg")
    for arch in archs:
      buildtype = "Release"
      devtools.buildMacOsPackage(devtools.rootDir, arch, buildtype, outfile)

def getBranchIniPath():
  outdir = os.path.abspath(os.path.join(module_path(), g_outdirname))    
  outdir = os.path.join(outdir, "player/lib/branch.ini")
  return outdir

def createBranchIni(uiurl):
  print "Adding additional parameters in branch.ini..."
  cfgPath = getBranchIniPath()
  cfgParser = ConfigParser.ConfigParser()
  cfgParser.read(cfgPath)
  if not cfgParser.has_section("General"):
    cfgParser.add_section("General")
  cfgParser.set("General", "UiUrl", uiurl)
  with open(cfgPath, "w") as config_file:
    cfgParser.write(config_file)

def clearBranchIni():
  cfgPath = getBranchIniPath()
  if os.path.exists(cfgPath):
    os.remove(cfgPath)

parser = argparse.ArgumentParser(description='build tool')
parser.add_argument('--clean', required=False, action='store_true', help="clean build results")
parser.add_argument('--3rdparty', nargs="*", required=False, dest='rdparty', help="build 3rdparty libs")
parser.add_argument('--merge', required=False, action='store_true', help="merge x86 and x86_64 binaries (macos only)")
parser.add_argument('--project', required=False, action='store_true', help="build project")
parser.add_argument('--server-only', required=False, action='store_true', help="only build server")
parser.add_argument('--dproject', required=False, action='store_true', help="build Xcode project")
parser.add_argument('--debug', required=False, action='store_true', help="build project debug")
parser.add_argument('--test', required=False, action='store_true', help="build project with console (windows only)")
parser.add_argument('--resources', required=False, action='store_true', help="copy resources")
parser.add_argument('--sign', required=False, action='store_true', help="sign binaries (windows only)")
parser.add_argument('--dist', required=False, action='store_true', help="zip binaries (windows only)")
parser.add_argument('--version', required=False, default=time.strftime("%Y%m%d-%H%M%S"), help="version for zip or deb packages")
parser.add_argument('--brand', required=False, default="game", help="product version, one of following values: game, cast")
parser.add_argument('--start_page', required=False, default="", help="UiUrl parameter of config.ini for player build, works only with 'project' parameter")
parser.add_argument('--clear_branch', required=False, default="", help="Delete branch.ini as additional config")

args = parser.parse_args()

if args.clean:
  clean()

if args.rdparty != None:
  libs = args.rdparty
  if len(libs) == 0:
    libs = ["all"]
  build3rdparty(libs, args.server_only)

if args.project or args.test or args.debug or args.dproject:
  params = list()
  if not args.debug:
    params.append("release")
  else:
    params.append("debug")

  if args.test:
    params.append("test")

  if args.dproject:
    params.append("dproject")

  buildproject(params, args.brand, args.server_only)

if args.resources:
  prepareResources()

if args.sign:
  passwordfilename = os.path.join(expanduser("~"), ".cert", "password")
  password = ""
  with open(passwordfilename) as f:
    lines = f.readlines()
    if len(lines) > 0:
      password = lines[0]
      password = password.rstrip('\n')

  sign(password)

if args.dist:
  dist(args.version)

if args.start_page:
  createBranchIni(args.start_page)

if args.clear_branch:
  clearBranchIni()
