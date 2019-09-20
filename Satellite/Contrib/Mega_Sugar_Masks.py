########################################################
# Copyright  Growing Data Pty Ltd, Australia
# AUTHOR: Michael-James Coetzee, Amit Wats
# EMAIL: mj@growingdata.com.au, amit@growingdata.com.au
########################################################

import geopandas as gpd
import geopy.distance
import json
import math
import time

from math import atan,degrees,sqrt
from os import path
from PIL import Image
from shapely import geometry


# Adjust paths for your environment!
FULL_GEOMETRY_PATH ='C:/Satellites/Phase-2-2-Data/Phase02-DataDelivery/FullGeometry.json'
FULL_IMAGE_PATH ='C:/Satellites/Phase-2-2-Data/Phase02-DataDelivery/FullImage.png'
GEO_JSON_FOLDER ='C:/Satellites/Phase-2-2-Data/Phase02-DataDelivery/geometries'
MASTER_SUGAR_DATA_GEOJSON_PATH='C:/Satellites/Phase-2-2-Data/Phase02-DataDelivery/FullSugar.geojson'
TILE_IMAGE_FOLDER='C:/Satellites/Phase-2-2-Data/Phase02-DataDelivery/sugarcanetiles'
MASK_IMAGE_FOLDER='masks'
GRID_WIDTH=512
GRID_HEIGHT=512



def GetBearing(pointA, pointB):
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

def GetDistanceMeters(lat_long_point1, lat_long_point2):
    return geopy.distance.geodesic(lat_long_point1, lat_long_point2).meters

def GetLatLongFromPointBearingDistance(lat_long_point,bearing,distance):
    retVal=geopy.distance.geodesic(meters=distance).destination(lat_long_point,bearing)
    return retVal





print("Tile Image Folder: [" + TILE_IMAGE_FOLDER + "]")

def GetName(xPos,yPos):
    return "x"+str(xPos)+"-y"+str(yPos)

def GetFullPath(folder,prefix,ext,xPos,yPos):
    return folder+"/"+prefix+GetName(xPos,yPos)+ext

def GetTileName(xPos,yPos):
    return GetFullPath(TILE_IMAGE_FOLDER,"tile-",".png",xPos,yPos)

def GetGeoJSONName(xPos,yPos):
    return GetFullPath(GEO_JSON_FOLDER,"geo-",".geojson",xPos,yPos)

def GetMaskName(xPos,yPos):
    return GetFullPath(MASK_IMAGE_FOLDER,"mask-",".png",xPos,yPos)



#Prevent Image from throwing warning as the
#Image File is Big
Image.MAX_IMAGE_PIXELS = 1000000000


with open(FULL_GEOMETRY_PATH) as f:
    pic = json.load(f)["geometry"]

fullImage=Image.open(FULL_IMAGE_PATH)
fullImageWidth,fullImageHeight = fullImage.size


#we will have 2 lines across and down.
# so staring in top left corner each datetime and denotiong p as 512/dimension(fullImageWidth or fullImageHeight depending)
# go right p portrion across TR tile, down p portion to get BL tile and go portion across followed by p portion down to get BR tile
#note: assumption pictures are squares! Check lines for parallel
# approach scale in x p portion of (x2-x1) and for y scale p portion of (y2-y1) at the started off set of (x1,y1) + current_tile_offset *scale across approach*

top_left_lat_long=tuple([k for k in pic['coordinates'][0][0]])
top_right_lat_long=tuple([k for k in pic['coordinates'][0][1]])
bottom_right_lat_long=tuple([k for k in pic['coordinates'][0][2]])
bottom_left_lat_long=tuple([k for k in pic['coordinates'][0][3]])

def saveGeo(TL,TR,BR,BL,x_bit,y_bit):
    point_TL=geometry.Point(TL[0],TL[1])
    point_TR=geometry.Point(TR[0],TR[1])
    point_BR=geometry.Point(BR[0],BR[1])
    point_BL=geometry.Point(BL[0],BL[1])
    tile= geometry.Polygon([p.x,p.y] for p in [point_TL,point_TR,point_BR,point_BL])
    tile_geoseries=gpd.GeoSeries([tile])
    tile_gpd= gpd.GeoDataFrame(geometry=tile_geoseries)
    tile_gpd.crs = {'init': 'epsg:4326', 'no_defs': True}
    tile_gpd.to_file(GetGeoJSONName(x_bit,y_bit), driver="GeoJSON")

# the GeoLibrary file uses a convention where the
# latitute and longitute are in opposite orders
# This function heps swap the position while passing parameters
# As well as when results from the library are returned
def swapLatLon(coord):
    return (coord[1],coord[0])

def CreateCroppedImage(coords):
    tile=fullImage.crop((coords[0][0],coords[0][1],coords[2][0],coords[2][1]))
    tile.save(GetTileName(coords[0][0],coords[0][1]))

def GetFourPositions(x,y):
    top_left_pos=(GRID_WIDTH*x,GRID_HEIGHT*y)
    top_right_pos=(GRID_WIDTH*(x+1),GRID_HEIGHT*y)
    bottom_left_pos=(GRID_WIDTH*x,GRID_HEIGHT*(y+1))
    bottom_right_pos=(GRID_WIDTH*(x+1),GRID_HEIGHT*(y+1))
    return [top_left_pos,top_right_pos,bottom_right_pos, bottom_left_pos]

def GetLatLongForCoords(x,y):
    angle=0
    if x!=0:
        angle=atan(y/x)
    else :
        angle=1.570796 # 90 degrees in radians
    bearing=GetBearing(swapLatLon(top_left_lat_long),swapLatLon(top_right_lat_long))
    total_bearing=(bearing+degrees(angle) + 360) % 360
    distance_hor=GetDistanceMeters(swapLatLon(top_left_lat_long),swapLatLon(top_right_lat_long))
    distance_ver=GetDistanceMeters(swapLatLon(top_left_lat_long),swapLatLon(bottom_left_lat_long))
    distance_x=distance_hor/fullImageWidth*x
    distance_y=distance_ver/fullImageHeight*y
    distance_from_top_left=sqrt(distance_x**2+distance_y**2)
    retLatLon=GetLatLongFromPointBearingDistance(swapLatLon(top_left_lat_long),total_bearing,distance_from_top_left)
    return swapLatLon(retLatLon)

# Can be invoked externally to generate the
# Geo JSON of the x'th and y'th square position
def GenerateAndSaveTileGeo(x,y):
    fourLatLongPositions=[GetLatLongForCoords(r[0],r[1]) for r in GetFourPositions(x,y)]
    saveGeo(fourLatLongPositions[0],fourLatLongPositions[1],fourLatLongPositions[2],fourLatLongPositions[3],x*GRID_WIDTH,y*GRID_HEIGHT)
    fourCoordinates=GetFourPositions(x,y)
    CreateCroppedImage(fourCoordinates)

# The main method generates the GEO JSON files in the configured
# folder



RAWNESS=1 #this is used in generating the mask image.
# RAWNESS For production is 1.
# For testing it can vary betwen 1 to 6
# Increasing it generates the mask faster with lots of parts missed out
# varying it makes it human eye testable
# When using for generation SHOULD BE 1


start=time.time()

with open(MASTER_SUGAR_DATA_GEOJSON_PATH) as f:
    features = json.load(f)["features"]

##################################################################################
# GenerateMask(tileXPos,tileYPos,tileImageFilePath,geoJSONPath,outputFileName):
##################################################################################
# This is the key method to generate masks. It generates one mask in the
# specified location by reading from theGEO_JSON_FOLDER given locations
# tileXPos= the X position of the grid fGEO_JSON_FOLDERrom top left. first grid=0, second grid=1, etc
# tileYPos= the Y position of the grid fGEO_JSON_FOLDERrom top left. first grid=0, second grid=1, etc

def GenerateMask(tileXPos,tileYPos,tileImageFilePath,geoJSONPath,outputFileName):
    with open(geoJSONPath) as f:
        geo_json_features = json.load(f)["features"]

    tile=geometry.GeometryCollection([geometry.shape(feature["geometry"]).buffer(0) for feature in geo_json_features])
    img = Image.open(tileImageFilePath)

    pixels=img.load()


    result=geometry.GeometryCollection()

    for k in features:
        #print(".", end=" ")
        if geometry.shape(k["geometry"]).intersects(tile):
            result=result.union(geometry.shape(k["geometry"]).intersection(tile))
            
    if tile. intersects(result):
        for i in range(0,img.size[0],RAWNESS):
            for j in range(0,img.size[1],RAWNESS):
                lat_long=GetLatLongForCoords(GRID_WIDTH*(tileXPos)+i,GRID_HEIGHT*(tileYPos)+j)
                if result.intersects(geometry.Point(lat_long)):
                    pixels[i,j]=(0,0,0)
        img.save(outputFileName)





ranStartX=0
ranEndX=21
ranStartY=0
ranEndY=21

#the 512 by 512 bit tiles make for 21 rows and 21 columns in the case of sentinel 2a images.



for x in range(ranStartX,ranEndX):
    print("Starting x=" + str(x))
    for y in range(ranStartY,ranEndY):
        print("Starting y=" + str(y))
        posX=x
        posY=y
        xCoord=posX*GRID_WIDTH
        yCoord=posY*GRID_HEIGHT
        #tileName=GetTileName(xCoord,yCoord)
        #tileName = TILE_IMAGE_FOLDER + "/1536-1024-TCI-2019-08-09.png"
        tileName = TILE_IMAGE_FOLDER + "/" + str(xCoord) + "-" + str(yCoord) + "-TCI-2019-08-09.png"
        if (path.exists(tileName)):
            GeoJsonFile=GetGeoJSONName(xCoord,yCoord)
            maskOutput=GetMaskName(xCoord,yCoord)
            print("All Names", posX,posY,tileName,GeoJsonFile,maskOutput)
            GenerateMask(posX,posY,tileName,GeoJsonFile,maskOutput)
            print("Generated Mask of {0} and {1} tiles ".format(x,y))
        else:
            print("No tiles for: " + str(xCoord) + "-" + str(yCoord))

print("Finished!")
end=time.time()
print("execution time is", end-start)
