#!/usr/bin/env python
#Resource pack/unpack format:

#2 byte max path
#4 byte number of resources

#Resource entry:
#4 byte resource offset in file
#MAX_PATH byte source path

#End entry
#4 byte end of file

#Resource:
#N bytes source file bytes

import re
import time
import argparse
import os 
import struct
import fnmatch
from itertools import cycle, izip


#need to change the key in utils/res-pack.cpp also
KEY = 'a7OQ6pxCbfjxAy@tk2b~Ex?7ZB%OnCIm3Uj64cc5v3Q?rFr#sea7OQ6pxCbfjxAybKZfo21LFHnwyV6qCP*UFI1?0nxvezS$q3k9FEXWvf?jGnL1loa7OQ6pxsdinnNy7iAucRXqC3m~fQj?s'
MAX_PATH = 255
HEADER_LENGTH = 2 + 4
ENTRY_SIZE = MAX_PATH + 4
OFFSET_SIZE = 4

def xor_string_impl(data, key):
  return ''.join(chr(ord(c)^ord(k)) for c,k in izip(data, cycle(key)))

def xor_string(data, key, offset=0):
  if offset != 0:
    newKey = key[offset:]
    newKey += key[:offset]
  else:
    newKey = key

  return xor_string_impl(data, newKey)


def packResources(root, files, outfile, prefix):
  data = {}
  content = []

  # Write file header
  content.append(struct.pack('<HI', MAX_PATH, len(files)))

  # entries count * entry size + last offset size
  index_length = len(files) * ENTRY_SIZE + OFFSET_SIZE

  # Write index.
  data_offset = HEADER_LENGTH + index_length
  for f in files:
    filepath = prefix + "/" + os.path.relpath(f, root).replace(os.path.sep, '/')
    print "read file: " + filepath

    with open(f, 'rb') as file:
      data[f] = file.read()

    content.append(struct.pack('<I' + str(MAX_PATH) + 's', data_offset, str(filepath)))
    data_offset += len(data[f])

  print "write index"
  content.append(struct.pack('<I', data_offset))

  # Write data
  for f in files:
    content.append(data[f])

  # Write file
  print "write file: " + outfile
  with open(outfile, 'wb') as file:
    start = time.time()
    file.write(xor_string(''.join(content), KEY))
    end = time.time()
    print "spent: " + str(end - start)

def getFolderFiles(folder):
  files = []

  for root, subdirs, fs in os.walk(folder):
    for f in fs:
      filepath = os.path.join(root, f)
      files.append(filepath)
  return files

def filterFiles(folder, flist):
  rules = []
  ignoreFile = os.path.join(folder, ".packignore")
  if os.path.isfile(ignoreFile):
    with open(ignoreFile, "r") as f:
      for line in f:
        cleanedLine = line.strip()
        if cleanedLine:
          rules.append(cleanedLine)
  matched = []
  for f in flist:
    relPath = os.path.relpath(f, folder)
    relPath = relPath.replace(os.path.sep, '/')
    l = [relPath]
    for r in rules:
      m = fnmatch.filter(l, r)
      matched.extend(m)
  matched = set(matched)

  for m in matched:
    print "ignore: " + m
  result = [x for x in flist if os.path.relpath(x, folder).replace(os.path.sep, '/') not in matched]
  return result

def packFolder(outfile, folder, prefix):
  root = os.path.abspath(folder)
  files = getFolderFiles(root)
  filtered = filterFiles(root, files)
  packResources(root, filtered, outfile, prefix)
    
def unpackResources(infile):
  resources = {}
  # Read file
  file = open(infile, 'rb')
  if not file:
    return resources
  
  content = xor_string(file.read(), KEY)
  original_content = content

  # Read file header
  maxPath, num_entries = struct.unpack('<HI', content[:HEADER_LENGTH])

  # Read data
  if num_entries == 0:
    return resources

  content = content[HEADER_LENGTH:]
  kIndexEntrySize = maxPath + 4
  for _ in range(num_entries):
    offset, source = struct.unpack('<I' + str(maxPath) + 's', content[:kIndexEntrySize])
    content = content[kIndexEntrySize:]
    next_offset = struct.unpack('<I', content[:OFFSET_SIZE])[0]
    source = source.strip('\0')
    resources[source] = original_content[offset:next_offset]
    print "read file: " + source
  return resources
  
def unpackResouce(infile, insource):
  resource = {}
  # Read file
  file = open(infile, 'rb')
  if not file:
    return resources

  header = file.read(HEADER_LENGTH)
  header = xor_string(header, KEY)
  
  # Read file header
  maxPath, num_entries = struct.unpack('<HI', header)
  
  # entries count * entry size + last offset size
  index_length = num_entries * ENTRY_SIZE + OFFSET_SIZE
  entriesArray = xor_string(file.read(index_length), KEY, HEADER_LENGTH)
  print entriesArray
  for _ in range(num_entries):
    offset, source = struct.unpack('<I' + str(MAX_PATH) + 's', entriesArray[:ENTRY_SIZE])
    entriesArray = entriesArray[ENTRY_SIZE:]
    source = source.strip('\0')
    if source == insource:
      next_offset = struct.unpack('<I', entriesArray[:OFFSET_SIZE])[0]
      file.seek(offset)
      resource[source] = xor_string(file.read(next_offset - offset), KEY, offset)
      break
  return resource

def createFiles(resources, outfolder):
  paths = resources.keys()
  for path in paths:
    outfile = os.path.join(outfolder, path)
    outdir = os.path.dirname(outfile)
    if not os.path.exists(outdir):
      os.makedirs(outdir)
    with open(outfile, 'wb') as file:
      file.write(''.join(resources[path]))
  
def unpackFile(infile, outfolder, sourcefile):
  sourcefile = sourcefile.replace(os.path.sep, '/') 
  resource = unpackResouce(infile, sourcefile)
  createFiles(resource, outfolder)
  return resource
  
def unpackFolder(infile, outfolder):  
  resources = unpackResources(infile)
  createFiles(resources, outfolder)
  
def main():
  parser = argparse.ArgumentParser(description='pack/unpack resource folder')
  parser.add_argument('--pack', nargs=3, required=False, help="file.pack infolder")
  parser.add_argument('--unpack', nargs='+', required=False, help="file.pack outfolder [sourcename]")
  args = parser.parse_args()

  if args.pack:
    if len(args.pack) == 3:
      packFolder(args.pack[0], args.pack[1], args.pack[2])

  if args.unpack:
    if len(args.unpack) == 3:
      unpackFile(args.unpack[0], args.unpack[1], args.unpack[2])
      return;
      
    if len(args.unpack) == 2:
      unpackFolder(args.unpack[0], args.unpack[1])
      
    if len(args.unpack) == 1:
      unpackFolder(args.unpack[0], '')

if __name__ == '__main__':
  main()