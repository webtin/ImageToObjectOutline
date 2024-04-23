import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from PIL import Image, ImageTk
import cv2
import numpy as np

image_path = 'data\source_images\PXL_20240326_134928380_2.jpg'
# image_path = 'data\source_images\test.jpg'

# # Load the image
# img = cv2.imread(image_path)
# cv2.imshow('image', img)


class ImageScaler:
    """
    Initialize the class with the given root and set up the canvas for drawing. 
    Bind mouse and mouse wheel events for interaction. Load the image for display.

    The image is scaled and displayed in the canvas.
    Class can measure the distance between two points on the image and calculate pixel/mm by getting the real-world distance between the two points
    """
    def __init__(self, root):
        self.root = root

        self.scale = 1.0

        self.clicked_points = []

        # self.binary_mode = True
        # self.lower_threshold = None
        # self.upper_threshold = None

        self.pan_offset_x = 0
        self.pan_offset_y = 0

        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-2>", self.on_pan_start)  # Binding the middle mouse button press
        self.canvas.bind("<B2-Motion>", self.on_pan)
        self.canvas.bind("<ButtonRelease-2>", self.on_pan_end)  # Binding the middle mouse button release

        self.load_image()

    def load_image(self):
        # file_path = filedialog.askopenfilename()
        self.image = cv2.imread(image_path)
        self.display_image(self.scale)

    def display_image(self, scale):
        height, width = self.image.shape[:2]
        resized_image = cv2.resize(self.image, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)
        self.tk_image = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def on_canvas_click(self, event):

        # Calculate the image coordinates, adjust for zoom and pan
        x_pos_clicked = (event.x - self.pan_offset_x) / self.scale
        y_pos_clicked = (event.y - self.pan_offset_y) / self.scale
        print(f"Clicked point: {x_pos_clicked, y_pos_clicked}")
        self.clicked_points.append((x_pos_clicked, y_pos_clicked))
        print(f"Clicked points: {self.clicked_points}")

        # if self.binary_mode:
        #     # Check the pixel value at the clicked position
        #     grayscale_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        #     pixel_value = grayscale_image[int(y_pos_clicked), int(x_pos_clicked)]
        #     print(f"Pixel value at clicked point: {pixel_value}")
        #     self.apply_binary_thresholding()


        # Convert image coordinates to canvas coordinates
        # not working yet, points are not persistant when zooming in and out
        # solution: have a list of point coordinates and have a function to update point locations on pan and zoom and have a fuction to delete old points and redraw new
        # canvas_x = (event.x - self.pan_offset_x) 
        # canvas_y = (event.y - self.pan_offset_y) 
        # radius = 5
        # self.canvas.create_oval(canvas_x - radius, canvas_y - radius, canvas_x + radius, canvas_y + radius, fill="red")

        if len(self.clicked_points) == 2:
            x1, y1 = self.clicked_points[0]
            x2, y2 = self.clicked_points[1]
            pixel_distance = np.sqrt((x2 - x1) ** 2 + ((y2 - y1) ** 2))
            print(f"Distance between points: {pixel_distance} pixels")
            self.calculate_scaling_factor(pixel_distance)

    def apply_binary_thresholding(self):
        # Apply binary thresholding to the image
        grayscale_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(grayscale_image, self.lower_threshold, self.upper_threshold, cv2.THRESH_BINARY)

        # Convert to displayable format and update the canvas image
        self.tk_image = ImageTk.PhotoImage(image=Image.fromarray(binary_image))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Reset thresholds for next use
        self.lower_threshold = None
        self.upper_threshold = None

    def calculate_scaling_factor(self, pixel_distance):
        # Assume the user knows the real-world distance (in mm) between the points
        real_world_distance = simpledialog.askfloat("Real World Distance", "Enter the real world distance (in mm) between the points:")
        if real_world_distance is not None:
            scaling_factor = pixel_distance / real_world_distance
            print(f"Scaling factor: {scaling_factor} pixels/mm")
        self.close_window()


    def on_mouse_wheel(self, event):
        scale_per_scroll = 1.1
        if event.delta > 0:
            # Zoom in
            self.scale *= scale_per_scroll
            self.display_image(self.scale)
        elif event.delta < 0:
            # Zoom out
            self.scale /= scale_per_scroll
            self.display_image(self.scale)

        print(f"Scale: {self.scale}")

    def on_pan_start(self, event):
        self.canvas.scan_mark(event.x, event.y)
        print(f"Pan start: {event.x, event.y}")
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def on_pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_pan_end(self, event):
        print(f"Pan end: {event.x, event.y}")
        self.pan_offset_x += event.x - self.pan_start_x
        self.pan_offset_y += event.y - self.pan_start_y
        
        print(f"Pan offset: {self.pan_offset_x, self.pan_offset_y}")

    def close_window(self):
        self.root.destroy()

def write_svg_file(contour, scaling_factor, height, width):
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

# define scaling factor for SVG export
# scaling factor could be derived automatically later in development
scaling_factor = 0.245 #px/mm

# load image
image = cv2.imread(image_path)

# display image
cv2.imshow('image', image)

# get image size
height, width, channels = image.shape 

# convert image to grayscale
grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imshow('grayscale image', grayscale_image)

# apply gaussian blur to reduce noise 
blurred_image = cv2.GaussianBlur(grayscale_image, (7, 7), 0)
cv2.imshow('blurred_image image', blurred_image)

# apply Otsu's automatic thresholding which automatically determines
# the best threshold value
(treshold, threshInv) = cv2.threshold(blurred_image, 0, 255,
	cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
print(treshold)
cv2.imshow("Threshold", threshInv)

# find contours in the thresholded image and initialize the 
contours, hierarchy = cv2.findContours(threshInv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# find longest contour
# longestContour = max(contours, key=cv2.contourArea)
# print(len(longestContour))

# find n longest contours

# number of contours
number_of_contours = 10
longestContours = sorted(contours, key=cv2.contourArea, reverse=True)[:number_of_contours]



# # reduce points
# # https://stackoverflow.com/questions/66753026/opencv-smoother-contour

# epsilon = 0.0001 * cv2.arcLength(longestContour, True)
# reduced_contour  = cv2.approxPolyDP(longestContour, epsilon, True)

colors = [(0,255,0), (0,0,255), (255,0,0), (255,0,255), (0,255,255), (255,255,0), (255,255,255), (0,0,0), (128,128,128), (192,192,192)]  # Define different colors
for i, contour in enumerate(longestContours):
    cv2.drawContours(image, [contour], -1, colors[i], 3)

# cv2.drawContours(image, longestContours, -1, (0,255,0), 3)
cv2.imshow('Contours', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

## export contour as svg
# calculate absolute size


# write_svg_file(reduced_contour, scaling_factor, height, width)





# apply Otsu's automatic thresholding which automatically determines
# the best threshold value
# (T, threshInv) = cv2.threshold(blurred_image, 0, 255,
# 	cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
# cv2.imshow("Threshold", threshInv)

# print("[INFO] otsu's thresholding value: {}".format(T))
# # visualize only the masked regions in the image
# masked = cv2.bitwise_and(image, image, mask=threshInv)
# cv2.imshow("Output", masked)
# cv2.waitKey(0)


# root = tk.Tk()
# root.title("Image Scaler")
# root.geometry("800x600")
# app = ImageScaler(root)
# root.mainloop()


