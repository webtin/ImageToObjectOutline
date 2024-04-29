import cv2
import streamlit as st
import numpy as np
from PIL import Image
from helpers import *


def main_loop():
    st.title("OpenCV Demo App")
    st.subheader("This app allows you to play with Image filters!")
    st.text("We use OpenCV and Streamlit for this demo")

    blur_rate = st.sidebar.slider("Blurring", min_value=0.5, max_value=3.5)
    brightness_amount = st.sidebar.slider("Brightness", min_value=-50, max_value=50, value=0)
    apply_enhancement_filter = st.sidebar.checkbox('Enhance Details')

    options = ['Upload Picture', 'Take Picture with Camera', 'Use Example Picture']
    choice = st.radio('Choose an option', options)

    if choice == 'Upload Picture':
        image_file = st.file_uploader("Upload Your Image", type=['jpg', 'png', 'jpeg'])
        if not image_file:
            return None
        original_image = Image.open(image_file)

    elif choice == 'Take Picture with Camera':
        image_file = st.camera_input("Take Photo")
        original_image = Image.open(image_file)

    elif choice == 'Use Example Picture':
        image_file = 'default_image.jpg'
        original_image = Image.open(image_file)

    original_image = np.array(original_image)

    processed_image = blur_image(original_image, blur_rate)
    processed_image = brighten_image(processed_image, brightness_amount)

    if apply_enhancement_filter:
        processed_image = enhance_details(processed_image)

    st.text("Original Image vs Processed Image")
    st.image([original_image, processed_image])


if __name__ == '__main__':
    main_loop()