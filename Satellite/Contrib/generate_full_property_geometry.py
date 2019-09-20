'''
#####################################################
# PLEASE READ ME BEFORE ATTEMPTING TO RUN THIS FILE #
#####################################################
Make sure you have the "properties" folder (https://drive.google.com/open?id=1eW8d2zRiCNu2NQxJaPAhTnYyYtpVw5za) located in the "mask-generation" folder

Place and run me in the "mask-generation" folder from the phase 2 data
'''
import json
from PIL import Image
from shapely import geometry
import shapefile
import configparser as ConfigParser
from SugarUtils import *
import time

#Initialise the Config File
config = ConfigParser.ConfigParser()
config.read('geo.config')

FULL_IMAGE_GEOMETRY=config.get('Master Image', 'FULL_GEOMETRY_PATH')

start = time.time()

with open(FULL_IMAGE_GEOMETRY) as f:
    pic = json.load(f)["geometry"]


#Generates FullProperty.geojson in "mask-generation" folder
if __name__ == "__main__":

    print("Loading shapefile...")
    properties = shapefile.Reader("./properties/Property_boundaries___DCDB_Lite.shp")

    print("Loaded!")
    print("Loading records from shapefile...")
    records = properties.shapeRecords()

    print("Loading full image geometry...")
    tile = geometry.shape(pic)


    print("Generating file ......")

    i = 0
    fields = properties.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []
    for property in records:
        if geometry.shape(property.shape).intersects(tile):
            i = i + 1
            print("Writing " + str(i) + " property to geoJSON..")
            prop = records.pop(records.index(property))
            atr = dict(zip(field_names, prop.record))
            geom = prop.shape.__geo_interface__

            buffer.append(dict(type="Feature", geometry=geom, properties=atr))
        #else:
            #print(".", end='')
            
    #Write and save geoJSON here
    geojson = open("FullProperty.geojson", "w")
    geojson.write(json.dumps({"type": "FeatureCollection","features": buffer}, indent=2) + "\n")
    end = time.time()

    print("File Generation completed")
    print("execution time is", end-start)
