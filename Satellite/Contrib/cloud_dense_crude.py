'''
Created on 20 Aug 2019

@author: Tyler

A very crude cloud detector that just looks at B02 for pixels above a magic number threshold (6000 out of 65535)

We will get Andrew's test program working with s2cloudless, which is great use of prior-art
but sounds like it needs a bit more work to get the image data into the required format
'''

from PIL import Image
import glob
import os

cloud_magic_threshold = 7000

timeseries_files = os.listdir("data/sentinel-2a-tile-7680x-10240y/timeseries")
max_intensity = 0
for filename in timeseries_files:
    if "B02" in filename:
        tile = Image.open("data/sentinel-2a-tile-7680x-10240y/timeseries/" + filename)
        datestr = filename[15:25]
        print("Processing: " + datestr)
        pixels = tile.load()
        for y in range(512):
            for x in range(512):
                intensity = pixels[y,x]
                if (intensity > max_intensity):
                    max_intensity = intensity
                if intensity > cloud_magic_threshold:
                    pixels[y,x] = 65535 # pure white
        tile.save("data/harvested/" + datestr + ".png")
        print("Max: " + str(max_intensity))