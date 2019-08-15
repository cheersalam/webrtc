"""
Remove's GNU style curly brackets from files matching glob
"""
from __future__ import print_function

import os
import re
import sys
import glob
import tempfile
import contextlib

GNU_LINE = re.compile(r"^(\s*)(.*?\))\s*\{\s*?([\r\n]*)$", re.M)

IGLOB_NOT_RECURSIVE = (
  "WARNING: glob.iglob doesn't take recursive argument, "
  "** will not expand to multiple directories.  "
  "Use Python 3.5+ if this matters."
)

def main():
  """
  Entry point
  """
  try:
    glob.iglob("", recursive=True)
  except TypeError:
    print(IGLOB_NOT_RECURSIVE)

  pattern = sys.argv[1]
  print(pattern)
  for inputname in glob.iglob(pattern, recursive=True):
    outputfilehandle, outputname = tempfile.mkstemp()
    with contextlib.ExitStack() as stack:
      inputfile = stack.enter_context(open(inputname))
      outputfile = stack.enter_context(os.fdopen(outputfilehandle, "w"))

      for i, line in enumerate(inputfile):
        match = GNU_LINE.match(line)
        if not match:
          outputfile.write(line)
          continue

        indent, code, newline = match.groups()
        print(inputname, i)
        print(line)
        print(indent + code)
        print(indent + "{")
        outputfile.write(indent + code + newline)
        outputfile.write(indent + "{" + newline)
    os.remove(inputname)
    os.rename(outputname, inputname)

if __name__ == "__main__":
  main()
