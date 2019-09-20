'''
#####################################################
# PLEASE READ ME BEFORE ATTEMPTING TO RUN THIS FILE #
#####################################################

Make sure you have this in geo.config under [Master Image]
    - PROP_GEO_JSON_FOLDER =./prop_geometries
    - FULL_PROP_GEOMETRY_PATH=FullProperty.geojson

Create a directory called "prop_geometries"

!!!Run me ONLY after running "generate_full_property_geometry.py"!!!
'''
import os
import geopandas as gpd
import json
from shapely import geometry
import configparser as ConfigParser
from SugarUtils import *
import time

#Initialise the Config File
config = ConfigParser.ConfigParser()
config.read('geo.config')

#Make sure these are in the config file!
FULL_PROP_GEOMETRY_PATH=config.get('Master Image', 'FULL_PROP_GEOMETRY_PATH')
GEO_JSON_FOLDER=config.get('Master Image', 'GEO_JSON_FOLDER')

start = time.time()

with open(FULL_PROP_GEOMETRY_PATH) as f:
    properties = json.load(f)["features"]

def GeneratePropertyGeoJson(tileXPos,tileYPos,geoJSONPath,outputFileName):

    buffer = []

    with open(geoJSONPath) as f:
      geo_json_features = json.load(f)["features"]

    tile=geometry.GeometryCollection([geometry.shape(feature["geometry"]).buffer(0) for feature in geo_json_features])


    for k in properties:
        if geometry.shape(k["geometry"]).intersects(tile):
            buffer.append(dict(type="Feature", geometry=k["geometry"], properties=k["properties"]))

    #Write to file
    geojson = open(outputFileName, "w")
    geojson.write(json.dumps({"type": "FeatureCollection","features": buffer}, indent=2) + "\n")



#Generates prop-x-y.geojson for each tile
if __name__ == "__main__":
    ranStartX=0
    ranEndX=21
    ranStartY=0
    ranEndY=21
    #the 512 by 512 bit tiles make for 21 rows and 21 columns in the case of sentinel 2a images.

    for x in range(ranStartX,ranEndX):
        for y in range(ranStartY,ranEndY):
            posX=x
            posY=y
            xCoord=posX*GRID_WIDTH
            yCoord=posY*GRID_HEIGHT
            tileName=GetTileName(xCoord,yCoord)
            GeoJsonFile=GetGeoJSONName(xCoord,yCoord)
            #propGeoJson=GetPropGeoJSONName(xCoord,yCoord)
            propGeoJson=os.path.join("prop_geometries", "prop-"+ "x"+str(xCoord)+"-"+"y"+str(yCoord)+".geojson")
            print("All Names", posX,posY,GeoJsonFile,propGeoJson)
            GeneratePropertyGeoJson(posX,posY,GeoJsonFile,propGeoJson)
            print("Generated Geometry of {0} and {1} tiles ".format(x,y))


    end = time.time()
    print("Finished!")
    print("execution time is", end-start)
