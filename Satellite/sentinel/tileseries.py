'''
Created on 20 Aug 2019

@author: User
'''

import glob
import os
import pprint

from sentinel.geometry import geometry
from sentinel.tilesnapshot import tilesnapshot

class tileseries(object):
    '''
    A class used to represent a time series of snapshots of a tile
    '''

    def __init__(self, x, y):
        '''
        Parameters
        ----------
        x : str
            The x coordinate of the tile (7680 for phase 1)
            
        y : str
            The y-coordinate of the tile (10260 for phase 1)
        '''
        
        # Record the tile coords
        self.x = x
        self.y = y
        
        # Load the geometry for this tile
        self.geometryPath = os.path.join("geometries", "geo-x" + str(self.x) + "-y" + str(self.y) + ".geojson")
        self.geometry = geometry(self.geometryPath)
        
        # List available snapshots
        self.timeSeriesFilter = os.path.join("metadata", "*.json")
        self.timeSeriesList   = glob.glob(self.timeSeriesFilter)
        
        self.snapshots = dict()
        
        # Load each available snapshot into a "snapshots" dictionary
        #for i in range(len(self.timeSeriesList)):
        for i in range(len(self.timeSeriesList)):
            print("Loading snapshot [" + str(i) + "] [" + self.timeSeriesList[i] + "]")
            self.loadSnapshot(self.timeSeriesList[i])
            
    def loadSnapshot(self, fullPath):
        '''
        Loads one snapshot for a date into the tileseries.snapshots dictionary
        '''
        # Find the actual filename part of the path
        baseName = os.path.basename(fullPath)
        # Find the dateStr (YYYY-MM-DD)
        dateStr = baseName.split('.')[0]
        # Load the snapshot
        #self.snapshots[dateStr] = tilesnapshot(7680, 10240, dateStr)
        self.latestSnapshot = tilesnapshot(7680, 10240, dateStr)
        
    def print(self):
        '''
        Prints debug information about the object to the console
        '''
        print("Snapshots:")
        pprint.pprint(self.latestSnapshot)
        