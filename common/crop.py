from PIL import Image
import os
import sys
fn = "overlay.png"

im = Image.open(fn)

im2 = im.crop((4,4,8,8))
im2.save(fn + ".png")
