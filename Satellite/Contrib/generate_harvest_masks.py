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
#threshold = 0.32    # Green proportion of pixel intensity less than this value looks "harvested"
threshold = 0.33

#cloudMask = 'CrudeCloudMask'
cloudMask = 'CloudMask'

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
    
    # Load the Cloud Mask - s2cloudless
    t.loadCloudMask()
    
    # Load the Cloud Mask - crude
    t.loadCrudeCloudMask()
    
    # Create new mask
    img = Image.new('RGBA', (size_x, size_y))
    
    sugar_count   = 0
    cloud_count   = 0
    harvest_count = 0
    other_count   = 0
    
    # Offset the Sugar Mask which is mis-aligned
    y_offset = 50
    x_offset = 5
            
    for y in range(size_y):
        for x in range(size_x):
            # Yes I think the supplied Sugar Mask has its alpha backwards and I stubbornly refuse to do the same with the Cloud Mask

            red   = t.layers['TCI'][y,x][0]
            green = t.layers['TCI'][y,x][1]
            blue  = t.layers['TCI'][y,x][2]
                
            channelPortion = (green/(green+red+blue))
            
            if (t.layers[cloudMask][y,x]==(0, 0, 0, 255)):
                cloud_count += 1
                img.putpixel((y, x), (255, 255, 0, 255))
            elif ((x+x_offset < size_x) and (y+y_offset < size_y) and (t.layers['SugarMask'][y+y_offset,x+x_offset,] != (0, 0, 0, 255))):
                sugar_count += 1
                img.putpixel((y, x), (0, 0, 0, 128))
            elif ((x+x_offset >= size_x) or (y+y_offset >= size_y)):
                sugar_count += 1
                img.putpixel((y, x), (0, 0, 0, 128))
            elif (channelPortion < threshold):
                harvest_count += 1
                img.putpixel((y, x), (255, 0, 0, 255))
            else:
                other_count += 1
                img.putpixel((y, x), (red, green, blue, 255))
    
    output_file = save_location + "\\" + dateStr + ".png"
    print("Writing [" + output_file + "] Sugar: " + str(sugar_count) + " Cloud: " + str(cloud_count) + " Harvest: " + str(harvest_count) + " Other: " + str(other_count))
    img.save(output_file)
    
print("Finished!")