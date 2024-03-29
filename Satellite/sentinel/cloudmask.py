'''
Created on 17 Sep 2019

@author: User
'''

import glob
import os

from sentinel.tilesnapshot import tilesnapshot

class cloudmask(object):
    '''
    A class used to generate cloud masks for a tile
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def generate_cloud_mask(self, tile_x, tile_y, size_x=512, size_y=512, threshold=0.7):
        # List available snapshots
        timeSeriesFilter = os.path.join("sugarcanetiles", str(tile_x) + "-" + str(tile_y) + "-B01-*.png")
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

        print("Finished cloud mask! " + str(tile_x) + ", " + str(tile_y))     