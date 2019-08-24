#demo.py
from PIL import Image, ImageDraw
import glob
import os

#s2cloudless example .ipynb
import datetime

import matplotlib.pyplot as plt
from matplotlib.image import imread
import numpy as np

from s2cloudless import S2PixelCloudDetector, CloudMaskRequest

# The initial release contains only one tile, so lets hardcode its location
# here.  When you have more tiles, you can update this
TILE_X = 7680
TILE_Y = 10240
CLOUD_BANDS = ["B01","B02","B04","B05","B08","B8A","B09","B10","B11","B12"]


# The expected value of a Pixel in a mask file indicating that the pixel is
# within that region.  Tuple value, (Red, Green, Blue, Alpha)
IS_IN_MASK_PIXEL_VALUE = (0, 0, 0, 255)

# Tile width / height in pixels
TILE_WIDTH_PX = 512
TILE_HEIGHT_PX = 512


def get_mask_path(tile_x, tile_y, mask_type):
    path = f"./data/sentinel-2a-tile-{tile_x}x-{tile_y}y/masks/{mask_type}-mask.png"
    return path


# Open an image file and get all the pixels
def get_tile_pixels(tile_path):
    img = Image.open(tile_path)
    pixels = img.load()
    return pixels


# Get the pixels for an image file
def get_mask_pixels(tile_x, tile_y, mask_type):
    mask_path = get_mask_path(tile_x, tile_y, mask_type)
    return get_tile_pixels(mask_path)


def is_in_mask(mask_pixels, pixel_x, pixel_y):
    if mask_pixels[pixel_y, pixel_x] == IS_IN_MASK_PIXEL_VALUE:
        return True
    else:
        return False


def print_ascii_mask(tile_x, tile_y, mask_type):
    mask_pixels = get_mask_pixels(tile_x, tile_y, mask_type)

    # We don't really want to display ASCII art that is 512 characters long as it will be
    # too long to show in a terminal, so lets scale it
    scale_factor = 10

    width_in_chars = int(TILE_WIDTH_PX / scale_factor)
    height_in_chars = int(TILE_HEIGHT_PX / scale_factor)

    for x_char in range(0, width_in_chars - 1):
        for y_char in range(0, height_in_chars - 1):
            # Convert the character index back to actual pixels
            pixel_x = x_char * scale_factor
            pixel_y = y_char * scale_factor

            # is the pixel in my mask?
            in_mask = is_in_mask(mask_pixels, pixel_x, pixel_y)
            if in_mask:
                print("X", end="")
            else:
                print(" ", end="")

        # Print a newline at the end of each row
        print("\n", end="")


# Get a list of all the image tiles for a specific x,y coordinate
# for the specified band
def get_timeseries_image_paths(tile_x, tile_y, band, date):
    """
    I've been modified from demo.py!
    """

    path = f"./data/sentinel-2a-tile-{tile_x}x-{tile_y}y/timeseries/{tile_x}-{tile_y}-{band}-{date}.png"
    images = glob.glob(path)
    return images


def overlay_cloud_mask(image, mask=None, factor=1./255, figsize=(15, 15), fig=None):
    """
    Utility function for plotting RGB images with binary mask overlayed.
    """
    if fig == None:
        plt.figure(figsize=figsize)
    rgb = np.array(image)
    plt.imshow(rgb * factor)
    if mask is not None:
        cloud_image = np.zeros((mask.shape[0], mask.shape[1], 4), dtype=np.uint8)
        cloud_image[mask == 1] = np.asarray([255, 255, 0, 100], dtype=np.uint8)
        plt.imshow(cloud_image)

def plot_probability_map(rgb_image, prob_map, factor=1./255, figsize=(15, 30)):
    """
    Utility function for plotting a RGB image and its cloud probability map next to each other.
    """
    plt.figure(figsize=figsize)
    plot = plt.subplot(1, 2, 1)
    plt.imshow(rgb_image * factor)
    plot = plt.subplot(1, 2, 2)
    plot.imshow(prob_map, cmap=plt.cm.inferno)

def plot_cloud_mask(mask, figsize=(15, 15), fig=None):
    """
    Utility function for plotting a binary cloud mask.
    """
    if fig == None:
        plt.figure(figsize=figsize)
    plt.imshow(mask, cmap=plt.cm.gray)


#def plot_previews(data, dates, cols=4, figsize=(15, 15)):
def plot_previews(data, cols=4, figsize=(15, 15)):
    """
    Utility to plot small "true color" previews.
    """
    width = data[-1].shape[1]
    height = data[-1].shape[0]

    rows = data.shape[0] // cols + (1 if data.shape[0] % cols else 0)
    fig, axs = plt.subplots(nrows=rows, ncols=cols, figsize=figsize)
    for index, ax in enumerate(axs.flatten()):
        if index < data.shape[0]:
            #caption = '{}: {}'.format(index, dates[index].strftime('%Y-%m-%d'))
            ax.set_axis_off()
            ax.imshow(data[index] / 255., vmin=0.0, vmax=1.0)
            ax.text(0, -2, caption, fontsize=12, color='g')
        else:
            ax.set_axis_off()


#get TCI image paths
tci_paths = get_timeseries_image_paths(TILE_X, TILE_Y, "TCI", "2019-01-21")

tci_images = []
#get TCI images
for path in tci_paths:
    tci_images.append(np.asarray(Image.open(path)))
plt.imshow(tci_images[0])
plt.show()

cloud_detector = S2PixelCloudDetector(threshold=0.4, average_over=4, dilation_size=2)

bands = set()
dates = set()

for img_filename in os.listdir(f"./data/sentinel-2a-tile-{TILE_X}x-{TILE_Y}y/timeseries/"):
    if img_filename.endswith(".png"):
        tilex, tiley, band, year, month, day = img_filename.split(".")[0].split("-")

        bands.add(band)
        dates.add(year + "-" + month + "-" + day)

images = [np.arange(0, len(dates) - 1)]
i = 0
j = 0

for date in dates:
    images[i] = [np.arange(0, len(CLOUD_BANDS) - 1)]
    for band in CLOUD_BANDS:
        paths = get_timeseries_image_paths(TILE_X, TILE_Y, band, date)
        for path in paths:
            images[i][j] = np.append(images[i][j], Image.open(path))
        j = j + 1
    i = i + 1

## TODO: Not working, need to figure out proper array dimensions for
## cloud detector functions
## Documentation: https://github.com/sentinel-hub/sentinel2-cloud-detector/blob/master/s2cloudless/S2PixelCloudDetector.py

#cloud_images = np.asarray(images)
#cloud_probs = cloud_detector.get_cloud_probability_maps(cloud_images)
