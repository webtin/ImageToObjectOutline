from image_processing import image_processing

# import cv2
# import numpy as np

### Defaults

# Define the color-divisor to split the color space 
color_reduction_divisor = 64

# Define standard color depth
standard_color_depth = 255

# Define default gaussian blur value
gaussian_blur_value = 1

# default image path
default_image_path = (r"data\source_images\PXL_20240326_134928380_2.jpg")

### Main

# select image
image = cv2.imread(default_image_path)

# reduce color
image = reduce_color(image, color_reduction_divisor)

# # blur the image to reduce noise
image = cv2.GaussianBlur(image, (gaussian_blur_value, gaussian_blur_value), 0)

# # select ROI
image_roi = get_ROI(image)
# convert to HSV image to enable Hue filtering
image_roi_hsv = cv2.cvtColor(image_roi, cv2.COLOR_BGR2HSV)
# get ROI HSV color range
hue_min, hue_max, sat_min, sat_max, val_min, val_max = get_HSV_colorspace(image_roi_hsv)
# convert original image to HSV
image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

cv2.imshow('ima', image)

# create sliders and initialize with min max values for HSV colorspace of ROI
cv2.namedWindow("Slider")
cv2.resizeWindow("Slider", 640, 480)
cv2.createTrackbar("Hue Min", "Slider", hue_min, standard_color_depth, do_nothing)
cv2.createTrackbar("Hue Max", "Slider", hue_max, standard_color_depth, do_nothing)
cv2.createTrackbar("Saturation Min", "Slider", sat_min, standard_color_depth, do_nothing)
cv2.createTrackbar("Saturation Max", "Slider", sat_max, standard_color_depth, do_nothing)
cv2.createTrackbar("Value Min", "Slider", val_min, standard_color_depth, do_nothing)
cv2.createTrackbar("Value Max", "Slider", val_max, standard_color_depth, do_nothing)
# Add text to window
# Create an image to display
img = np.zeros((100, 640, 3), dtype=np.uint8)
cv2.putText(img, "press c to abort", (10, 10), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1)
# Display the image in the window
cv2.imshow('Slider', img)


print("Press q button to save mask and exit")

# create mask with ROI HSV color range in a while loop to fine adjust HSV color range of background
while True:

    if cv2.waitKey(1) & 0xFF == ord("r"):
        # # select ROI
        image_roi = get_ROI(image)

        # convert to HSV image to enable Hue filtering
        image_roi_hsv = cv2.cvtColor(image_roi, cv2.COLOR_BGR2HSV)

        # get ROI HSV color range
        hue_min, hue_max, sat_min, sat_max, val_min, val_max = get_HSV_colorspace(image_roi_hsv)
  
    # extract the values from the trackbar
    hue_min = cv2.getTrackbarPos("Hue Min", "Slider")
    hue_max = cv2.getTrackbarPos("Hue Max", "Slider")
    sat_min = cv2.getTrackbarPos("Saturation Min", "Slider")
    sat_max = cv2.getTrackbarPos("Saturation Max", "Slider")
    val_min = cv2.getTrackbarPos("Value Min", "Slider")
    val_max = cv2.getTrackbarPos("Value Max", "Slider")
    
    # print(hue_min, hue_max, sat_min, sat_max, val_min, val_max)

    # set bounds
    lower_bound = np.array([hue_min, sat_min, val_min])
    upper_bound = np.array([hue_max, sat_max, val_max])

    # create mask
    mask = cv2.inRange(image_hsv, lower_bound, upper_bound)

    resulting_image = cv2.bitwise_and(image, image, mask=mask)

    stacked_images = np.hstack([image, resulting_image])

    # create a stacked image of the original and the HSV one.
    cv2.imshow("Image", stacked_images)

    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        cv2.imwrite("data\processed\output_image2.jpg", mask)
        print("Mask saved")
        break


cv2.destroyAllWindows()   
