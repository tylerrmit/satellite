'''
Created on 21 Sep 2019

@author: Tyler

Output all images required for one tile
'''

from generate_cloud_masks_s2cloudless import *
from generate_harvest_masks_nvdi      import *
from delta_harvest_masks              import *
from delta_nvdi_intensity             import *

def all_for_one_tile(tile_x, tile_y):
    # Generate cloud masks
    generate_cloud_masks(tile_x=tile_x, tile_y=tile_y)
    
    # Generate harvest masks and NVDI intensity
    generate_harvest_masks_nvdi(tile_x=tile_x, tile_y=tile_y)
    
    # Get change in harvest masks to identify when each pixel was harvested
    delta_harvest_masks(tile_x=tile_x, tile_y=tile_y)
    
    # Get NVDI intensity, adjusted for cloudy pixels
    delta_nvdi_intensity(tile_x=tile_x, tile_y=tile_y)
    
    
if __name__ == "__main__":
    # Test delta harvest on phase1 example tile
    all_for_one_tile(tile_x=7680, tile_y=10240)
    