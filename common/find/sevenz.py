name = "7-Zip"
helpMessage = "Please download and install it http://www.7-zip.org/download.html"

import platform

platformStr = platform.system().lower()

if "windows" in platformStr:
  exe = "7z.exe"
  paths = [
    "C:\\Program Files\\7-Zip\\",
    "C:\\Program Files (x86)\\7-Zip\\"
    ]
elif "linux" in platformStr:
  exe = "7zr"
  paths = [
    "/bin/",
    "/usr/bin/",
    "/usr/local/bin/"
  ]
elif "darwin" in platformStr:
  exe = "7z"
  paths = [
    "/bin/",
    "/usr/bin/",
    "/usr/local/bin/"
  ]

