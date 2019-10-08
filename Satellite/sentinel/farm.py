'''
Created on 22 Sep 2019

@author: Tyler
'''

import glob
import os
import requests

import json
from shapely.geometry import Point, shape, GeometryCollection
import math
import geopy

from PIL import Image
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
        self.address  = address 
        self.coords   = self.addressGeocode(address)
        self.dates    = []
        self.img      = "N/A"
        self.boundary = "N/A"
        
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
    
    def getFeature(self):
        if (self.coords == "N/A"):
            self.boundary = "N/A"
            return "N/A"
        
        with open(os.path.join("geometries", "geo-x" + str(self.tile_x) + "-y" + str(self.tile_y) + ".geojson")) as fp:
            self.pic = json.load(fp)["features"][0]["geometry"]
        
        self.top_left_lat_long    = tuple([k for k in self.pic['coordinates'][0][0]])
        self.top_right_lat_long   = tuple([k for k in self.pic['coordinates'][0][1]])
        self.bottom_left_lat_long = tuple([k for k in self.pic['coordinates'][0][3]])
        
        self.top_left_lat_long_swap = self.swapLatLon(self.top_left_lat_long)
        self.top_right_lat_long_swap = self.swapLatLon(self.top_right_lat_long)
        self.bottom_left_lat_long_swap = self.swapLatLon(self.bottom_left_lat_long)
        
        self.bearing       = self.GetBearing(self.top_left_lat_long_swap, self.top_right_lat_long_swap)
        self.distance_hor  = self.GetDistanceMeters(self.top_left_lat_long_swap, self.top_right_lat_long_swap)
        self.distance_ver  = self.GetDistanceMeters(self.top_left_lat_long_swap, self.bottom_left_lat_long_swap)
        
        point = Point(self.coords['x'], self.coords['y'])
        
        with open("FullProperty.geojson") as f:
            features = json.load(f)["features"]
            
        for feature in features:
            if shape(feature['geometry']).contains(point):
                self.boundary = feature
                #print("FOUND IT!")
                return feature
                                                         
        return "N/A"
    
    def swapLatLon(self, coord):
        return (coord[1],coord[0])

    def GetBearing(self, pointA, pointB):
        if (type(pointA) != tuple) or (type(pointB) != tuple):
            raise TypeError("Only tuples are supported as arguments")

        lat1 = math.radians(pointA[0])
        lat2 = math.radians(pointB[0])

        diffLong = math.radians(pointB[1] - pointA[1])

        x = math.sin(diffLong) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

        initial_bearing = math.atan2(x, y)

        # Now we have the initial bearing but math.atan2 return values
        # from -180 to + 180 which is not what we want for a compass bearing
        # The solution is to normalize the initial bearing as shown below
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360

        return compass_bearing

    def GetDistanceMeters(self, lat_long_point1, lat_long_point2):
        return geopy.distance.geodesic(lat_long_point1, lat_long_point2).meters

    def GetLatLongFromPointBearingDistance(self, lat_long_point,bearing,distance):
        retVal=geopy.distance.geodesic(meters=distance).destination(lat_long_point, bearing)
        return retVal

    def GetLatLongForCoords(self, x, y, size_x=512, size_y=512):
        angle = 0
        if (x != 0):
            angle=math.atan(y/x)
        else:
            angle=1.570796 # 90 degrees in radians

        total_bearing = (self.bearing + math.degrees(angle) + 360) % 360
        distance_x    = self.distance_hor / size_x*x
        distance_y    = self.distance_ver / size_y*y
        
        distance_from_top_left = math.sqrt(distance_x**2 + distance_y**2)
        retLatLon = self.GetLatLongFromPointBearingDistance(self.top_left_lat_long_swap, total_bearing, distance_from_top_left)
        
        return self.swapLatLon(retLatLon)
    
    def getBoundary(self, size_x=512, size_y=512, force=False):
        # Return the img if already loaded
        if (self.img != "N/A"):
            return self.img
        
        # Find the "shape" of the boundary, if we haven't already
        if (self.boundary == "N/A"):
            self.boundary = self.getFeature()
        
        # If the "shape" of the boundary cannot be found, that's all we can do
        if (self.boundary == "N/A"):
            return "N/A"
        
        # Check if the "img" has already been cached, and just open it if it is there
        os.makedirs("cached_property_images", exist_ok=True)
        
        cache_file = os.path.join("cached_property_images", self.boundary['properties']['LOT'] + "_" + self.boundary['properties']['PLAN'] + ".png")

        if (os.path.exists(cache_file) and (force == False)):
            self.img = Image.open(cache_file)
            return self.img
        
        print("Isolating farm", end='')
        
        with open(os.path.join("geometries", "geo-x" + str(self.tile_x) + "-y" + str(self.tile_y) + ".geojson")) as f1:
            geo_json_features = json.load(f1)["features"]
        
        tile = GeometryCollection([shape(feature["geometry"]).buffer(0) for feature in geo_json_features])
        
        self.img = Image.new('RGBA', (size_x, size_y))
        
        count_hit = 0
        
        result = GeometryCollection()
        
        if shape(self.boundary["geometry"]).intersects(tile):
            result=result.union(shape(self.boundary["geometry"]).intersection(tile))
            
        if tile.intersects(result):
            for y in range(size_y):
                if (y % 15 == 0):
                    #print("y="+  str(y) + ", hits=" + str(count_hit))
                    print(".", end="")
                for x in range(size_x):
                    lat_long=self.GetLatLongForCoords(y, x)
                    if result.intersects(Point(lat_long)):
                        self.img.putpixel((y, x), (0, 0, 255, 255))  # Blue
                        count_hit += 1
        
        #print("Hits: " + str(count_hit))
        
        # Find the border
        for y in range(size_y):
            for x in range(size_x):
                # It is a border if it's not blue...
                if (self.img.getpixel((y, x)) != (0, 0, 255, 255)):
                    # And it has a neighbour that is blue
                    for j in range(y-1, y+2):
                        for i in range(x-1, x+2):
                            # Check for neighbour out of bounds, don't compare pixel to itself
                            if ((j >= 0) and (j < size_y) and (i >= 0) and (i < size_x) and ((j != y) or (i != x))):
                                if (self.img.getpixel((j, i)) == (0, 0, 255, 255)):
                                    # This is part of the border!
                                    self.img.putpixel((y, x), (255, 0, 0, 255))
                                    
        # Save the image to the cache
        self.img.save(cache_file)
        
        print(" done")
        
        return self.img
               
    # Helper function to get dateStr from full path of time series PNG
    def snapshotToDateStr(self, fullpath):
        # Find the actual filename part of the path
        baseName  = os.path.basename(fullpath)
        # Find the dateStr (YYYY-MM-DD)
        dateStart = len(str(self.tile_x)) + len(str(self.tile_y)) + 6
        dateEnd   = dateStart + 10
        dateStr   = baseName[dateStart:dateEnd]

        return dateStr
    
        