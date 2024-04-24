### Imports
import cv2
import numpy as np

### Variables and Default Values

# default image path
image = cv2.imread("data\source_images\PXL_20240326_134928380_2.jpg")

# Define the color-divisor to split the color space
Color_reduction_divisor = 64

# Define standard color depth
standard_color_depth = 255

# Define default gaussian blur value
gaussian_blur_value = 13


### Functions
def do_nothing(nothing):
    '''
    A function that does nothing
    required for cv2 trackbar
    '''
    pass

def reduce_color(image: np.ndarray, color_divisor: int) -> np.ndarray:
    '''
    Quantize the color space of an image by a predefined divisor
    '''
    # multiply by div and add div // 2 to get closer to the original value
    quantized = image // color_divisor * color_divisor + color_divisor // 2

    return quantized

def get_ROI(image: np.ndarray) -> np.ndarray:
    # select ROI (region of interest)
    roi = cv2.selectROI("Image", image)

    # extract ROI area as new array
    roi_image = image[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]

    return roi_image

def get_HSV_colorspace(image_HSV: np.ndarray) -> np.ndarray:
    # select ROI (region of interest) to get baseline values for background color space
    # initilize min and max HSV values with base values of pixel [0, 0]
    hue_min, sat_min, val_min = roi_image[0, 0]
    hue_max, sat_max, val_max = roi_image[0, 0]

    # iterate over ROI-pixels
    for x in range(roi_image.shape[0]):
        for y in range(roi_image.shape[1]):
            hue, sat, val = roi_image[x, y]
            # # debug
            # print(x, y)
            # print(hue, sat, val)

            ## extract HSV color range of ROI
            hue_min = min(hue, hue_min)
            hue_max = max(hue, hue_max)
            sat_min = min(sat, sat_min)
            sat_max = max(sat, sat_max)
            val_min = min(val, val_min)
            val_max = max(val, val_max)

    # # debug
    # print("Minimum H:", hue_min)
    # print("Maximum H:", hue_max)
    # print("Minimum S:", sat_min)
    # print("Maximum S:", sat_max)
    # print("Minimum V:", val_min)
    # print("Maximum V:", val_max)

    HSV_colorspace = np.array([hue_min, hue_max, sat_min, sat_max, val_min, val_max])

    return HSV_colorspace