'''
Created on 26 Aug 2019

@author: User
'''

import numpy as np
from s2cloudless import S2PixelCloudDetector
from sentinel import tilesnapshot



t0 = tilesnapshot(7680, 10240, '2017-01-01')
t1 = tilesnapshot(7680, 10240, '2017-01-11')
t2 = tilesnapshot(7680, 10240, '2017-02-10')
t3 = tilesnapshot(7680, 10240, '2017-02-20')
t4 = tilesnapshot(7680, 10240, '2017-03-02')

numpy_bands = np.empty((5, 512, 512, 10))
    
def add_me(i, tile):
    print("Adding " + str(i))
    numpy_bands[i,:,:,0] = tile.numpy_layers['B01']
    numpy_bands[i,:,:,1] = tile.numpy_layers['B02']
    numpy_bands[i,:,:,2] = tile.numpy_layers['B04']
    numpy_bands[i,:,:,3] = tile.numpy_layers['B05']
    numpy_bands[i,:,:,4] = tile.numpy_layers['B08']
    numpy_bands[i,:,:,5] = tile.numpy_layers['B8A']
    numpy_bands[i,:,:,6] = tile.numpy_layers['B09']
    numpy_bands[i,:,:,7] = tile.numpy_layers['B10']
    numpy_bands[i,:,:,8] = tile.numpy_layers['B11']
    numpy_bands[i,:,:,9] = tile.numpy_layers['B12']

add_me(0, t0)
add_me(1, t1)
add_me(2, t2)
add_me(3, t3)
add_me(4, t4)

print("Added all tiles")

print("Detecting clouds")
cloud_detector  = S2PixelCloudDetector(threshold=0.4, average_over=4, dilation_size=2)
cloud_masks = cloud_detector.get_cloud_masks(numpy_bands)
print("... done")

print(cloud_masks[1])

