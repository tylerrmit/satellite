'''
Created on 29 Aug 2019

@author: Tyler
'''

import glob
import os

from PIL import Image

from sentinel.tilesnapshot import tilesnapshot

tile_x    = 7680
tile_y    = 10240
size_x    = 512
size_y    = 512
threshold = 0.32    # Green proportion of pixel intensity less than this value looks "harvested"
     
# Base location for data   
basePath = "data\\sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y"

# Location for output
save_location = "data\\sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y\\Masks\\harvested_masks"
os.makedirs(save_location, exist_ok=True)

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
    
    # Initialise the tilesnapshot
    t = tilesnapshot(tile_x, tile_y, dateStr, size_x, size_y)
    
    # Load the TCI layer
    t.loadLayers(['TCI'])
    
    # Load the Sugar Mask
    t.loadSugarMask()
    
    # Load the Cloud Mask
    t.loadCloudMask()
    
    # Create new mask
    img = Image.new('RGBA', (size_x, size_y))
    
    for y in range(size_y):
        for x in range(size_x):
            # Yes I think the supplied Sugar Mask has its alpha backwards and I stubbornly refuse to do the same with the Cloud Mask
            if ((t.layers['SugarMask'][y,x]==(0, 0, 0, 255)) and (t.layers['CloudMask'][y,x]==(0, 0, 0, 0))):
                red   = t.layers['TCI'][y,x][0]
                green = t.layers['TCI'][y,x][1]
                blue  = t.layers['TCI'][y,x][2]
                
                channelPortion = (green/(green+red+blue))
                
                if (channelPortion < threshold):
                    img.putpixel((x, y), (255,0,0,255))
                else:
                    img.putpixel((x, y), (0,0,0,0))
            else:
                img.putpixel((x, y), (0,0,0,0))
    
    output_file = save_location + "\\" + dateStr + ".png"
    print("Writing [" + output_file + "]")
    img.save(output_file)
    
print("Finished!")