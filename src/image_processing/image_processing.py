### Imports
import numpy as np
import cv2
from PIL import Image, ImageDraw
import random

### Defaults

# Define the color-divisor to split the color space 
color_reduction_divisor = 64

# Define standard color depth
standard_color_depth = 255

# Define default gaussian blur value
gaussian_blur_value = 1

# default image path
default_image_path = (r"data\source_images\PXL_20240326_134928380_2.jpg")

# predefine some colors
colors = [(0,255,0), (0,0,255), (255,0,0), (255,0,255), (0,255,255), (255,255,0), (128,192,128), (192,192,192), (128,0,128), (128,128,0)]  # Define different colors

# def random_rgb_generator(n):
#     colors = []
#     for _ in range(n):
#         r = random.randint(0, 255)
#         g = random.randint(0, 255)
#         b = random.randint(0, 255)
#         colors.append((r, g, b))

#     return colors

# colors = random_rgb_generator(10)
def brighten_image(image, amount):
    img_bright = cv2.convertScaleAbs(image, beta=amount)
    return img_bright

def blur_image(image, amount):
    blur_img = cv2.GaussianBlur(image, (0, 0), amount)
    return blur_img

def enhance_details(img):
    hdr = cv2.detailEnhance(img, sigma_s=12, sigma_r=0.15)
    return hdr

def proportional_resize_image(image, max_height=None, max_width=None):
    width, height = image.size

    if max_height and (max_width is None or (height / width) > (max_height / max_width)):
        # Resize based on height
        new_height = max_height
        new_width = int(width * (max_height / height))
        scaling_factor = new_height / height
    else:
        # Resize based on width
        new_width = max_width
        new_height = int(height * (max_width / width))   
        scaling_factor = new_width / width   

    image = image.resize((new_width, new_height))
    return image, scaling_factor

def reduce_color(image: np.ndarray, color_divisor: int) -> np.ndarray:
    '''
    Quantize the color space of an image by a predefined divisor
    '''
    # multiply by div and add div // 2 to get closer to the original value
    quantized_image = image // color_divisor * color_divisor + color_divisor // 2

    return quantized_image

def get_ROI(image: np.ndarray) -> np.ndarray:
    # select ROI (region of interest)
    roi = cv2.selectROI("Image", image)

    # extract ROI area as new array
    roi_image = image[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]

    return roi_image

def get_HSV_colorspace(image_HSV: np.ndarray) -> np.ndarray:
    """
    Calculate the HSV color space of an image.
    Args:
        image (np.ndarray): The input image, must be HSV.
    Returns:
        np.ndarray: An array containing the minimum and maximum HSV values of the image.
    """
    # initilize min and max HSV values with base values of pixel [0, 0]
    hue_min, sat_min, val_min = image_HSV[0, 0]
    hue_max, sat_max, val_max = image_HSV[0, 0]
    # print("start")
    # iterate over ROI-pixels
    for x in range(image_HSV.shape[0]):
        for y in range(image_HSV.shape[1]):
            hue, sat, val = image_HSV[x, y]
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
    # print(hue_min, hue_max, sat_min, sat_max, val_min, val_max)
    # print("Minimum H:", hue_min)
    # print("Maximum H:", hue_max)
    # print("Minimum S:", sat_min)
    # print("Maximum S:", sat_max)
    # print("Minimum V:", val_min)
    # print("Maximum V:", val_max)

    HSV_colorspace = np.array([hue_min, hue_max, sat_min, sat_max, val_min, val_max])

    return HSV_colorspace

def get_mask(image_hsv: np.ndarray, lower_bound: np.ndarray, upper_bound: np.ndarray) -> np.ndarray:
    return cv2.inRange(image_hsv, lower_bound, upper_bound)

def apply_mask(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    return cv2.bitwise_and(image, image, mask=mask)

def get_contours(mask: np.ndarray, outline_treshold: int, object_count: int) -> np.ndarray:

    ret, thresh = cv2.threshold(mask, outline_treshold, 255, 0)

    # find contours in the thresholded image and initialize the 
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # reduce number of contours
    longestContours = sorted(contours, key=cv2.contourArea, reverse=True)[1:object_count+1]

    return longestContours

def reduce_contours(contours: np.ndarray, epsilon_factor: int) -> np.ndarray:
    reduced_contours = []
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        epsilon = epsilon_factor * perimeter
        reduced_contour  = cv2.approxPolyDP(contour, epsilon, True)
        reduced_contours.append(reduced_contour)

    return reduced_contours

def invert_color(color):
    r, g, b = color
    return (255 - r, 255 - g, 255 - b)

def draw_contours(image: np.ndarray, contours: np.ndarray, point_color: np.ndarray = (0, 0, 0)) -> np.ndarray:
    for i, contour in enumerate(contours):
        cv2.drawContours(image, [contour], -1, colors[i], 2)
        for point in contour:
            # print(tuple(point[0]))
            cv2.circle(image, tuple(point[0]), 2, invert_color(colors[i]), -1)

    return image

def RGB_to_HSV(rgb_image):
    # Convert the RGB image to the HSV color space
    hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)

    return hsv_image

def cv2HSV_to_pil(hsv_image):
    # Convert the HSV image from cv2 to a NumPy array
    hsv_array = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2RGB)

    # Reshape the NumPy array to match the dimensions of the image
    h, w, _ = hsv_image.shape
    pil_image = Image.fromarray(hsv_array.reshape((h, w, 3)))

    return pil_image

def cv2RGB_to_pil(rgb_image):
    # Convert the RGB image from cv2 to a NumPy array
    rgb_array = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)

    # Reshape the NumPy array to match the dimensions of the image
    h, w, _ = rgb_image.shape
    pil_image = Image.fromarray(rgb_array.reshape((h, w, 3)))

    return pil_image

def cv2_to_pil(cv2_image_nparray):
    # Create a PIL image from the NumPy array
    pil_image = Image.fromarray(cv2_image_nparray)

    return pil_image

def pil_to_cv2(pil_image):
    # Convert the PIL image to a NumPy array in BGR format
    cv2_image_bgr = np.array(pil_image, dtype=np.uint8)

    return cv2_image_bgr

def cv2_mask_to_pil(mask):
    # Convert the cv2 mask from a NumPy array to an 8-bit grayscale image
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

    # Create a PIL image from the grayscale image
    pil_image = Image.fromarray(mask)

    return pil_image

def cv2_mask_to_RGB(mask):
    # Convert the cv2 mask from a NumPy array to an 8-bit grayscale image
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    
    return mask