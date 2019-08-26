'''
Created on 26 Aug 2019

@author: User
'''

#import matplotlib.pyplot as plt
#import numpy as np
from PIL import Image

from sentinel import tilesnapshot


datestr = '2018-01-26'


t = tilesnapshot(7680, 10240, datestr)
t.print()

tile = Image.open("data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-B02-" + datestr + ".png")

print("Processing: " + datestr)
pixels = tile.load() 
mask = t.cloud_mask[0]

for y in range(512):
    for x in range(512):
        if (mask[y,x] > 0):
            pixels[y,x] = 0 # black as the night itself
        else:
            pixels[y,x] = 65535 # pure white
tile.save("data/s2cloud/" + datestr + ".png")
print("Done.")
        
#import numpy as np
#import pprint
#import PIL
#from PIL import Image

#fullPath = 'data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-B01-2017-11-27.png'
#img = Image.open(fullPath)
#layer_image = img.load()
#layer_numpy = np.array(layer_image)

#I = np.asarray(PIL.Image.open(fullPath))

#def f(x):
#        return x / 65535

#vf = np.vectorize(f)

#I2 = np.array([f(xi) for xi in I])

#pprint.pprint(I2)