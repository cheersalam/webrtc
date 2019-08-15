import os
import sys
import subprocess

def we_are_frozen():
    return hasattr(sys, "frozen")

def module_path():
    encoding = sys.getfilesystemencoding()
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, encoding))
    return os.path.dirname(unicode(__file__, encoding))


for subdir, dirs, files in os.walk(module_path()):
    for file in files:
        if ".dmp" in file:
            uuid = os.path.basename(subdir)
            dmp = os.path.join(subdir, file)
            outfile = open(uuid + ".analyse", "w")
            cmd = ["C:\\Program Files (x86)\\Windows Kits\\8.1\\Debuggers\\x86\\cdb.exe",
                   "-z",
                   dmp,
                   "-c",
                   '!analyze -v; q']
            print cmd
            proc = subprocess.call(cmd, env=os.environ.copy(), stdout=outfile)




