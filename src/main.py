from src import *

# ### Defaults

# # Define the color-divisor to split the color space
# Color_reduction_divisor = 64

# # Define standard color depth
# standard_color_depth = 255

# # Define default gaussian blur value
# gaussian_blur_value = 13

# # default image path
# default_image_path = (r"data\source_images\PXL_20240326_134928380_2.jpg")

# ### Main

# # select image
# image = image_processing.cv2.imread(default_image_path)

# # reduce color
# image = image_processing.reduce_color(image, Color_reduction_divisor)

# # blur the image to reduce noise
# image = cv2.GaussianBlur(image, (gaussianBlurValue, gaussianBlurValue), 0)

# # select ROI
# image_roi = get_ROI(image)