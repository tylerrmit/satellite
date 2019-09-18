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

# Job parameters that can be tuned
tile_x                     = 7680
tile_y                     = 10240
size_x                     = 512  # Width of the tile in pixels
size_y                     = 512  # Height of the tile in pixels
pre_window                 = 2    # How many previous snapshots must have "high-vegetation" to count the change to "low-vegetation" (was there vegetation before?)
post_window                = 2    # How many following snapshots must have "low-vegetation" to count the change to "low-vegetation" (is it stable?)

# Base location for data
basePath = os.path.join("data", "sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y")

# Location for output - create this directory if it does not already exist
save_location = os.path.join("data", "sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y", "Masks", "harvested")
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
def is_harvested(pixel):
    if (pixel == (255, 0, 0, 255)):
        return 1
    else:
        return 0


# Helper function to check if a pixel is obscured by cloud
def is_cloudy(pixel):
    if (pixel == (255, 255, 0, 255)):
        return 1
    else:
        return 0
    

# List available snapshots
# Just look for the "B01" image as an indicator of which dates are available
timeSeriesFilter = os.path.join(basePath, "timeseries", str(tile_x) + "-" + str(tile_y) + "-B01-*.png")
timeSeriesList   = glob.glob(timeSeriesFilter)

# Initialize a "dictionary" of tilesnapshots, so we can compare pixels across time within a "window"
# We only want to keep just enough in memory for that window, though!  We could run out of memory
# if we try to load years at a time!
tileSnapshotList = dict()

# Process each snapshot
for i in range(len(timeSeriesList)):
#for i in range(3):
    dateStr = snapshotToDateStr(timeSeriesList[i])
    
    print("Processing [" + timeSeriesList[i].replace('B01', '*') + "]")

    # ================================================================================
    # Make sure all the required snapshots (before and after) are loaded and available
    # ================================================================================
    
    # Record the min_index and max_index in the window
    min_index  = -1
    max_index  = -1
    this_index = -1
    
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
            if (min_index < 0):
                min_index = j
        
    # Check if the tilesnapshot has already been loaded
    if (i not in tileSnapshotList):
        print ("Loading  snapshot " + dateStr + " (" + str(i) + ")")
        
        # Initialize the tilesnapshot object and add it to the list/dictionary
        tileSnapshotList[i] = tilesnapshot(tile_x, tile_y, dateStr, size_x, size_y)
        
        # Load the TCI layer
        tileSnapshotList[i].loadLayers(['TCI'])
        
        # Load the harvest mask
        tileSnapshotList[i].loadHarvestMask()
    else:
        print("Reusing  snapshot " + dateStr + " (" + str(i) + ") to support itself")
    
    if (min_index < 0):
        min_index = i
    this_index = i 
    max_index  = i  

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
                tileSnapshotList[j].loadHarvestMask()
            else:
                print("Reusing  snapshot " + dateStrFollowing + " (" + str(j) + ") to follow snapshot " + dateStr + " (" + str(i) + ")")
                
            max_index = j
            
    print("Loaded range " + str(min_index) + " -> " + str(this_index) + " -> " + str(max_index) + " to support snapshot " + dateStr + " (" + str(i) + ")")


    # ======================================================================================================
    # Compare each pixel in the current snapshot against the preceding and following snapshots in the window
    # ======================================================================================================
    
    # Create a new Image object for output
    img = Image.new('RGBA', (size_x, size_y))

    # Record where output will be written
    output_file = save_location + "\\" + dateStr + ".png"
    
    
    # We will store a list of pixels from 0 => last snapshot included in the window
    pixel_window = []
               
    first_index   = 0
    current_index = this_index - min_index
    last_index    = max_index  - min_index
    
    count_cloud_adjust      = 0
    count_deltas            = 0
    count_current_harvested = 0
        
    # For each pixel
    for y in range(size_y):
    #for y in range(1):
        for x in range(size_x):
        #for x in range(317):
            if (is_harvested(tileSnapshotList[i].layers['HarvestMask'][y,x])):
                count_current_harvested += 1
                
            # Load time series window for pixel into a list
            pixel_window.clear()
            
            for s in range(min_index, max_index + 1):
                pixel_window.append(tileSnapshotList[s].layers['HarvestMask'][y,x])
                
            # Load the original TCI pixel
            tci_pixel = tileSnapshotList[i].layers['TCI'][y,x]
            
            # How many of the preceding snapshots had the pixel harvested/unharvested?
            preceding_harvested   = 0
            preceding_unharvested = 0
            preceding_available   = 0
            
            for t in range(first_index, current_index):
                if ((t >= 0) and (t < current_index)):  # New language paranoia
                    if (is_harvested(pixel_window[t])):
                        preceding_harvested   += 1
                    else:
                        preceding_unharvested += 1
                    preceding_available += 1
                
            # How many of the following snapshots had the pixel harvested/unharvested?
            following_harvested   = 0
            following_unharvested = 0
            following_available   = 0
            
            for t in range(current_index, last_index + 1):
                if ((t >= current_index) and (t <= last_index) and (t-1 > 0)): # New language paranoia
                    # If the pixel is cloudy, assume the last thing we had for it
                    if ((is_cloudy(pixel_window[t])) and (t - 1 >= 0) and not (is_cloudy(pixel_window[t-1]))):
                        # Update the window copy of this pixel, use the value of the previous snapshot
                        # If THAT was a cloud, we've already made a similar adjustment to it!
                        pixel_window[t] = pixel_window[t-1]
                        # Update the master "layer" copy of this pixel so that the correction propagates
                        tileSnapshotList[i + t - current_index].layers['HarvestMask'][y,x] = pixel_window[t]
                        count_cloud_adjust += 1
                        
                    # After applying prior-to-cloud-is-sticky assumption, is it harvested?
                    if (t > current_index):
                        if (is_harvested(pixel_window[t])):
                            following_harvested   += 1
                        else:
                            following_unharvested += 1
                        following_available += 1
                               
            # So, knowing all that, was it harvested?               
            if (
                (preceding_available)                          and
                (is_harvested(pixel_window[current_index]))    and
                (preceding_unharvested == preceding_available) and
                (following_harvested   >= following_available)
            ):
                # Yes!  Everything before was unharvested (high vegetation) and everything after was harvested (low vegetation)
                # If we have clouds serveral days in a row, this is vulnerable to false positives at the moment
                img.putpixel((y, x), (0, 0, 255, 255))  # Blue
                count_deltas += 1
            else:
                img.putpixel((y, x), tileSnapshotList[i].layers['HarvestMask'][y,x])

                
    print("Writing [" + output_file + "] cloud_adjust [" + str(count_cloud_adjust) + "] deltas [" + str(count_deltas) + "] current_harvested [" + str(count_current_harvested) + "]")
    img.save(output_file)    
                
print("Finished!")
