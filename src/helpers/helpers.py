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

def get_color_reduction_divisor(color_reduction_factor):
    if color_reduction_factor == 1:
        return 16
    elif color_reduction_factor == 2:
        return 32
    elif color_reduction_factor == 3:
        return 64
    elif color_reduction_factor == 4:
        return 128