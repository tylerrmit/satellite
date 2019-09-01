'''
Created on 20 Aug 2019

@author: Tyler

A very crude cloud detector that just looks at B02 for pixels above a magic number threshold (6000 out of 65535)

We will get Andrew's test program working with s2cloudless, which is great use of prior-art
but sounds like it needs a bit more work to get the image data into the required format
'''

from PIL import Image
import os

tile_x = 7680
tile_y = 10240
size_x = 512
size_y = 512

cloud_magic_threshold = 4000

# Location for output
#save_location = "data\\sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y\\Masks\\crude_cloud_masks"
save_location = os.path.join("data", "sentinel-2a-tile-" + str(tile_x) + "x-" + str(tile_y) + "y", "Masks", "crude_cloud_masks")
os.makedirs(save_location, exist_ok=True)

timeseries_files = os.listdir("data/sentinel-2a-tile-7680x-10240y/timeseries")
max_intensity    = 0

for filename in timeseries_files:
    if "B02" in filename:
        tile = Image.open("data/sentinel-2a-tile-7680x-10240y/timeseries/" + filename)
        dateStr = filename[15:25]
        print("Processing: " + dateStr)
        pixels = tile.load()
        
        # Create new mask
        img = Image.new('RGBA', (size_x, size_y))
         
        for y in range(size_y):
            for x in range(size_x):
                intensity = pixels[y,x]
                if (intensity > max_intensity):
                    max_intensity = intensity
                if intensity > cloud_magic_threshold:
                    img.putpixel((y, x), (0,0,0,255)) # Opaque
                else:
                    img.putpixel((y, x), (0,0,0,0))   # Transparent
        
        #output_file = save_location + "\\" + dateStr + ".png"
        output_file = os.path.join(save_location, dateStr + ".png")
        print("Writing [" + output_file + "]")
        img.save(output_file)
    
        print("Max: " + str(max_intensity))