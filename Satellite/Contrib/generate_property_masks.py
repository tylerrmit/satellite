'''
#####################################################
# PLEASE READ ME BEFORE ATTEMPTING TO RUN THIS FILE #
#####################################################

Make sure you have this in "geo.config" under [Master Image]
    - PROP_GEO_JSON_FOLDER =./prop_geometries
    - FULL_PROP_GEOMETRY_PATH=FullProperty.geojson

Make sure you have these functions and definitions in "SugarUtils.py"
    - PROP_GEO_JSON_FOLDER=config.get('Master Image', 'PROP_GEO_JSON_FOLDER')
    - PROP_MASK_IMAGE_FOLDER = config.get('Master Image', 'PROP_MASK_IMAGE_FOLDER')

    - def GetPropGeoJSONName(xPos,yPos):
        return GetFullPath(PROP_GEO_JSON_FOLDER,"prop-",".geojson",xPos,yPos)
    - def GetPropMaskName(xPos,yPos):
        return GetFullPath(PROP_MASK_IMAGE_FOLDER,"mask-",".png",xPos,yPos)

!!!Run me ONLY after running "generate_property_geojson.py"!!!
'''
import os
import geopandas as gpd
import json
from shapely import geometry
from PIL import Image
import configparser as ConfigParser
from GenerateGeoJSON import GetLatLongForCoords
from SugarUtils import *
import time

#Initialise the Config File
config = ConfigParser.ConfigParser()
config.read('geo.config')

GRID_WIDTH=int(config.get('Master Image', 'GRID_WIDTH'))
GRID_HEIGHT=int(config.get('Master Image', 'GRID_HEIGHT'))
TILE_IMAGE_FOLDER=config.get('Master Image', 'TILE_IMAGE_FOLDER')
MASK_IMAGE_FOLDER=config.get('Master Image', 'MASK_IMAGE_FOLDER')
GEO_JSON_FOLDER=config.get('Master Image', 'GEO_JSON_FOLDER')
PROP_GEO_JSON_FOLDER=config.get('Master Image', 'PROP_GEO_JSON_FOLDER')
PROP_MASK_IMAGE_FOLDER=config.get('Master Image','PROP_MASK_IMAGE_FOLDER')

#Make sure these are in the config file!
GEO_JSON_FOLDER=config.get('Master Image', 'GEO_JSON_FOLDER')

RAWNESS=1 #this is used in generating the mask image.
# RAWNESS For production is 1.
# For testing it can vary betwen 1 to 6
# Increasing it generates the mask faster with lots of parts missed out
# varying it makes it human eye testable
# When using for generation SHOULD BE 1


start = time.time()

def GeneratePropertyMask(tileXPos,tileYPos,tileImageFilePath,geoJSONPath,propGeoJSONPath,outputFileName):
    with open(geoJSONPath) as f:
        geo_json_features = json.load(f)["features"]

    with open(propGeoJSONPath) as f:
        property_geo_json_features = json.load(f)["features"]

    tile=geometry.GeometryCollection([geometry.shape(feature["geometry"]).buffer(0) for feature in geo_json_features])

    properties = geometry.GeometryCollection([geometry.shape(feature["geometry"]).buffer(0) for feature in property_geo_json_features])

    img = Image.open(tileImageFilePath)


    pixels=img.load()

    result = geometry.GeometryCollection()

    '''
    for i in range(0,img.size[0],RAWNESS):
        for j in range(0,img.size[1],RAWNESS):
            lat_long=GetLatLongForCoords(GRID_WIDTH*(tileXPos)+i,GRID_HEIGHT*(tileYPos)+j)
            for property in properties:
                if property.exterior.intersects(geometry.Point(lat_long)):
                    pixels[i,j]=(255,0,0)
    '''
    for property in properties:
        if property.intersects(tile):
            result = result.union(geometry.shape(property).intersection(tile))

    if tile.intersects(result):
        for i in range(0,img.size[0],RAWNESS):
            for j in range(0,img.size[1],RAWNESS):
                lat_long=GetLatLongForCoords(GRID_WIDTH*(tileXPos)+i,GRID_HEIGHT*(tileYPos)+j)
                if result.intersects(geometry.Point(lat_long)):
                    pixels[i,j]=(255,0,0)


    img.save(outputFileName)




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
            propGeoJson=GetPropGeoJSONName(xCoord,yCoord)
            propMaskOutput=GetPropMaskName(xCoord,yCoord)
            print("All Names", posX,posY,tileName,GeoJsonFile,propGeoJson,propMaskOutput)
            GeneratePropertyMask(posX,posY,tileName,GeoJsonFile,propGeoJson,propMaskOutput)
            print("Generated Mask of {0} and {1} tiles ".format(x,y))


    end = time.time()
    print("Finished!")
    print("execution time is", end-start)
