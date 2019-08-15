import zlib
import sys

for filename in sys.argv:
    if filename == sys.argv[0]:
        continue

    print ("****** Uncompressing " + filename + " ******")
    try:
        with open(filename, 'rb') as compressed:
            data = zlib.decompress(compressed.read())
            print data
    except:
        print(filename + " is not valid")
