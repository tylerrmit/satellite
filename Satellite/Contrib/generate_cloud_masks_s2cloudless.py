'''
Created on 27 Aug 2019

@author: Tyler
'''

import glob
import os

from sentinel.tilesnapshot import tilesnapshot

tile_x    = 7680
tile_y    = 10240
size_x    = 512
size_y    = 512
threshold = 0.7    # Minimum probability of cloud, for a pixel to be masked

# Base location for data     
basePath = "data\\sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y"

# List available snapshots
timeSeriesFilter = basePath + "\\timeseries\\" + str(tile_x) + "-" + str(tile_y) + "-B01-*.png"
timeSeriesList   = glob.glob(timeSeriesFilter)

# Process each snapshot
for i in range(len(timeSeriesList)):
    print("Processing [" + timeSeriesList[i].replace('B01', '*') + "]")
    
    # Find the actual filename part of the path
    baseName  = os.path.basename(timeSeriesList[i])
    # Find the dateStr (YYYY-MM-DD)
    dateStart = len(str(tile_x)) + len(str(tile_y)) + 6
    dateEnd   = dateStart + 10
    dateStr   = baseName[dateStart:dateEnd]
    
    # Load the snapshot and generate clouds with specified threshold
    t = tilesnapshot(tile_x, tile_y, dateStr, size_x, size_y)
    t.detectClouds(threshold)

print("Finished!")