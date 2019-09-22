'''
Created on 22 Sep 2019

@author: Tyler
'''

import glob
import os
import requests

#import sentinel.geometry_list as geometry_list

class farm(object):
    '''
    classdocs
    '''


    def __init__(self, address, gl):
        '''
        Constructor
        '''
    
        # Geocode address into coords
        self.address = address 
        self.coords  = self.addressGeocode(address)
        self.dates   = []
        
        if (self.coords != "N/A"):
            # Load geometry data
            # Load tile geometry data
            #gl = geometry_list("geometries")

            # Find the file
            self.tile_x, self.tile_y = gl.findTile(latitude=self.coords['x'], longitude=self.coords['y'])
        
            # Find available snapshots
            timeSeriesFilter = os.path.join("sugarcanetiles", str(self.tile_x) + "-" + str(self.tile_y) + "-TCI-*.png")
            timeSeriesList   = glob.glob(timeSeriesFilter)
            
            for snapshot_i in range(len(timeSeriesList)):
                self.dates.append(self.snapshotToDateStr(timeSeriesList[snapshot_i]))
                
                
        else:
            self.tile_x = "N/A"
            self.tile_y = "N/A"
            print("Unable to locate farm: [" + self.address + "]")
        
        
    def addressGeocode(self, address, outSR = "4326"):
        geoCodeUrl = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
    
        #clean up the address for url encoding
        address = address.replace(" ", "+")
        address = address.replace(",", "%3B")

        #send address to geocode service
        lookup = requests.get(geoCodeUrl + "?SingleLine=" + address + "&outSR=" + outSR + "&maxLocations=1&f=pjson")
        data = lookup.json()

        if data["candidates"]:
            #results
            coords = data["candidates"][0]["location"]
            return coords
        else:
            #no results
            return "N/A"
        
        
    # Helper function to get dateStr from full path of time series PNG
    def snapshotToDateStr(self, fullpath):
        # Find the actual filename part of the path
        baseName  = os.path.basename(fullpath)
        # Find the dateStr (YYYY-MM-DD)
        dateStart = len(str(self.tile_x)) + len(str(self.tile_y)) + 6
        dateEnd   = dateStart + 10
        dateStr   = baseName[dateStart:dateEnd]

        return dateStr    
        