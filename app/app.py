import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from PIL import Image, ImageTk
import cv2
import numpy as np

image_path = 'data\source_images\PXL_20240204_110214340_smaller.jpg'
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
        x_image = (event.x - self.pan_offset_x) / self.scale
        y_image = (event.y - self.pan_offset_y) / self.scale
        print(f"Clicked point: {x_image, y_image}")
        self.clicked_points.append((x_image, y_image))
        print(f"Clicked points: {self.clicked_points}")

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

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Image Scaler")
    root.geometry("800x600")
    app = ImageScaler(root)
    root.mainloop()
# import cv2
# import numpy as np

# image_path = 'data\source_images\PXL_20240204_110214340.jpg'

# # Initialize the list to store the points
# points = []

# def click_event(event, x, y, flags, param):
#     # Check if the event was a left mouse click
#     if event == cv2.EVENT_LBUTTONDOWN:
#         # Store the coordinates of the point
#         points.append((x, y))

#         # Draw a circle at the clicked point
#         cv2.circle(img, (x, y), 5, (255, 0, 0), -1)
#         cv2.imshow('image', img)

#         # If two points have been clicked, calculate the distance
#         if len(points) == 2:
#             cv2.line(img, points[0], points[1], (255, 0, 0), 2)
#             cv2.imshow('image', img)
#             p1, p2 = points
#             distance_pixels = np.linalg.norm(np.array(p1) - np.array(p2))
#             distance_mm = float(input("Enter the real world distance (in mm) between the clicked points: "))
#             scaling_factor = distance_pixels / distance_mm
#             print(f"Scaling factor: {scaling_factor} pixels/mm")

# # Load the image
# img = cv2.imread(image_path)
# cv2.imshow('image', img)

# # Set the mouse callback function for the window
# cv2.setMouseCallback('image', click_event)

# cv2.waitKey(0)
# cv2.destroyAllWindows()






# assert im is not None, "file could not be read, check with os.path.exists()"
# imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
# ret, thresh = cv.threshold(imgray, 127, 255, 0)
# im2, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

# plt.subplot(121),plt.imshow(img,cmap = 'gray')
# plt.title('Original Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(122),plt.imshow(im2,cmap = 'gray')
# plt.title('Contour'), plt.xticks([]), plt.yticks([])

# plt.show()