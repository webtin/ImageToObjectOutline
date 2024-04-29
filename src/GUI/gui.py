import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ImageSliderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Slider App")

        self.image_label = tk.Label(self.root)
        self.image_label.pack()

        self.sliders = {}  # Use a dictionary to store the sliders

        self.create_slider("slider_0", 0, "Slider 0")
        self.create_slider("slider_1", 1, "Slider 1")
        self.create_slider("slider_2", 2, "Slider 2")
        self.create_slider("slider_3", 3, "Slider 3")
        self.create_slider("slider_4", 4, "Slider 4")
        self.create_slider("slider_5", 5, "Slider 5")

        self.update_image()

    def create_slider(self, slider_name, index, label_text):
        slider_frame = ttk.Frame(self.root)
        slider_frame.pack(pady=10)

        slider = ttk.Scale(slider_frame, from_=0, to=255, orient="horizontal", length=400, command=lambda value, name=slider_name: self.on_slider_change(name, value))
        slider.pack(side="left", padx=10)

        label = ttk.Label(slider_frame, text=label_text)
        label.pack(side="left")

        self.sliders[slider_name] = slider

    def on_slider_change(self, slider_name, value):
        print(f"Slider {slider_name} changed to {value}")
        # Add your custom logic here to update the image based on the slider changes

    def update_image(self):
        # Create a sample image (you can replace this with your own image processing logic)
        width, height = 500, 500
        image = Image.new("RGB", (width, height), "white")
        pixels = image.load()

        # Set pixel values based on slider positions
        for i, slider_name in enumerate(self.sliders):
            slider_value = self.sliders[slider_name].get()  # Get the value of each slider
            for y in range(height):
                for x in range(width):
                    pixels[x, y] = (slider_value,) * 3  # Use the slider value for all color channels

        # Display the image
        img_tk = ImageTk.PhotoImage(image)
        self.image_label.config(image=img_tk)
        self.image_label.image = img_tk

        # Update image periodically
        self.root.after(100, self.update_image)

root = tk.Tk()
app = ImageSliderApp(root)
root.mainloop()