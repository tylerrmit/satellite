'''
Created on 20 Aug 2019

@author: User
'''

import glob
import os
import numpy as np
import PIL

from PIL import Image

from s2cloudless import S2PixelCloudDetector

from sentinel.geometry import geometry
from sentinel.metadata import metadata


class tilesnapshot(object):
    '''
    A class used to one point-in-time "snapshot" of a tile
    '''


    def __init__(self, tile_x, tile_y, dateStr, size_x=512, size_y=512):
        '''
        Initialise the object and load geometry and metadata.
        Defer loading of layers/bands, call loadLayers() to do that
        
        Parameters
        ----------
        tile_x : str
            The x coordinate of the tile (7680 for phase 1)
            
        tile_y : str
            The y-coordinate of the tile (10260 for phase 1)
        
        size_x : int
            The width of the tile in pixels
            
        size_y : int
            The height of the tile in pixels
        
        dateStr : str
            The string representing the date of the snapshot in YYYY-MM-DD format
        '''
        
        # Record the tile coordinates and date of snapshot
        self.tile_x           = tile_x
        self.tile_y           = tile_y
        self.size_x           = size_x
        self.size_y           = size_y
        self.dateStr          = dateStr
        
        # List of "band" layers that are required for cloud detection
        self.band_list        = ['B01', 'B02', 'B04', 'B05', 'B08', 'B8A', 'B09', 'B10', 'B11', 'B12']
        
        # Work out basePath from x and y
        self.basePath         = 'data/sentinel-2a-tile-' + str(self.tile_x) + 'x-' + str(self.tile_y) + 'y'
        
        # Load the geometry for this tile
        self.geometryPath     = self.basePath + "/geometry/file-x" + str(self.tile_x) + "-y" + str(self.tile_y) + ".geojson"
        self.geometry         = geometry(self.geometryPath)
        
        # Load the metadata for this snapshot as a child object
        self.metadataPath     = self.basePath + "/metadata/" + dateStr + ".json"
        self.metadata         = metadata(self.metadataPath)
        
        # List available layers
        self.layerFilesFilter = self.basePath + "/timeseries/" + str(self.tile_x) + "-" + str(self.tile_y) + "-*-" + self.dateStr + ".png"
        self.layerList        = glob.glob(self.layerFilesFilter)
        
        # Create dictionaries for layer data
        self.layers           = dict()  # Pillow Image format
        self.numpy_layers     = dict()  # Numpy array
    
    
    def loadLayers(self, layerList=['ALL']):
        '''
        Load layers belonging to a snapshot
        
        Parameters
        ----------
        layerList : list
            List of band names to load, e.g. 'TCI', 'B01', etc.
            Default list ['ALL'] means load all available layers
        '''
        # Load each available layer into a "layers" dictionary
        for i in range(len(self.layerList)):
            fullPath  = self.layerList[i]
            baseName  = os.path.basename(fullPath)
            layerName = baseName.split('-')[2]
            
            # Load this layer if we requested ALL layers, or if we requested it by name
            if (('ALL' in layerList) or (layerName in layerList)):
                self.loadLayer(fullPath, layerName)
    
    
    def loadSugarMask(self):
        '''
        Load sugar cane mask as 'SugarMask' layer
        '''
        self.sugarCaneMaskPath = self.basePath + "/masks/sugarcane-region-mask.png"
        self.loadLayer(self.sugarCaneMaskPath, 'SugarMask')

        
    def loadLayer(self, fullPath, layerName):
        '''
        Load an individual layer by fullPath and layerName
        
        Parameters
        ----------
        layerList : list
            List of band names to load, e.g. 'TCI', 'B01', etc.
            Default list ['ALL'] means load all available layers
        '''
        # Only load layers that are not already there
        if (layerName not in self.layers):
            # Load the layer as-is
            self.layers[layerName] = Image.open(fullPath).load()
            
            # If it is a "band" layer, convert it into an array for cloud detection
            if (layerName.startswith('B')):
                numpy_raw = np.asarray(PIL.Image.open(fullPath))
                self.numpy_layers[layerName] = numpy_raw / 20000 # Do not ask me why it's not 65536, I reverse-engineered this and it took all day


    def detectClouds(self, threshold):
        '''
        Use s2cloudless to detect clouds
        
        Parameters
        ----------
        threshold : float
            Minimum probability of cloud in order to mask a pixel
        '''
        self.threshold = threshold
        
        # Load any bands that are not already there
        
        load_required = 0
        for band in self.band_list:
            if (band not in self.layers):
                load_required = 1
                
        if (load_required == 1):
            self.loadLayers(self.band_list)
            
        # Load numpy.ndarray for use with s2cloudless
        numpy_bands = np.empty((1, self.size_x, self.size_y, 10))
        numpy_bands[0,:,:,0] = self.numpy_layers['B01']
        numpy_bands[0,:,:,1] = self.numpy_layers['B02']
        numpy_bands[0,:,:,2] = self.numpy_layers['B04']
        numpy_bands[0,:,:,3] = self.numpy_layers['B05']
        numpy_bands[0,:,:,4] = self.numpy_layers['B08']
        numpy_bands[0,:,:,5] = self.numpy_layers['B8A']
        numpy_bands[0,:,:,6] = self.numpy_layers['B09']
        numpy_bands[0,:,:,7] = self.numpy_layers['B10']
        numpy_bands[0,:,:,8] = self.numpy_layers['B11']
        numpy_bands[0,:,:,9] = self.numpy_layers['B12']
        
        cloud_detector   = S2PixelCloudDetector(threshold=threshold, average_over=4, dilation_size=2)
        self.cloud_probs = cloud_detector.get_cloud_probability_maps(np.array(numpy_bands))
        self.cloud_masks = cloud_detector.get_cloud_masks(numpy_bands)
        
        # Save cloud mask to disk as black PNG that is transparent where there is no cloud,
        # and opaque where the probability of cloud > threshold
        save_location = "data\\sentinel-2a-tile-" + str(self.tile_x) + "x-" + str(self.tile_y) + "y\\Masks\\cloud_masks"
        os.makedirs(save_location, exist_ok=True)
    
        img = Image.new('RGBA', (self.size_x, self.size_y), color = 'black')

        for x in range(self.size_x):
            for y in range(self.size_y):
                if (self.cloud_masks[0][y][x] > 0):
                    img.putpixel((x, y), (0,0,0,255)) # Opaque
                else:
                    img.putpixel((x, y), (0,0,0,0))   # Transparent
    
        output_file = save_location + "\\" + self.dateStr + ".png"
        print("Writing [" + output_file + "]")    
        img.save(output_file)
        
        
    def print(self):
        '''
        Prints debug information about the object to the console
        '''
        print("Metadata:")
        self.metadata.print()
        print("Geometry:")
        self.geometry.print()
        