'''
Created on 20 Aug 2019

@author: User
'''

import glob
import os
import pprint

from PIL import Image, ImageDraw

from sentinel.geometry import geometry
from sentinel.metadata import metadata

class tilesnapshot(object):
    '''
    A class used to one point-in-time "snapshot" of a tile
    '''


    def __init__(self, x, y, dateStr):
        '''
        Parameters
        ----------
        x : str
            The x coordinate of the tile (7680 for phase 1)
            
        y : str
            The y-coordinate of the tile (10260 for phase 1)
        
        dateStr : str
            The string representing the date of the snapshot in YYYY-MM-DD format
        '''
        
        # Record the tile coords and date of snapshot
        self.x        = x
        self.y        = y
        self.dateStr  = dateStr
        
        # Work out basePath from x and y
        self.basePath = 'data/sentinel-2a-tile-' + str(self.x) + 'x-' + str(self.y) + 'y'
        
        # Load the geometry for this tile
        self.geometryPath = self.basePath + "/geometry/file-x" + str(self.x) + "-y" + str(self.y) + ".geojson"
        self.geometry = geometry(self.geometryPath)
        
        # Load the metadata for this snapshot as a child object
        self.metadataPath = self.basePath + "/metadata/" + dateStr + ".json"
        self.metadata = metadata(self.metadataPath)
        
        # List available layers
        self.layerFilesFilter = self.basePath + "/timeseries/" + str(self.x) + "-" + str(self.y) + "-*-" + self.dateStr + ".png"
        self.layerList = glob.glob(self.layerFilesFilter)
        
        self.layers = dict()
        
        # Load each available layer into a "layers" dictionary
        for i in range(len(self.layerList)):
            self.loadLayer(self.layerList[i])
            
        # Load sugar cane mask
        self.sugarCaneMaskPath = self.basePath + "/masks/sugarcane-region-mask.png"
        self.loadLayer(self.sugarCaneMaskPath, 'SugarMask')
    
    def loadLayer(self, fullPath, layerName=None):
        # Find the actual filename part of the path
        baseName = os.path.basename(fullPath)
        # Find the layerName (e.g. TCI, B01, B02, ..., B12)
        if layerName is None:
            layerName = baseName.split('-')[2]
        # Load the layer
        img = Image.open(fullPath)
        self.layers[layerName] = img.load()
        
    def print(self):
        '''
        Prints debug information about the object to the console
        '''
        print("Metadata:")
        self.metadata.print()
        print("Geometry:")
        self.geometry.print()
        print("Layers:")
        pprint.pprint(self.layers)'''
Created on 25 Aug 2019

@author: User
'''
