'''
Created on 22 Sep 2019

@author: Tyler
'''

# Imports
import glob
import os
from datetime import datetime

from PIL import Image

from sentinel.tilesnapshot import tilesnapshot


def generate_days_since_harvest(tile_x, tile_y, size_x=512, size_y=512):
    # size_x                     = 512  # Width of the tile in pixels
    # size_y                     = 512  # Height of the tile in pixels

    # Location for output - create this directory if it does not already exist
    save_location = os.path.join("masks", "days_since_harvest")
    os.makedirs(save_location, exist_ok=True)
    
    save_location_8bit = os.path.join("masks", "days_since_harvest_8bit")
    os.makedirs(save_location_8bit, exist_ok=True)
    
    
        # Helper function to get dateStr from full path of time series PNG
    def snapshotToDateStr(fullpath):
        # Find the actual filename part of the path
        baseName  = os.path.basename(fullpath)
        # Find the dateStr (YYYY-MM-DD)
        dateStart = len(str(tile_x)) + len(str(tile_y)) + 6
        dateEnd   = dateStart + 10
        dateStr   = baseName[dateStart:dateEnd]

        return dateStr


    # Helper function to check if a pixel is harvested
    def is_harvested_today(pixel):
        if (pixel == (0, 0, 255, 255)):
            return 1
        else:
            return 0
        
        
    # List available snapshots
    # Just look for the "B01" image as an indicator of which dates are available
    timeSeriesFilter = os.path.join("sugarcanetiles", str(tile_x) + "-" + str(tile_y) + "-B01-*.png")
    timeSeriesList   = glob.glob(timeSeriesFilter)

    print("Searching for tiles: [" + timeSeriesFilter + "]")
    
    # Create an image that will store days since last harvest for each pixel
    img_days = Image.new('I', (size_x, size_y), 65535)
    
    # Output an 8-bit version of the image, too
    img_8bit = Image.new('RGB', (size_x, size_y))
        
    date_format = "%Y-%m-%d"
    
    # Process each snapshot
    for i in range(len(timeSeriesList)):
        dateStr = snapshotToDateStr(timeSeriesList[i])
    
        print("Processing [" + dateStr + "]")
        
        # Work out how many days since the previous snapshot (if any)
        if (i == 0):
            prev_day = datetime.strptime(dateStr, date_format)    
        this_day = datetime.strptime(dateStr, date_format)
        delta = this_day - prev_day
        days_since_prev_snapshot = delta.days
                
        # Open the relevant tilesnapshot layers for reading
        ts = tilesnapshot(tile_x, tile_y, dateStr, size_x, size_y)
        ts.loadLayers(['TCI'])
        ts.loadHarvested()
        
        
        # Open an image for output
        # Iterate through each pixel
        max_value = 0
        for y in range(size_y):
            for x in range(size_x):
                current_value = img_days.getpixel((y, x))
                
                if (current_value > max_value):
                    max_value = current_value
                    
                if (is_harvested_today(ts.layers['Harvested'][y,x])):
                    # Reset days since harvest to zero
                    img_days.putpixel((y, x), 0)
                #elif (current_value == 65535):
                    # Never harvested
                    # put TCI pixel    
                elif (current_value != 65535):
                    new_value = current_value + (days_since_prev_snapshot * 90) # Magic number to make 2 years almost white
                    if (new_value >= 65535):
                        new_value = 65534
                    img_days.putpixel((y, x), new_value)
 
                if (current_value == 65535):
                    img_8bit.putpixel((y, x), (0, 0, 0))
                else:
                    approx_value = round(current_value * 255 / 65535)
                    img_8bit.putpixel((y, x), (0, approx_value, 0))
                
        # Output the image
        # Record where output will be written
        output_file = os.path.join(save_location, "mask-x" + str(tile_x) + "-y" + str(tile_y) + "-" +  dateStr + ".png")
        img_days.save(output_file)
        
        output_file_8bit = os.path.join(save_location_8bit, "mask-x" + str(tile_x) + "-y" + str(tile_y) + "-" +  dateStr + ".png")
        img_8bit.save(output_file_8bit)
        
        print("Max value: " + str(max_value))
        
        for y in range(size_y):
            for x in range(size_x):
                current_value = img_days
        
        
        prev_day = this_day
    
    print("Finished!")
        
if __name__ == "__main__":
    # Test delta harvest on phase1 example tile
    generate_days_since_harvest(tile_x=7680, tile_y=10240)
        