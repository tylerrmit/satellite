'''
Created on 20 Aug 2019

@author: User
'''

import glob
import os
import pprint
import numpy as np
import PIL

from PIL import Image

from sentinelhub import WmsRequest, BBox, CRS, MimeType, CustomUrlParam, get_area_dates
from s2cloudless import S2PixelCloudDetector, CloudMaskRequest

from sentinel.geometry import geometry
from sentinel.metadata import metadata

# Static function to divide a pixel by 65535 to get into expected format
def convert_pixel_65535(x):
    return x / 65535

# Vectorized version
v_convert_pixel_65535 = np.vectorize(convert_pixel_65535)


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
        #print("Layer List Filter: " + self.layerFilesFilter)
        self.layerList = glob.glob(self.layerFilesFilter)
        #print("Layer List: ")
        #print(self.layerList)
        
        self.layers = dict()
        self.numpy_layers = dict()
        self.numpy_raw = dict()
        
        # Load each available layer into a "layers" dictionary
        for i in range(len(self.layerList)):
            #print("Loading layer: " + str(i))
            self.loadLayer(self.layerList[i])
            
        # Load sugar cane mask
        self.sugarCaneMaskPath = self.basePath + "/masks/sugarcane-region-mask.png"
        self.loadLayer(self.sugarCaneMaskPath, 'SugarMask')
    
        # Load numpy.ndarray for use with s2cloudless
        self.numpy_bands = np.empty((1, 512, 512, 10))
        self.numpy_bands[0,:,:,0] = self.numpy_layers['B01']
        self.numpy_bands[0,:,:,1] = self.numpy_layers['B02']
        self.numpy_bands[0,:,:,2] = self.numpy_layers['B04']
        self.numpy_bands[0,:,:,3] = self.numpy_layers['B05']
        self.numpy_bands[0,:,:,4] = self.numpy_layers['B08']
        self.numpy_bands[0,:,:,5] = self.numpy_layers['B8A']
        self.numpy_bands[0,:,:,6] = self.numpy_layers['B09']
        self.numpy_bands[0,:,:,7] = self.numpy_layers['B10']
        self.numpy_bands[0,:,:,8] = self.numpy_layers['B11']
        self.numpy_bands[0,:,:,9] = self.numpy_layers['B12']
        
        # Detect clouds!
        print("Detecting clouds for " + dateStr)
        cloud_detector  = S2PixelCloudDetector(threshold=0.7, average_over=4, dilation_size=2)
        self.cloud_probs = cloud_detector.get_cloud_probability_maps(np.array(self.numpy_bands))
        self.cloud_masks = cloud_detector.get_cloud_masks(self.numpy_bands)
        print("... done")
        
    def loadLayer(self, fullPath, layerName=None):
        # Find the actual filename part of the path
        baseName = os.path.basename(fullPath)
        # Find the layerName (e.g. TCI, B01, B02, ..., B12)
        if layerName is None:
            layerName = baseName.split('-')[2]
        # Load the layer
        img = Image.open(fullPath)
        self.layers[layerName] = img.load()
        # Convert the layer into a numpy array
        #self.numpy_layers[layerName] = np.asarray(PIL.Image.open(fullPath))
        self.numpy_raw[layerName] = np.asarray(PIL.Image.open(fullPath))
        self.numpy_layers[layerName] = self.numpy_raw[layerName] / 20000 # Do not ask me why it's not 65536
    
        
    def print(self):
        '''
        Prints debug information about the object to the console
        '''
        print("Metadata:")
        self.metadata.print()
        print("Geometry:")
        self.geometry.print()
        #print("Layers:")
        #pprint.pprint(self.layers)
        print("Numpy Layers:")
        pprint.pprint(self.numpy_layers)
        print("Cloud Mask:")
        pprint.pprint(self.cloud_masks)
        print("Numpy bands shape:")
        print(self.numpy_bands.shape)
        
        