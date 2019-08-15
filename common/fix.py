from PIL import Image
import os
import sys
fn = "input_hover.png"

im = Image.open(fn)

sx = im.size[0]
sy = im.size[1]

x = sx - 1;
while x > 30:
  x = x - 1
  for y in range(0, sy):
    im.putpixel((x + 1, y), im.getpixel((x, y)))

im.save(fn + ".png")
