from PIL import Image
import os
import sys

fn = "hover"

im = Image.open(fn + ".png")

sx = im.size[0]
sy = im.size[1]

newImage = Image.new("RGBA", (sx + 2, sy + 2))
newImage.paste(im, (1,1))
sxn = sx + 2
syn = sy + 2

if False:
  for x in range(0, sxn):
    newImage.putpixel((x, 0), newImage.getpixel((x, 1)))
    newImage.putpixel((x, syn - 1), newImage.getpixel((x, syn - 2)))

  for y in range(0, sy):
    newImage.putpixel((0, y), newImage.getpixel((1, y)))
    newImage.putpixel((sxn - 1, y), newImage.getpixel((sxn - 2, y)))
else:
  pixel = (0,0,0,0)
  for x in range(0, sxn):
    newImage.putpixel((x, 0), pixel)
    newImage.putpixel((x, syn - 1), pixel)

  for y in range(0, sy):
    newImage.putpixel((0, y), pixel)
    newImage.putpixel((sxn - 1, y), pixel)


newImage.save(fn + ".png")
