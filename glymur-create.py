
import os
import sys
import subprocess

pyenv = os.path.join(os.path.dirname(__file__), 'pyenv')
os.makedirs(pyenv, exist_ok=True)
sys.path.append(pyenv)


try:
  import glymur
except:
  subprocess.run([
    sys.executable, *('-m pip install glymur'.split()), f'--target={pyenv}'
  ])
  import glymur


try:
  import numpy
except:
  subprocess.run([
    sys.executable, *('-m pip install numpy'.split()), f'--target={pyenv}'
  ])
  import numpy


try:
  import matplotlib
except:
  subprocess.run([
    sys.executable, *('-m pip install matplotlib'.split()), f'--target={pyenv}'
  ])
  import matplotlib

import matplotlib.pyplot

try:
  import skimage
except:
  subprocess.run([
    sys.executable, *('-m pip install scikit-image'.split()), f'--target={pyenv}'
  ])
  import skimage

import skimage.data

print(f'glymur = {glymur}')
j2kfile = glymur.data.goodstuff()
print(f'j2kfile = {j2kfile}')
j2k = glymur.Jp2k(j2kfile)
print(f'j2k = {j2k}')

astronaut = skimage.data.astronaut()
print(f'astronaut = {astronaut}')
x_count = 4
y_count = 4


if not os.path.exists('astronaut.jp2'):
  jp2 = glymur.Jp2k('astronaut.jp2')
  final_img = numpy.zeros(((x_count * len(astronaut[0])) + 1 , (y_count * len(astronaut)) + 1, 3 ), dtype=numpy.uint8)

  for y in range(0, len(final_img)):
    for x in range(0, len(final_img[0])):
      final_img[y][x] = (
        numpy.uint8(255.0 * (y / len(final_img)) ),
        numpy.uint8(255.0 * (x / len(final_img)) ),
        128
      )

  for i in range(0, min(x_count, y_count)):
    for row_i, row in enumerate(astronaut):
      for col_i, col_val in enumerate(row):
        final_img[row_i + (i * len(astronaut)) ][col_i + (i * len(astronaut[0])) ] = astronaut[row_i][col_i]

  print(f'final_img = {len(final_img)}x{len(final_img[0])}')

  #jp2[:] = astronaut
  jp2[:] = final_img

  jp2 = None


# Ok, now we parse this code-stream but only to x0..x1,y0..y1
x0 = int( ((x_count * len(astronaut[0])) / 2.0) - (len(astronaut[0]) / 2.0) )
y0 = int( ((y_count * len(astronaut)) / 2.0) - (len(astronaut) / 2.0) )
x1 = int( ((x_count * len(astronaut[0])) / 2.0) + (len(astronaut[0]) / 2.0) )
y1 = int( ((y_count * len(astronaut)) / 2.0) + (len(astronaut) / 2.0) )
w = int(x1 - x0)
h = int(y1 - y0)

out_pixels = numpy.zeros((w, h, 3), dtype=numpy.uint8)
with open('astronaut.jp2', 'rb') as fd:
  pass


matplotlib.pyplot.imshow(out_pixels, interpolation='nearest')
matplotlib.pyplot.show()
