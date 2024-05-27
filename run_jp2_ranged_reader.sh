#!/bin/bash

set -e

gcc \
  -Wall -Werror \
  -Wno-unused-variable \
  -Wno-unused-but-set-variable \
  -g jp2_ranged_reader.c \
  -o jp2_ranged_reader

([ -e astronaut.jp2 ] || python glymur-create.py)

echo
echo "====== astronaut.jp2 ======"
./jp2_ranged_reader astronaut.jp2 768 768 512 512

echo
echo "====== astronaut.grey.jp2 ======"
./jp2_ranged_reader astronaut.grey.jp2 768 768 512 512
