import cv2
import numpy as np
import streamlit as st

def brighten_image(image, amount):
    img_bright = cv2.convertScaleAbs(image, beta=amount)
    return img_bright


def blur_image(image, amount):
    blur_img = cv2.GaussianBlur(image, (0, 0), amount)
    return blur_img


def enhance_details(img):
    hdr = cv2.detailEnhance(img, sigma_s=12, sigma_r=0.15)
    return hdr

def int_to_uint8(value):
    # Clip the integer value to the range of uint8 (0 to 255) and convert to uint8
    uint8_value = np.uint8(np.clip(value, 0, 255))
    return uint8_value

def convert_dict_to_tuple(data):
    left = data['left']
    top = data['top']
    width = data['width']
    height = data['height']
    right = left + width
    bottom = top + height
    return (left, right, top, bottom)

def calculate_corner_points(width, height, percentage):

    # Calculate the size of the inner rectangle
    inner_width = width * percentage / 100
    inner_height = height * percentage / 100

    # Calculate the corner points
    x_left =   int((width - inner_width) / 2)
    x_right =  int(x_left + inner_width)
    y_top =    int((height - inner_height) / 2)
    y_bottom = int(y_top + inner_height)

    return (x_left, x_right, y_top, y_bottom)

import cv2

def draw_colored_rect(image, coordinates, color=(0, 0, 255)):
    x_left, x_right, y_top, y_bottom = coordinates
    
    # Draw a colored rectangle on the image
    image_with_rect = cv2.rectangle(image.copy(), (int(x_left), int(y_top)), (int(x_right), int(y_bottom)), color, 2)
    
    return image_with_rect

def get_color_reduction_divisor(color_reduction_factor):
    if color_reduction_factor == 1:
        return 16
    elif color_reduction_factor == 2:
        return 32
    elif color_reduction_factor == 3:
        return 64
    elif color_reduction_factor == 4:
        return 128