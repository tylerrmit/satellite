'''
Created on 19 Aug 2019

@author: User
'''

import json
import pprint

class metadata(object):
    '''
    A "metadata" object belonging to Tile Snapshot (a tile at a point-in-time)
    
    Attributes
    ----------
    data : dictionary
        A full copy of the JSON file, loaded as a nested dictionary
        
    CloudCover : str
        The "cloudCover" element extracted from the metadata
    
    Centroid : tuple
        The "centroid/coordinates" element extracted from the metadata,
        formatted as a latitude/longitude tuple
        
    StartDate : str
        The date part of the "startDate" element extracted from the metadata
    '''


    def __init__(self, filename):
        '''
        filename : str
            The name of the Metadata JSON file to load.
            Either a full path, or assume it's relative to the current working directory
        '''
        with open(filename) as json_file:
            self.data = json.load(json_file)
            self.CloudCover = self.data["metadata"]["cloudCover"]
            self.Centroid   = (self.data["metadata"]["centroid"]["coordinates"][1], self.data["metadata"]["centroid"]["coordinates"][0])
            self.StartDate  = self.data["metadata"]["startDate"].split("T")[0]
            
    def print(self):
        '''
        Prints debug information about the object to the console
        '''
        pprint.pprint(self.data)
        print("CloudCover: " + str(self.CloudCover))
        print("Centroid:   " + str(self.Centroid))
        print("StartDate:  " + str(self.StartDate))