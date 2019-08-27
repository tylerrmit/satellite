'''
Created on 27 Aug 2019

@author: Tyler
'''

import glob
import os

from PIL import Image
from sentinel.tilesnapshot import tilesnapshot

tile_x    = 7680
tile_y    = 10240
threshold = 0.7    # Minimum probability of cloud for a pixel to be masked
        
basePath = "data\\sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y"

# List available snapshots
timeSeriesFilter = basePath + "\\timeseries\\" + str(tile_x) + "-" + str(tile_y) + "-B01-*.png"
timeSeriesList   = glob.glob(timeSeriesFilter)

for i in range(len(timeSeriesList)):
    print("Building Cloud Mask [" + str(i) + "] [" + timeSeriesList[i] + "]")
    
    # Find the actual filename part of the path
    baseName  = os.path.basename(timeSeriesList[i])
    # Find the dateStr (YYYY-MM-DD)
    dateStart = len(str(tile_x)) + len(str(tile_y)) + 6
    dateEnd   = dateStart + 10
    dateStr   = baseName[dateStart:dateEnd]
    
    # Load the snapshot and generate clouds with specified threshold
    t = tilesnapshot(tile_x, tile_y, dateStr, threshold)
    
    save_location = "data\\sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y\\Masks\\cloud_masks"
    os.makedirs(save_location, exist_ok=True)
    
    img = Image.new('RGBA', (512, 512), color = 'black')

    for x in range(512):
        for y in range(512):
            if (t.cloud_masks[0][y][x] > 0):
                img.putpixel((x, y), (0,0,0,0))
            else:
                img.putpixel((x, y), (0,0,0,255))
        
    img.save(save_location + "\\" + dateStr + ".png")
