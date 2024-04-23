import cv2
import numpy as np

def do_nothing(nothing):
    '''
    A function that does nothing
    required for cv2 trackbar
    '''
    pass

def write_svg_file(contour, scaling_factor, height, width):
    """
    Write an SVG file with the given contour, scaling factor, height, and width.
    Parameters:
    - contour: the contour to be written to the SVG file
    - scaling_factor: the factor by which to scale the width and height of the SVG
    - height: the height of the SVG in pixels
    - width: the width of the SVG in pixels
    """
    standard_DPI = 96 #px/inch
    inch_mm_ratio = 1
    standard_DPmm = standard_DPI / inch_mm_ratio
    formatted_scaled_width = str(int(width / scaling_factor))+'mm'
    formatted_scaled_height = str(int(height / scaling_factor))+'mm'
    # scaled_witdh = str(int(width / scaling_factor * standard_DPmm))
    # scaled_height = str(int(height / scaling_factor * standard_DPmm))


    f = open('outline.svg', 'w+')
    f.write('<svg width="'+formatted_scaled_width+'" height="'+formatted_scaled_height+'" viewBox="0 0 '+str(10*width)+' '+str(10*height)+'" xmlns="http://www.w3.org/2000/svg">')
    f.write('<polyline points="0,0 '+str(width)+',0 '+str(width)+','+str(height)+' 0,'+str(height)+'" stroke="black" fill="none"/>')
    f.write('<polygon points="')

    for i in range(len(reduced_contour)):
        #print(c[i][0])
        x, y = reduced_contour[i][0]
        print(x, y)
        f.write(str(x)+  ',' + str(y)+' ')

    f.write('" fill="black"/>')
    f.write('</svg>')
    f.close()

# predefine some colors
colors = [(0,255,0), (0,0,255), (255,0,0), (255,0,255), (0,255,255), (255,255,0), (255,255,255), (0,0,0), (128,128,128), (192,192,192)]  # Define different colors

# load orignal image
image = cv2.imread("data\source_images\PXL_20240326_134928380_2.jpg")

# load mask image
mask = cv2.imread(r'data\processed\output_image2.jpg')
mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

# define gaussian blur value
gaussianBlurValue = 21
max_gaussianBlurValue = 100

# define epsilon value

epsilon_factor = 1
max_epsilon_factor = 1000
# epsilon factor 0.0001 .. 0.01



# create sliders
cv2.namedWindow("Slider")
cv2.resizeWindow("Slider", 640, 480)
cv2.createTrackbar("Blur", "Slider", gaussianBlurValue, max_gaussianBlurValue, do_nothing)
cv2.createTrackbar("Epsilon", "Slider", epsilon_factor, max_epsilon_factor, do_nothing)

# create mask with ROI HSV color range in a while loop to fine adjust HSV color range of background
while True:

    gaussianBlurValue = cv2.getTrackbarPos("Blur", "Slider")

    if gaussianBlurValue % 2 == 0:
        gaussianBlurValue += 1

    epsilon_factor = cv2.getTrackbarPos("Epsilon", "Slider")

    # apply gaussian blur to smooth the mask
    blurred_mask = cv2.GaussianBlur(mask, (gaussianBlurValue, gaussianBlurValue), 0)

    # apply threshold
    ret, thresh = cv2.threshold(blurred_mask, 127, 255, 0)

    # cv2.imshow('mask', mask)
    # cv2.imshow('blurred_mask mask', blurred_mask)
    # cv2.imshow('threshold mask', thresh)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    full_contour_image = image.copy()
    reduced_contour_image = image

    # find contours in the thresholded image and initialize the 
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # get number of objects from console
    # number_of_contours = int(input("Enter number of objects: "))
    number_of_contours = 7

    longestContours = sorted(contours, key=cv2.contourArea, reverse=True)[1:number_of_contours+1]

    reduced_contours = []
    for contour in longestContours:
        perimeter = cv2.arcLength(contour, True)
        epsilon = epsilon_factor/(100*max_epsilon_factor) * perimeter
        reduced_contour  = cv2.approxPolyDP(contour, epsilon, True)
        reduced_contours.append(reduced_contour)

    longestContours = reduced_contours

    for i, contour in enumerate(longestContours):  
        cv2.drawContours(full_contour_image, [contour], -1, colors[i], 1)
        print("len of contour " + str(i) + ": " + str(len(contour)))

        # Draw the points of the contour
        for point in contour:
            # print(tuple(point[0]))
            cv2.circle(full_contour_image, tuple(point[0]), 1, (0, 0, 0), -1)

    # reduce number of points in contours
    # https://stackoverflow.com/questions/66753026/opencv-smoother-contour

    cv2.imshow('Contours', full_contour_image)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break




# for i, contour in enumerate(reduced_contours):  
#     cv2.drawContours(reduced_contour_image, [contour], -1, colors[i], 3)

# cv2.imshow('reduced Contours', reduced_contour_image)


cv2.waitKey(0)
cv2.destroyAllWindows()

