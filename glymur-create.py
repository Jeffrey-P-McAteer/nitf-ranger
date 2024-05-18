
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

jp2 = glymur.Jp2k('astronaut.jp2')
astronaut = skimage.data.astronaut()
print(f'astronaut = {astronaut}')

big_picture = []
for i in range(0, 2):
  for row_i, row in enumerate(astronaut):
    if len(big_picture) <= row_i:
      big_picture.append([])
    for col_i, col_val in enumerate(row):
      big_picture[row_i].append(astronaut[row_i][col_i])

print(f'big_picture = {len(big_picture)}x{len(big_picture[0])}')

#jp2[:] = astronaut
jp2[:] = numpy.array(big_picture)



