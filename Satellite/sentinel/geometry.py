'''
Created on 19 Aug 2019

@author: User
'''

import json
from geopy.distance import geodesic

class geometry(object):
    '''
    A class used to represent the "geometry" of a tile

    ...

    Attributes
    ----------
    BoundaryLongLat : array
        An array of five [longitude, latitude] Coordinate arrays,
        denoting the Boundary of the tile, clockwise from NW -> NE -> SE -> SW -> NW
        Note: The order of longitude/Latitude elements within the Coordinate arrays
        is the reverse of the Latitude/Longitude order that Google Maps and other
        things expect.
    
    BoundaryLatLong : array
        An array of five [latitude, longitude] Coordinate arrays,
        denoting the Boundary of the tile, clockwise from NW -> NE -> SE -> SW -> NW
        Note: This longitude/latitude order is what Google Map expects

    Corner_NW : tuple
        Latitude/Longitude tuple for NW corner
        
    Corner_NE : tuple
        Latitude/Longitude tuple for NE corner
        
    Corner_SE : tuple
        Latitude/Longitude tuple for SE corner
    
    Corner_SW : tuple
        Latitude/Longitude tuple for SW corner
        
    Corners : array
        Array of Latitude/Longitude tuples NW -> NE -> SE -> SW
        
    Methods
    -------
    print()
        Prints debug information about the object to the console
    '''


    def __init__(self, filename):
        '''
        Parameters
        ----------
        filename : str
            The name of the GeoJSON file to load.
            Either a full path, or assume it's relative to the current working directory
        '''
        with open(filename) as json_file:
            self.data = json.load(json_file)
            
            # Store Boundary in original Longitude/Latitude order
            self.BoundaryLongLat = self.data["features"][0]["geometry"]["coordinates"][0]
            
            # Store Boundary in more convenient Latitude/Longitude order
            self.BoundaryLatLong = [[]]
            for i in range(len(self.BoundaryLongLat)):
                self.BoundaryLatLong.append([self.BoundaryLongLat[i][1], self.BoundaryLongLat[i][0]])
            del self.BoundaryLatLong[0]
            
            # Store corners
            self.Corner_NW = (self.BoundaryLatLong[0][0], self.BoundaryLatLong[0][1])
            self.Corner_NE = (self.BoundaryLatLong[1][0], self.BoundaryLatLong[1][1])
            self.Corner_SE = (self.BoundaryLatLong[2][0], self.BoundaryLatLong[2][1])
            self.Corner_SW = (self.BoundaryLatLong[3][0], self.BoundaryLatLong[3][1])
            
            # Store corners as an array of tuples
            self.Corners = [self.Corner_NW, self.Corner_NE, self.Corner_SE, self.Corner_SW]
            
    def print(self):
        '''
        Prints debug information about the object to the console
        '''
        #pprint.pprint(self.data)
        print("Corners: " + str(self.Corners))
        # These coords are "backwards" as far as Google Maps is concerned, you need to reverse the order of latitude/longitude
        # First one is NW corner (top left) then they are clockwise NW -> NE -> SE -> SW -> NW
        print("Dist NW->NE: %3.4f km" % geodesic(self.Corner_NW, self.Corner_NE).kilometers)
        print("Dist NE->SE: %3.4f km" % geodesic(self.Corner_NE, self.Corner_SE).kilometers)
        print("Dist SE->SW: %3.4f km" % geodesic(self.Corner_SE, self.Corner_SW).kilometers)
        print("Dist SW->NW: %3.4f km" % geodesic(self.Corner_SW, self.Corner_NW).kilometers)
        