'''
Created on 04 Oct 2019

@author: Tyler

Output GNVDI images for all tiles
'''

import glob
import os
import re

from generate_gnvdi_sticky import *

# Find all the tiles to process!
geometriesFilter = os.path.join("geometries", "geo-*.geojson")
geometriesList   = glob.glob(geometriesFilter)

for i in range(len(geometriesList)):
    parts = re.split("x|y|-|\.", geometriesList[i])
    tile_x = parts[2]
    tile_y = parts[4]
    
    if tile_x == '6144' or tile_x == '6656' or tile_x == '7168' or tile_x == '7680' or tile_x == '8192' or tile_x == '8704' or tile_x == '9216' or tile_x == '9728' or tile_x == '10240':
        print("Doing everything for " + tile_x + ", " + tile_y);
    
        generate_gnvdi_sticky(tile_x=tile_x, tile_y=tile_y)
    