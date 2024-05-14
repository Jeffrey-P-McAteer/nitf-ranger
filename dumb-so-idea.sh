#!/bin/bash

set -e

mkdir -p data

X1=0
Y1=0
X2=30
Y2=30
Z=5
for x in `seq $X1 $X2`; do
  for y in `seq $Y1 $Y2`; do
    if ! [[ -e "data/${Z}_${y}_${x}.png" ]] ; then
      echo "Getting ${x},${y}"
      curl -s "https://tile.openstreetmap.org/${Z}/${x}/${y}.png" -o "data/${Z}_${y}_${x}.png"
    else
      echo "Already-exists ${x},${y}"
    fi
  done
done

montage -mode concatenate -tile "$((X2-X1+1))x" data/"${Z}_*.png" "data/out_z${Z}_${X1}_${Y1}-${X2}_${Y2}.png"

echo "See data/out_z${Z}_${X1}_${Y1}-${X2}_${Y2}.png "

ls -alh "data/out_z${Z}_${X1}_${Y1}-${X2}_${Y2}.png"

feh "data/out_z${Z}_${X1}_${Y1}-${X2}_${Y2}.png"



