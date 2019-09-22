'''
Created on 21 Sep 2019

@author: Tyler

Output all images required for all tiles
'''

import glob
import os
import re

from all_for_one_tile import *

# Find all the tiles to process!
geometriesFilter = os.path.join("geometries", "geo-*.geojson")
geometriesList   = glob.glob(geometriesFilter)

for i in range(len(geometriesList)):
    parts = re.split("x|y|-|\.", geometriesList[i])
    tile_x = parts[2]
    tile_y = parts[4]
    
    print("Doing everything for " + tile_x + ", " + tile_y);
    
    all_for_one_tile(tile_x=tile_x, tile_y=tile_y)
    