'''
Basically a test script to see if this .shp (ESRI format) file can be imported as a shapely/geojson

Essentially this allows us to use government data to (hopefully) overlay and segment specific areas in our current data
According to the dataset research, this can probably also be done with potential sugarcane areas, rural properties, soil survey sites and also possibly before/after cyclone damages

Done:
- Read/convert to geoJSON

To Do:
- Make it work with a single tile
- Group property boundaries by satellite snapshots
- Integrate as a member of sentinel tilesnapshot class

Created by: @Andrew
'''

import os.path
import shapefile #new dependency!!
from shapely.geometry import shape
from json import dumps

path = os.path.expanduser("~/Desktop/propbound/Property_boundaries___DCDB_Lite.shp")
print("Reading shapefile..")
reader = shapefile.Reader(path)
fields = reader.fields[1:]
field_names = [field[0] for field in fields]
buffer = []
print("Shapefile loaded!")

#TODO group records according to data given eg. each coord of each snapshot

for sr in reader.shapeRecords():
    atr = dict(zip(field_names, sr.record))
    print("Reading record: " + str(atr))
    geom = sr.shape.__geo_interface__
    buffer.append(dict(type="Feature", geometry=geom, properties=atr))

#write GeoJSON file
from json import dumps
print("Writing to geoJson file..")
geojson = open("propboundtest.geoJson", "w")
geojson.write(dumps({"type": "FeatureCollection", "features":buffer}, indent=2) + "\n")
geojson.close()
print("Finished!")

