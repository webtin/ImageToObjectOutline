import cv2
import ezdxf
from ezdxf import units
import numpy as np
import streamlit as st

def get_ellipse_coords(point: tuple[int, int], radius: int) -> tuple[int, int, int, int]:
    center = point
    return (
        center[0] - radius,
        center[1] - radius,
        center[0] + radius,
        center[1] + radius,
    )

def int_to_uint8(value):
    # Clip the integer value to the range of uint8 (0 to 255) and convert to uint8
    uint8_value = np.uint8(np.clip(value, 0, 255))
    return uint8_value

def convert_coordinates_dict_to_tuple(data):
    left = data['left'] + 2
    top = data['top'] + 2
    width = data['width']
    height = data['height']
    right = left + width + 4
    bottom = top + height + 4
    return (left, right, top, bottom)

def calculate_corner_points(width, height, percentage):

    # Calculate the size of the inner rectangle
    inner_width = width * percentage / 100
    inner_height = height * percentage / 100

    # Calculate the corner points
    x_left =   int((width - inner_width) / 2)
    x_right =  int(x_left + inner_width)
    y_top =    int((height - inner_height) / 2)
    y_bottom = int(y_top + inner_height)

    return (x_left, x_right, y_top, y_bottom)

import cv2

def draw_colored_rect(image, coordinates, color=(0, 0, 255)):
    x_left, x_right, y_top, y_bottom = coordinates
    
    # Draw a colored rectangle on the image
    image_with_rect = cv2.rectangle(image.copy(), (int(x_left), int(y_top)), (int(x_right), int(y_bottom)), color, 2)
    
    return image_with_rect

def get_color_reduction_divisor(color_reduction_factor):
    if color_reduction_factor == 1:
        return 16
    elif color_reduction_factor == 2:
        return 32
    elif color_reduction_factor == 3:
        return 64
    elif color_reduction_factor == 4:
        return 128

def write_svg_file(contours, scaling_factor, height, width):
    """
    Write an SVG file with the given contours, scaling factor, height, and width.
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

    for contour in contours:
        for point in contour:
            print(point)
            print("x : ", point[0][0])
            print("y : ", point[0][1])

    f = open('outline.svg', 'w+')
    # svg header
    f.write('<svg width="'+formatted_scaled_width+'" height="'+formatted_scaled_height+'" viewBox="0 0 '+str(10*width)+' '+str(10*height)+'" xmlns="http://www.w3.org/2000/svg">')
    # svg frame
    f.write('<polyline points="0,0 '+str(width)+',0 '+str(width)+','+str(height)+' 0,'+str(height)+'" stroke="black" fill="none"/>')

    for contour in contours:
        f.write('<polygon points="')
        for point in contour:
            x, y = point[0][0], point[0][1]
            f.write(str(x)+  ',' + str(y)+' ')
            # print(x, y)
            # print("x : ", point[0][0])
            # print("y : ", point[0][1])
        f.write('" fill="black"/>')

    f.write('</svg>')
    f.close()

def write_svg(contours, scaling_factor, height, width):
    standard_DPI = 96 #px/inch
    inch_mm_ratio = 1
    standard_DPmm = standard_DPI / inch_mm_ratio
    formatted_scaled_width = str(int(width / scaling_factor))+'mm'
    formatted_scaled_height = str(int(height / scaling_factor))+'mm'
    
    # write header
    svg_content = '<svg width="'+formatted_scaled_width+'" height="'+formatted_scaled_height+'" viewBox="0 0 '+str(width)+' '+str(height)+'" xmlns="http://www.w3.org/2000/svg">'
    # svg frame
    svg_content += '<polyline points="0,0 '+str(width)+',0 '+str(width)+','+str(height)+' 0,'+str(height)+'" stroke="black" fill="none"/>'
    
    for contour in contours:
        svg_content += '<polygon points="'
        for point in contour:
            x, y = point[0][0], point[0][1]
            svg_content += f"{x},{y} "
            # print(x, y)
            # print("x : ", point[0][0])
            # print("y : ", point[0][1])
        svg_content += '" fill="black"/>'

    svg_content += '</svg>'
    
    return svg_content

def create_dxf_with_line(filename):
    # Create a new DXF document
    doc = ezdxf.new()

    # Create a new layer for the object outlines
    doc.layers.new('Outlines')

    # Create a new LINE entity
    line = doc.modelspace().add_line(
        start=(0, 0),
        end=(100, 100),
    )

    # Set the layer and color of the line
    line.layer = 'Outlines'
    line.color = 1  # Red

    # Save the DXF file
    doc.saveas(filename)

def convert_contours_to_list(contours):
    """
    Convert an outline to a list of points in the format [(x1, y1), (x2, y2), ...][(x1, y1), (x2, y2)].
    """
    points_list = []
    for contour in contours:
        points=[]
        for point in contour:
            points.append((point[0][0], point[0][1]))
        points.append((points[0][0], points[0][1]))  # Add the first point as the last point
        points_list.append(points)
    # print(points_list)
    return points_list

def create_dxf_from_contours(filename, points_list):
    # Create a new DXF document
    doc = ezdxf.new("R2000")
    doc.units = units.MM
    msp = doc.modelspace()

    for points in points_list:
        msp.add_lwpolyline(points)

    # # Iterate over the contours and create LINE entities for each contour
    # for contour in contours:
    #     for i in range(len(contour) - 1):
    #         start_point = contour[i]
    #         end_point = contour[i + 1]
    #         line = doc.modelspace().add_line(start=start_point, end=end_point)
    #         line.layer = 'Outlines'
    #         line.color = 1  # Red

    # Save the DXF file with the provided filename
    doc.saveas(filename)

# Call the function to create a DXF file with a line
# create_dxf_with_line("object_outlines.dxf")

def scale_points_list(points_list, pixel_per_mm, scaling_factor):
    scaled_points_list = []
    for points in points_list:
        scaled_points = []
        for point in points:
            scaled_x = scaling_factor * point[0] / pixel_per_mm
            scaled_y = scaling_factor * point[1] / pixel_per_mm
            scaled_points.append((scaled_x, scaled_y))
        scaled_points_list.append(scaled_points)
    return scaled_points_list
