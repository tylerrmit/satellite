'''
Created on 18 Sep 2019

@author: Tyler
'''

import os
import glob
import re

from shapely.geometry import shape, Point

import sentinel.geometry as geometry

class geometry_list(object):
    '''
    classdocs
    '''

    def __init__(self, path="geometries"):
        '''
        Constructor
        '''
        
        self.geometries = dict()
        
        self.loadGeometries(path)
        
    def loadGeometries(self, path):
        # List available geometry files
        geometriesFilter = os.path.join("geometries", "geo-x*.geojson")
        geometriesList   = glob.glob(geometriesFilter)

        # Process each geometry file
        for i in range(len(geometriesList)):            
            # Find the X and Y for this tile, from the filename
            parts = re.split("x|y|-|\.", geometriesList[i])
            tile_x = parts[2]
            tile_y = parts[4]
            
            #print("Loading geometry for (" + tile_x + "," + tile_y + ")")
            
            g = geometry(geometriesList[i])
            self.geometries[tile_x + "," + tile_y] = g

    def listGeometries(self):
        for tile in self.geometries.keys():
            parts = tile.split(",")
            tile_x = parts[0]
            tile_y = parts[1]
            
            g = self.geometries[tile]
            
            print("Printing tile: [" + tile_x + "," + tile_y + "]")
            g.print()
            
    def findTile(self, longitude, latitude):
        #print("Latitude:  " + str(latitude))
        #print("Longitude: " + str(longitude))
        
        # Iterate through every tile
        for tile in self.geometries.keys():
            parts = tile.split(",")
            tile_x = parts[0]
            tile_y = parts[1]
            
            g = self.geometries[tile]

            #print("Checking tile: [" + tile_x + "," + tile_y + "] " + str(g.Corners))
            
            point = Point(latitude, longitude)

            # check each polygon to see if it contains the point
            for feature in g.data['features']:
                polygon = shape(feature['geometry'])
                if polygon.contains(point):
                    #print("Found tile! " + tile)
                    return tile_x, tile_y
        
        # If not found, return an error
        return "N/A", "N/A"            