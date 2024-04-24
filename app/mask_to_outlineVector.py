import cv2
import numpy as np

def do_nothing(nothing):
    '''
    A function that does nothing
    required for cv2 trackbar
    '''
    pass

# predefine some colors
colors = [(0,255,0), (0,0,255), (255,0,0), (255,0,255), (0,255,255), (255,255,0), (255,255,255), (0,0,0), (128,128,128), (192,192,192)]  # Define different colors

# load orignal image
image = cv2.imread("data\source_images\PXL_20240326_134928380_2.jpg")

# load mask image
mask = cv2.imread(r'data\processed\output_image2.jpg')
mask_GRAY = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

# define gaussian blur value
gaussianBlurValue = 21
max_gaussianBlurValue = 100

# define epsilon value

epsilon_factor = 1
max_epsilon_factor = 1000
# epsilon factor 0.0001 .. 0.01

# define outline treshold value
outline_treshold = 127
max_outline_treshold = 255

# define default number of objects
number_of_objects = 1
max_number_of_objects = 20

# create sliders
cv2.namedWindow("Slider")
cv2.resizeWindow("Slider", 640, 480)
trackbar_name_objects = "Objects"
trackbar_name_treshold = "Treshold"
trackbar_name_blur = "Blur"
trackbar_name_detail = "Detail"

cv2.createTrackbar(trackbar_name_objects, "Slider", number_of_objects, max_number_of_objects, do_nothing)
cv2.createTrackbar(trackbar_name_treshold, "Slider", outline_treshold, max_outline_treshold, do_nothing)
cv2.createTrackbar(trackbar_name_blur, "Slider", gaussianBlurValue, max_gaussianBlurValue, do_nothing)
cv2.createTrackbar(trackbar_name_detail, "Slider", epsilon_factor, max_epsilon_factor, do_nothing)

# create mask with ROI HSV color range in a while loop to fine adjust HSV color range of background
while True:

    # get gaussian blur value
    gaussianBlurValue = cv2.getTrackbarPos(trackbar_name_blur, "Slider")
    if gaussianBlurValue % 2 == 0:
        gaussianBlurValue += 1

    # get outline treshold
    outline_treshold = cv2.getTrackbarPos(trackbar_name_treshold, "Slider")

    # get epsilon factor
    epsilon_factor = cv2.getTrackbarPos(trackbar_name_detail, "Slider")

    # get number of objects
    number_of_objects = cv2.getTrackbarPos(trackbar_name_objects, "Slider")
    print(number_of_objects)

    # apply gaussian blur to smooth the mask
    blurred_mask_GRAY = cv2.GaussianBlur(mask_GRAY, (gaussianBlurValue, gaussianBlurValue), 0)
    blurred_mask = cv2.cvtColor(blurred_mask_GRAY, cv2.COLOR_GRAY2BGR)

    # apply threshold
    ret, thresh = cv2.threshold(blurred_mask_GRAY, outline_treshold, 255, 0)

    full_contour_image = image.copy()
    reduced_contour_image = image

    # find contours in the thresholded image and initialize the 
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # reduce number of contours
    longestContours = sorted(contours, key=cv2.contourArea, reverse=True)[1:number_of_objects+1]

    # reduce number of points in contours
    # https://stackoverflow.com/questions/66753026/opencv-smoother-contour
    reduced_contours = []
    for contour in longestContours:
        perimeter = cv2.arcLength(contour, True)
        epsilon = epsilon_factor/(100*max_epsilon_factor) * perimeter
        reduced_contour  = cv2.approxPolyDP(contour, epsilon, True)
        reduced_contours.append(reduced_contour)

    longestContours = reduced_contours

    # draw contours
    for i, contour in enumerate(longestContours):  
        cv2.drawContours(full_contour_image, [contour], -1, colors[i], 2)
        cv2.drawContours(blurred_mask, [contour], -1, colors[i], 2)
        print("len of contour " + str(i) + ": " + str(len(contour)))

        # Draw the points of the contour
        for point in contour:
            # print(tuple(point[0]))
            cv2.circle(full_contour_image, tuple(point[0]), 1, (0, 0, 0), -1)


    stacked_images = np.hstack([full_contour_image, blurred_mask])

    cv2.imshow('Contours', stacked_images)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.waitKey(0)
cv2.destroyAllWindows()

