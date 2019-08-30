'''
Created on 30 Aug 2019

@author: Tyler

Step through the harvest masks (from generate_harvest_masks_nvdi.py) over time

Masked pixels don't count

The first time we see a 'red' (low-vegetation) pixel, it doesn't count as harvested

We are looking for 'red' pixels where:
- the preceding "pre_window" snapshots have the same pixel as high-vegetation
- the following "post_window" snapshots have the same pixel as low-vegetation
- it is assumed that any pixel that is masked by cloud has the same value as the most recent good snapshot
'''

# Imports
import glob
import os
import sys

from PIL import Image

from sentinel.tilesnapshot import tilesnapshot

# Job parameters that can be tuned
tile_x                     = 7680
tile_y                     = 10240
size_x                     = 512  # Width of the tile in pixels
size_y                     = 512  # Height of the tile in pixels
pre_window                 = 2    # How many previous snapshots must have "high-vegetation" to count the change to "low-vegetation" (was there vegetation before?)
post_window                = 2    # How many following snapshots must have "low-vegetation" to count the change to "low-vegetation" (is it stable?)

# Base location for data   
basePath = "data\\sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y"

# Location for output - create this directory if it does not already exist
save_location = "data\\sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y\\Output\\harvested"
os.makedirs(save_location, exist_ok=True)


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
def is_harvested(img, y, x):
    if (img.getpixel((y,x)) == (255, 0, 0, 255)):
        return 1
    else:
        return 0
    

# List available snapshots
# Just look for the "B01" image as an indicator of which dates are available
timeSeriesFilter = basePath + "\\timeseries\\" + str(tile_x) + "-" + str(tile_y) + "-B01-*.png"
timeSeriesList   = glob.glob(timeSeriesFilter)

# Initialize a "dictionary" of tilesnapshots, so we can compare pixels across time within a "window"
# We only want to keep just enough in memory for that window, though!  We could run out of memory
# if we try to load years at a time!
tileSnapshotList = dict()

# Process each snapshot
for i in range(len(timeSeriesList)):
    dateStr = snapshotToDateStr(timeSeriesList[i])
    
    print("Processing [" + timeSeriesList[i].replace('B01', '*') + "]")

    # Drop snapshots that are no longer required that have not already been dropped
    j = i - pre_window - 1
    if (j in tileSnapshotList):
        dateStrPreceding = snapshotToDateStr(timeSeriesList[j])
        print("Dropping snapshot " + dateStrPreceding + " (" + str(j) + ") no longer required")
        del tileSnapshotList[j]
    
    # Report on preceding snapshots that will be reused
    for j in range(i - pre_window, i):
        if ((j >= 0) and (j < i)):
            dateStrPreceding = snapshotToDateStr(timeSeriesList[j])
            print("Reusing  snapshot " + dateStrPreceding + " (" + str(j) + ") to precede snapshot " + dateStr + " (" + str(i) + ")")
        
    # Check if the tilesnapshot has already been loaded
    if (i not in tileSnapshotList):
        print ("Loading  snapshot " + dateStr + " (" + str(i) + ")")
        
        # Initialize the tilesnapshot object and add it to the list/dictionary
        tileSnapshotList[i] = tilesnapshot(tile_x, tile_y, dateStr, size_x, size_y)
        
        # Load the TCI layer
        tileSnapshotList[i].loadLayers(['TCI'])
        
        # Load the harvest mask
        # TODO
        # tileSnapshotList[i].loadHarvestMask()
    else:
        print("Reusing  snapshot " + dateStr + " (" + str(i) + ") to support itself")      

    # Assume "preceding" snapshots are already loaded
    # Load "following" snapshots as required for the window
    for j in range(i + 1, i + post_window + 1):
        if (j < len(timeSeriesList)):
            dateStrFollowing = snapshotToDateStr(timeSeriesList[j])
            
            if (j not in tileSnapshotList):
                print("Loading  snapshot " + dateStrFollowing + " (" + str(j) + ") to follow snapshot " + dateStr + " (" + str(i) + ")")
            
                # Initialize the tilesnapshot object and add it to the list/dictionary
                tileSnapshotList[j] = tilesnapshot(tile_x, tile_y, dateStrFollowing, size_x, size_y)
        
                # Load the TCI layer
                tileSnapshotList[j].loadLayers(['TCI'])
        
                # Load the harvest mask
                # TODO
                # tileSnapshotList[j].loadHarvestMask()
            else:
                print("Reusing  snapshot " + dateStrFollowing + " (" + str(j) + ") to follow snapshot " + dateStr + " (" + str(i) + ")")
            
print("Finished!")
