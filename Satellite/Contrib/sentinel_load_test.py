'''
Created on 26 Aug 2019

@author: User
'''

#import matplotlib.pyplot as plt
#import numpy as np
from PIL import Image

from sentinel import tilesnapshot


datestr = '2017-03-02'


t = tilesnapshot(7680, 10240, datestr)
t.print()

tile = Image.open("data/sentinel-2a-tile-7680x-10240y/timeseries/7680-10240-B02-" + datestr + ".png")

print("Processing: " + datestr)
pixels = tile.load() 
mask = t.cloud_masks[0]

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

x=100
y=100
print("Prob 0/0: " + str(t.cloud_probs[0][y][x]))
print("Mask 0/0: " + str(t.cloud_masks[0][y][x]))
print("B01  0/0: " + str(t.numpy_bands[0][y][x][0]) + " = " + str(t.numpy_raw["B01"][y][x]))
print("B02  0/0: " + str(t.numpy_bands[0][y][x][1]) + " = " + str(t.numpy_raw["B02"][y][x]))
print("B04  0/0: " + str(t.numpy_bands[0][y][x][2]) + " = " + str(t.numpy_raw["B04"][y][x]))
print("B05  0/0: " + str(t.numpy_bands[0][y][x][3]) + " = " + str(t.numpy_raw["B05"][y][x]))
print("B08  0/0: " + str(t.numpy_bands[0][y][x][4]) + " = " + str(t.numpy_raw["B08"][y][x]))
print("B8A  0/0: " + str(t.numpy_bands[0][y][x][5]) + " = " + str(t.numpy_raw["B8A"][y][x]))
print("B09  0/0: " + str(t.numpy_bands[0][y][x][6]) + " = " + str(t.numpy_raw["B09"][y][x]))
print("B10  0/0: " + str(t.numpy_bands[0][y][x][7]) + " = " + str(t.numpy_raw["B10"][y][x]))
print("B11  0/0: " + str(t.numpy_bands[0][y][x][8]) + " = " + str(t.numpy_raw["B11"][y][x]))
print("B12  0/0: " + str(t.numpy_bands[0][y][x][9]) + " = " + str(t.numpy_raw["B12"][y][x]))


band="B04"

max_intensity = -1
max_y = -1
max_x = -1

for i in range(512):
    for j in range(512):
        if (t.numpy_raw[band][j][i] > max_intensity):
            max_intensity = t.numpy_raw[band][j][i]
            max_y = j
            max_x = i
print("Max intensity: " + str(max_intensity) + " at (X=" + str(max_x) + ", Y=" + str(max_y) + ")")

        

import matplotlib
import seaborn as sns

matplotlib.image.imsave(band + ".png", t.numpy_raw[band])

matplotlib.image.imsave('mask.png', t.cloud_masks[0])  # I DID IT I DID IT I DID IT!


plot = sns.distplot(t.numpy_raw[band].ravel())
figure = plot.get_figure()
figure.savefig("figure_" + band + ".png")

print("ALL DONE")


