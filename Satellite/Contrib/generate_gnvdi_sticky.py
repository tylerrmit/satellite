'''
Created on 04 Aug 2019

@author: Tyler

Generate GNVDI intensity

If masked by cloud -> use previous good reading
'''

import glob
import os

from PIL import Image

from sentinel.tilesnapshot import tilesnapshot

def generate_gnvdi_sticky(tile_x, tile_y, size_x=512, size_y=512):
    # tile_x                     = 7680
    # tile_y                     = 10240
    # size_x                     = 512  # Width of the tile in pixels
    # size_y                     = 512  # Height of the tile in pixels


    # Which cloud mask to use
    cloudMask = 'CloudMask'

    # Location for output - create this directory if it does not already exist   
    save_location_intensity = os.path.join("masks", "gnvdi_intensity")
    os.makedirs(save_location_intensity, exist_ok=True)

    # List available snapshots
    # Just look for the "B01" image as an indicator of which dates are available
    timeSeriesFilter = os.path.join("sugarcanetiles", str(tile_x) + "-" + str(tile_y) + "-B01-*.png")
    timeSeriesList   = glob.glob(timeSeriesFilter)

    print("Searching for tiles: [" + timeSeriesFilter + "]")     
        
    img_prev = Image.new('LA', (size_x, size_y))
    
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
        t.loadLayers(['TCI', 'B03', 'B08'])
    
        # Load the Sugar Mask
        t.loadSugarMask()
    
        # Load the Cloud Mask - s2cloudless
        t.loadCloudMask()
        
        # Create output image for NVDI intensity from 0 to 65535
        img_intensity = Image.new('LA', (size_x, size_y))

        # Record where output will be written
        output_file_intensity = os.path.join(save_location_intensity, "mask-x" + str(tile_x) + "-y" + str(tile_y) + "-" + dateStr + ".png")
    
        sugar_count   = 0
        cloud_count   = 0
        
        # First pass - estimate which individual pixels might be "harvested" based on NVDI  
        for y in range(size_y):
            for x in range(size_x):
                # Record the RGB values from the true color image            
                NIR   = t.layers['B08'][y,x]
                green = t.layers['B03'][y,x]
                
                if (NIR + green != 0):
                    GNVDI = (NIR - green)/(NIR + green)
                else:
                    GNVDI = 0
                    
                GNVDI_8bit = round(GNVDI * 255)
            
                if (t.layers[cloudMask][y,x]==(0, 0, 0, 255)):
                    cloud_count += 1
                    img_intensity.putpixel((y, x), img_prev.getpixel((y, x)))
                elif (t.layers['SugarMask'][y,x,] != (0, 0, 0, 255)):
                    sugar_count += 1
                    img_intensity.putpixel((y, x), (0, 0))
                else:                       
                    img_intensity.putpixel((y, x), (GNVDI_8bit, 255))
                    
        print("Writing [" + output_file_intensity + "]")
        img_intensity.save(output_file_intensity)
        
        img_prev = img_intensity
    
    print("Finished!")
    
    
if __name__ == "__main__":
    # Test harvest mask generation on phase1 example tile
    generate_gnvdi_sticky(tile_x=7680, tile_y=10240)