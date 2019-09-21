'''
Created on 30 Aug 2019

@author: Tyler

Step through the harvest masks (from generate_harvest_masks_nvdi.py) over time

Masked pixels don't count

The first time we see a 'red' (low-vegetation) pixel, it doesn't count as harvested

We are looking for 'red' pixels where:
- the preceding "pre_window"  snapshots have high-vegetation for the pixel
- the following "post_window" snapshots have low -vegetation for the pixel
- it is assumed that any pixel that is masked by cloud has the same value as the most recent snapshot when the pixel was not obscured by cloud
'''

# Imports
import glob
import os

from PIL import Image

from sentinel.tilesnapshot import tilesnapshot


def delta_nvdi_intensity(tile_x, tile_y, size_x=512, size_y=512):
    # size_x                     = 512  # Width of the tile in pixels
    # size_y                     = 512  # Height of the tile in pixels

    # Location for output - create this directory if it does not already exist
    save_location = os.path.join("masks", "nvdi_intensity_cloudless")
    os.makedirs(save_location, exist_ok=True)


    # Helper function to get dateStr from full path of time series PNG
    def snapshotToDateStr(fullpath):
        # Find the actual filename part of the path
        baseName  = os.path.basename(fullpath)
        # Find the dateStr (YYYY-MM-DD)
        dateStart = len(str(tile_x)) + len(str(tile_y)) + 9
        dateEnd   = dateStart + 10
        dateStr   = baseName[dateStart:dateEnd]

        return dateStr


    # Helper function to check if a pixel is obscured by cloud
    def is_cloudy(pixel):
        if (pixel == (0, 128)):
            return 1
        else:
            return 0
    
    # List available snapshots
    # Just look for the "B01" image as an indicator of which dates are available
    timeSeriesFilter = os.path.join("masks", "nvdi_intensity", "mask-x" + str(tile_x) + "-y" + str(tile_y) + "-*.png")
    timeSeriesList   = glob.glob(timeSeriesFilter)
    
    print("Searching for tiles: [" + timeSeriesFilter + "]")

    # Create a new Image object for output/retention
    img_output = Image.new('LA', (size_x, size_y))
        
    # Process each snapshot
    for i in range(len(timeSeriesList)):
        dateStr = snapshotToDateStr(timeSeriesList[i])
    
        print("Processing [" + timeSeriesList[i] + "]")
      
        count_cloud_adjust = 0
            
        # The first image is left as-is, because we don't have any prior images to use to remove clouds
        if (i == 0):
            snapshot = tilesnapshot(tile_x, tile_y, dateStr, size_x, size_y)
            snapshot.loadNVDIIntensity()
            
            # Copy the original layer into the output image
            for y in range(size_y):
                for x in range(size_x):
                    img_output.putpixel((y, x), snapshot.layers['NVDI'][y,x])
                    
        # Subsequent image keep the output of the previous image if a pixel is cloudy,
        # and replace the pixel if it is not cloudy
        else:
            snapshot = tilesnapshot(tile_x, tile_y, dateStr, size_x, size_y)
            snapshot.loadNVDIIntensity()
            
            for y in range(size_y):
                for x in range(size_x):
                    # Check if the pixel in this_snapshot is cloudy
                    if (not is_cloudy(snapshot.layers['NVDI'][y,x])):
                        img_output.putpixel((y, x), snapshot.layers['NVDI'][y,x])
                        count_cloud_adjust += 1     
            
        # Save the output for this snapshot
        output_file = os.path.join(save_location, "mask-x" + str(tile_x) + "-y" + str(tile_y) + "-" + dateStr + ".png")
        print("Writing [" + output_file + "] cloud_adjust [" + str(count_cloud_adjust) + "]")
        img_output.save(output_file)  
                
    print("Finished!")

if __name__ == "__main__":
    # Test delta harvest on phase1 example tile
    delta_nvdi_intensity(tile_x=7680, tile_y=10240)