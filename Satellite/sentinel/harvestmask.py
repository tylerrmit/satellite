'''
Created on 17 Sep 2019

@author: Tyler
'''

import glob
import os

from PIL import Image

from sentinel.tilesnapshot import tilesnapshot


class harvestmask(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def generate_harvest_mask(self, tile_x, tile_y, size_x=512, size_y=512, threshold=0.35, min_neighbours_harvested=5, max_neighbours_unharvested=7, neighbourhood_size=2, neighbourhood_passes=7):
        # threshold                  = 0.35 # Threshold NVDI measure, below this looks potentially "harvested"
        # min_neighbours_harvested   = 5  # 3    # In order to have a pixel harvested, it must have at least this many neighbours also "harvested"
        # max_neighbours_unharvested = 7  # 5    # If an otherwise "unharvested" pixel has this many "harvested" neighbours, then consider it "harvested"
        # neighbourhood_size         = 2  # 1    # Number of pixels in each direction to consider a pixel's "neighbourhood"
        # neighbourhood_passes       = 7  # How many times to do a pass over the neighbourhood

        # Which cloud mask to use
        #cloudMask = 'CrudeCloudMask'
        cloudMask = 'CloudMask'

        # Base location for data
        basePath = os.path.join("data", "sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y")

        # Location for output - create this directory if it does not already exist
        save_location = os.path.join("data", "sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y", "Masks", "harvested_nvdi_masks")
        os.makedirs(save_location, exist_ok=True)

        # List available snapshots
        # Just look for the "B01" image as an indicator of which dates are available
        timeSeriesFilter = os.path.join(basePath, "timeseries", str(tile_x) + "-" + str(tile_y) + "-B01-*.png")
        timeSeriesList   = glob.glob(timeSeriesFilter)

        # Helper function to check if a pixel is harvested
        def is_harvested(img, y, x):
            if (img.getpixel((y,x)) == (255, 0, 0, 255)):
                return 1
            else:
                return 0

        # Process each snapshot
        for i in range(len(timeSeriesList)):
            print("Processing [" + timeSeriesList[i].replace('B01', '*') + "]")
    
            # Find the actual filename part of the path
            baseName  = os.path.basename(timeSeriesList[i])
            # Find the dateStr (YYYY-MM-DD)
            dateStart = len(str(tile_x)) + len(str(tile_y)) + 6
            dateEnd   = dateStart + 10
            dateStr   = baseName[dateStart:dateEnd]
    
            # Initialize the tilesnapshot object
            t = tilesnapshot(tile_x, tile_y, dateStr, size_x, size_y)
    
            # Load the TCI layer
            t.loadLayers(['TCI', 'B04', 'B08'])
    
            # Load the Sugar Mask
            t.loadSugarMask()
    
            # Load the Cloud Mask - s2cloudless
            t.loadCloudMask()
    
            # Load the Cloud Mask - crude
            t.loadCrudeCloudMask()
    
            # Create new mask
            img = Image.new('RGBA', (size_x, size_y))

            # Record where output will be written
            output_file = os.path.join(save_location, dateStr + ".png")
    
            sugar_count   = 0
            cloud_count   = 0
            harvest_count = 0
            other_count   = 0
    
            count_harvest_reset = 0  # How many pixels were reset due to min_neighbours_harvested   rule
            count_harvest_set   = 0  # How many pixels were set   due to max_neighbours_unharvested rule
        
            # First pass - estimate which individual pixels might be "harvested" based on NVDI  
            for y in range(size_y):
                for x in range(size_x):
                    # Record the RGB values from the true color image
                    rgb_red   = t.layers['TCI'][y,x][0]
                    rgb_green = t.layers['TCI'][y,x][1]
                    rgb_blue  = t.layers['TCI'][y,x][2]
            
                    NIR = t.layers['B08'][y,x]
                    red = t.layers['B04'][y,x]
            
                    NVDI = (NIR - red)/(NIR + red)
            
                    if (t.layers[cloudMask][y,x]==(0, 0, 0, 255)):
                        cloud_count += 1
                        img.putpixel((y, x), (255, 255, 0, 255))
                    elif (t.layers['SugarMask'][y,x,] != (0, 0, 0, 255)):
                        sugar_count += 1
                        img.putpixel((y, x), (0, 0, 0, 128))
                    elif (NVDI < threshold):
                        harvest_count += 1
                        img.putpixel((y, x), (255, 0, 0, 255))
                    else:
                        other_count += 1
                        img.putpixel((y, x), (rgb_red, rgb_green, rgb_blue, 255))
    
    
            # How to perform a single pass to smooth out harvested pixels based on their neighbourhood
            # - minimum number of neighbours that must be harvested in order for a pixel to be considered harvested
            # - maximum number of neighbours that can be harvested in order for a pixel to be considered unharvested   

            def neighbourhood_pass(img, pass_number):
                local_count_reset        = 0
                local_count_set          = 0
        
                img2 = Image.new('RGBA', (size_x, size_y))
        
                for y in range(size_y):
                    for x in range(size_x):
                        # Recall the RGB values from the true color image, in case we decide to switch from harvested -> unharvested
                        rgb_red   = t.layers['TCI'][y,x][0]
                        rgb_green = t.layers['TCI'][y,x][1]
                        rgb_blue  = t.layers['TCI'][y,x][2]
        
                        # Recall first-pass harvested/unharvested status
                
                        status_harvested = is_harvested(img, y, x)
                    
                        # Check neighbour status
                        neighbours_count     = 0
                        neighbours_harvested = 0
                        for neighbour_y in range(y - neighbourhood_size, y + neighbourhood_size + 1): # Includes start but not end, so, +2
                            for neighbour_x in range(x-1, x+2):
                                if ((0 <= neighbour_y < size_y) and (0 <= neighbour_x < size_x)):
                                    neighbours_count += 1
                                    if (is_harvested(img, neighbour_y, neighbour_x)):
                                        neighbours_harvested += 1
                
                        # Start with the original pixel value from the first pass
                        img2.putpixel((y, x), img.getpixel((y, x)))
                                
                        # Apply min_neighbours_harvested rule
                        if ((min_neighbours_harvested != 0) and (neighbours_harvested < min_neighbours_harvested) and (status_harvested)):
                            local_count_reset += 1
                            img2.putpixel((y, x), (rgb_red, rgb_green, rgb_blue, 255))
                    
                        # Apply max_neighbours_unharvested rule
                        elif ((max_neighbours_unharvested != 0) and (neighbours_harvested > max_neighbours_unharvested) and (not status_harvested)):
                            local_count_set   += 1
                            img2.putpixel((y, x), (255, 0, 0, 255))                               
                    
                print("PASS [" + str(pass_number) + "] Neighbours rules reset [" + str(local_count_reset) + "] and set [" + str(local_count_set) + "] pixels")
    
                return (local_count_reset, local_count_set, img2)
    
            if ((min_neighbours_harvested != 0) or (max_neighbours_unharvested != 0) and (neighbourhood_passes > 0)):
                for pass_number in range(1, neighbourhood_passes+1):
                    (local_count_reset, local_count_set, img2) = neighbourhood_pass(img, pass_number)
            
                    count_harvest_reset += local_count_reset
                    count_harvest_set   += local_count_set
            
                    img = img2
            
                    if (local_count_reset + local_count_set == 0):
                        break;
            
            print("Writing [" + output_file + "] Sugar: " + str(sugar_count) + " Cloud: " + str(cloud_count) + " Harvest: " + str(harvest_count) + " Other: " + str(other_count))
            print("Neighbours rules reset [" + str(count_harvest_reset) + "] and set [" + str(count_harvest_set) + "] pixels")
            img.save(output_file)
    
        print("Finished harvest mask! " + str(tile_x) + ", " + str(tile_y))