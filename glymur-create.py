
import os
import sys
import subprocess
import struct

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

#print(f'glymur = {glymur}')
#j2kfile = glymur.data.goodstuff()
#print(f'j2kfile = {j2kfile}')
#j2k = glymur.Jp2k(j2kfile)
#print(f'j2k = {j2k}')

astronaut = skimage.data.astronaut()
# print(f'astronaut = {astronaut}')
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

  print(f'final_img size = {len(final_img)}x{len(final_img[0])}')

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

print(f'Reading the rectangle from {x0},{y0} -> {x1},{y1} ({w}x{h} pixels)')

out_pixels = numpy.zeros((w, h, 3), dtype=numpy.uint8)
with open('astronaut.jp2', 'rb') as fd:
  jp2_file_len = os.fstat(fd.fileno()).st_size

  # Ref: https://www.file-recovery.com/jp2-signature-format.htm
  # Ref: https://jpylyzer.openpreservation.org/doc/2-2/userManual.html#structure-jp2
  # Ref: https://github.com/quintusdias/glymur/blob/cb25720ab369da3151e0a3855c7580b779878c40/tests/data/nemo.txt#L6
  # Ref: https://gist.github.com/espresso3389/a4a7ffcc28cbd15dce61a5f45a94c3bf
  # Ref: https://vicente-gonzalez-ruiz.github.io/JPEG2000/
  # Ref: https://web.archive.org/web/20090419051120/http://www.upatras.gr/ieee/skodras/pubs/ans-c36.pdf

  # Read first chunk length (big-endian, 4 bytes)
  fd.seek(0)
  c1_len = struct.unpack('>I', fd.read(4))[0]
  c1_type = b''.join(struct.unpack('cccc', fd.read(4))).decode('utf-8')
  print(f'c1_len = {c1_len}, c1_type = {c1_type}')

  # Seek past any remaining bytes in chunk 1; seek's argument is ALWAYS offset from pos 0
  fd.seek(c1_len)
  c2_len = struct.unpack('>I', fd.read(4))[0]
  c2_type = b''.join(struct.unpack('cccc', fd.read(4))).decode('utf-8')
  print(f'c2_len = {c2_len}, c2_type = {c2_type}')

  if c2_type == 'ftyp':
    # Parse sub-type at offset 8
    c2_sub_type = b''.join(struct.unpack('cccc', fd.read(4))).decode('utf-8')
    print(f'  c2_sub_type = {c2_sub_type}')
    c2_sub_type_unk_num = struct.unpack('>I', fd.read(4))[0]
    print(f'  c2_sub_type_unk_num = {c2_sub_type_unk_num}')


  fd.seek(c1_len + c2_len)
  c3_len = struct.unpack('>I', fd.read(4))[0]
  c3_type = b''.join(struct.unpack('cccc', fd.read(4))).decode('utf-8')
  print(f'c3_len = {c3_len}, c3_type = {c3_type}')

  # Parse jp2h sub-boxes out
  if c3_type == 'jp2h':
    jp2h_offset = 0
    while jp2h_offset < c3_len:
      jp2h_box_len = struct.unpack('>I', fd.read(4))[0]
      jp2h_offset += 4
      jp2h_box_type = b''.join(struct.unpack('cccc', fd.read(4))).decode('utf-8')
      jp2h_offset += 4
      print(f'  jp2h_box_len = {jp2h_box_len}, jp2h_box_type = {jp2h_box_type}')
      if jp2h_box_type == 'ihdr':
        ihdr_width = struct.unpack('>I', fd.read(4))[0]
        ihdr_height = struct.unpack('>I', fd.read(4))[0]
        ihdr_color_channels = struct.unpack('>H', fd.read(2))[0]
        print(f'    ihdr_width = {ihdr_width}, ihdr_height = {ihdr_height}, ihdr_color_channels = {ihdr_color_channels}')

        ihdr_bit_depth = struct.unpack('>B', fd.read(1))[0]
        print(f'    ihdr_bit_depth = {ihdr_bit_depth}, ')



      elif jp2h_box_type == 'colr':
        pass
      # Ensure we seek to next box, no matter what the variable size of this box was
      if jp2h_box_len-8 > 0:
        jp2h_offset += jp2h_box_len
        fd.seek(c1_len + c2_len + jp2h_offset)



  fd.seek(c1_len + c2_len + c3_len)
  c4_len = struct.unpack('>I', fd.read(4))[0]
  c4_type = b''.join(struct.unpack('cccc', fd.read(4))).decode('utf-8')
  print(f'c4_len = {c4_len}, c4_type = {c4_type}')
  if c4_type == 'jp2c':
    # Begin parsing code-stream!
    pass


  fd.seek(c1_len + c2_len + c3_len + c4_len)
  if fd.tell() < jp2_file_len:
    c5_len = struct.unpack('>I', fd.read(4))[0]
    c5_type = b''.join(struct.unpack('cccc', fd.read(4))).decode('utf-8')
    print(f'c5_len = {c5_len}, c5_type = {c5_type}')



if 'display' in sys.argv:
  matplotlib.pyplot.imshow(out_pixels, interpolation='nearest')
  matplotlib.pyplot.show()
else:
  print('pass "display" as arg to show de-coded bounding box pixels using pyplot')


