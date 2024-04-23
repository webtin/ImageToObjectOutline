import cv2
import numpy as np

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

def get_ROI_HSV_colorspace(image: np.ndarray) -> np.ndarray:
    # select ROI (region of interest) to get baseline values for background color space
    roi = cv2.selectROI("Image", image)
    # # debug
    # print(roi)

    # extract ROI area as new array
    roi_image = hsv_image[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]

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

    ROI_HSV_colorspace = np.array([hue_min, hue_max, sat_min, sat_max, val_min, val_max])

    return ROI_HSV_colorspace


# read image
image = cv2.imread("data\source_images\PXL_20240326_134928380_2.jpg")

# define GaussianBlur value
gaussianBlurValue = 13

# quantize color
# Define the color-divisor to split the color space
Color_reduction_divisor = 64

# Define standard color depth
standard_color_depth = 255

# Apply color reduction
image = reduce_color(image, Color_reduction_divisor)

# blur the image to reduce noise
image = cv2.GaussianBlur(image, (gaussianBlurValue, gaussianBlurValue), 0)

# convert to HSV image to enable Hue filtering
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# get ROI HSV color range
hue_min, hue_max, sat_min, sat_max, val_min, val_max = get_ROI_HSV_colorspace(image)

# create sliders and initialize with min max values for HSV colorspace of ROI
cv2.namedWindow("Slider")
cv2.resizeWindow("Slider", 640, 480)
cv2.createTrackbar("Hue Min", "Slider", hue_min, standard_color_depth, do_nothing)
cv2.createTrackbar("Hue Max", "Slider", hue_max, standard_color_depth, do_nothing)
cv2.createTrackbar("Saturation Min", "Slider", sat_min, standard_color_depth, do_nothing)
cv2.createTrackbar("Saturation Max", "Slider", sat_max, standard_color_depth, do_nothing)
cv2.createTrackbar("Value Min", "Slider", val_min, standard_color_depth, do_nothing)
cv2.createTrackbar("Value Max", "Slider", val_max, standard_color_depth, do_nothing)

print("Press q button to save mask and exit")

# create mask with ROI HSV color range in a while loop to fine adjust HSV color range of background
while True:
  
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
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

    resulting_image = cv2.bitwise_and(image, image, mask=mask)

    stacked_images = np.hstack([image, resulting_image])

    # create a stacked image of the original and the HSV one.
    cv2.imshow("Image", stacked_images)

    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        cv2.imwrite("data\processed\output_image2.jpg", mask)
        print("Mask saved")
        break


cv2.destroyAllWindows()   

