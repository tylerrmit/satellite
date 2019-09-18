'''
Created on 17 Sep 2019

@author: Tyler
'''

from sentinel.cloudmask import cloudmask
from sentinel.harvestmask import harvestmask

tile_x = 7680
tile_y = 10240

# Generate cloud mask
c = cloudmask()
#c.generate_cloud_mask(tile_x=tile_x, tile_y=tile_y)

h = harvestmask()
h.generate_harvest_mask(tile_x=tile_x, tile_y=tile_y)

print("FINISHED!")