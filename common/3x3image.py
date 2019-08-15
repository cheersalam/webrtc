from PIL import Image
import os
import sys

def process(fn, fnout, midle, edges):
  im = Image.open(fn)

  w = im.size[0]
  h = im.size[1]

  x1 = 0
  x2 = edges
  x3 = x2 + midle

  x4 = w - edges
  x5 = w

  y1 = 0
  y2 = edges
  y3 = y2 + midle

  y4 = h - edges
  y5 = h

  prefixes = {
  "00" : (x1, y1, x2, y2),
  "01" : (x2, y1, x3, y2),
  "02" : (x4, y1, x5, y2),
  "10" : (x1, y2, x2, y3),
  "11" : (x2, y2, x3, y3),
  "12" : (x4, y2, x5, y3),
  "20" : (x1, y4, x2, y5),
  "21" : (x2, y4, x3, y5),
  "22" : (x4, y4, x5, y5),
  }

  for n, q in prefixes.iteritems():
    im2 = im.crop(q)
    im2.save(fnout + "_" + n + ".png")

fn = "btn_clicked.png"
fnout = "click"

process("white_btn_click.png", "click", 4, 10)
process("white_btn_idle.png", "idle", 4, 10)
process("white_btn_hover.png", "hover", 4, 10)