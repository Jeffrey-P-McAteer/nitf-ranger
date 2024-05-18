
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
jp2[:] = skimage.data.astronaut()





