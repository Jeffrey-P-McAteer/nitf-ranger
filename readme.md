
# NITF Ranger

Small c# experiment to download fragments of a NITF file given
WGS84 bounding box coordinates.


# Run

```bash
dotnet run

```

# Misc Experiments

```bash
gdalwarp -overwrite -to SRC_METHOD=NO_GEOTRANSFORM -te 0.0 0.0 2048.0 2048.0 /vsicurl/http://download.osgeo.org/pub/gdal/data/nitf/u_3054a.ntf /tmp/out.tif

git clone https://github.com/mdaus/nitro.git


```

