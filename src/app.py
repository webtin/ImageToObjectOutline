import numpy as np
from PIL import Image, ImageDraw
import streamlit as st
from streamlit_cropper import st_cropper
from streamlit_image_coordinates import streamlit_image_coordinates

from helpers import *
from image_processing import * 

def main_loop():

    # set image_available flag, so that script does not continue without valid image
    if 'image_available' not in st.session_state:
        st.session_state.image_available = False

    # set max image size
    max_image_width, max_image_height = 1000, 1000

    # initialize scaling factor to 1
    pixel_per_mm = 1

    # add text
    st.title("Get Object Outline from Image")

    # add radio buttons
    options = ['Upload Picture', 'Take Picture with Camera', 'Use Example Picture']
    choice = st.radio('Choose an option', options)

    if choice == 'Upload Picture':
        image_file = st.file_uploader("Upload Your Image", type=['jpg', 'png', 'jpeg'], accept_multiple_files=False)
        if not image_file:
            return None
        original_image = Image.open(image_file)
        st.session_state.image_available = True

    # image from webcam
    elif choice == 'Take Picture with Camera':
        image_file = st.camera_input("Take Photo")
        if image_file is not None:
            original_image = Image.open(image_file)
            st.session_state.image_available = True
        else:
            st.error("No image captured")

    # default image
    elif choice == 'Use Example Picture':
        image_file = 'data/source_images/PXL_20240326_134928380_1.jpg'
        original_image = Image.open(image_file)
        st.session_state.image_available = True
        
    try:
        original_image
    except:
        st.session_state.image_available = False

    # resize image
    if st.session_state.image_available:
        image_width, image_height = original_image.size    
        if image_width > max_image_width or image_height > max_image_height:
            original_image, _ = proportional_resize_image(original_image, max_height=max_image_height, max_width=max_image_width)
            image_width, image_height = original_image.size 

    # set preprocessing container
    preprocessing_container = st.empty()

    if st.session_state.image_available:
        with preprocessing_container.container(border=True):
            st.title("Step 1: Image Prepocessing")
            with st.expander("Tutorial", expanded=False):
                st.markdown(
                    '''
                    ### Step 1: Adjust The Image

                    - Adjust the following sliders on the sidebar:
                    - Color Reduction: To achieve a more even background color.
                    - Blur: To reduce noise.
                    - Color Space Deviation: To broaden the colorspace.
                    - Advanced: You can manually fine adjust the colorspace by using the sliders.

                    ### Step 2: Select Background Area

                    - Use the bounding box to select a portion of the background of your image.
                    - The color space of the background will be used to filter out your objects.

                    ### Step 3: Check Mask

                    - Play around with the sliders and check the mask until you are happy with the result.

                    ### Step 4: Resume

                    - Once satisfied with the mask, resume to Step 2 to create the outline for your objects.
                    ''')

            # add sidebar sliders
            with st.sidebar.expander("Adjust Image", expanded=True):
                # color reduction
                apply_color_reduction = st.checkbox('Color Reduction', value=True)
                color_reduction_factor = st.slider("Color Reduction Multiplier", min_value=1, max_value=4, value=2)
                
                # blur
                apply_blur = st.checkbox('Blur Original Picture', value=True)
                blur_rate = st.slider("Blur Original Picture", min_value=0.5, max_value=5.0, value=1.5)

                # Color Space Deviation
                color_space_deviation = st.slider("Color Space Deviation", min_value=0, max_value=20, value=5)

            # lookup color reduction divisor
            color_reduction_divisor = get_color_reduction_divisor(color_reduction_factor)

            # convert PIL Image to np Array to use with cv2
            processed_image_np = np.array(original_image)

            # blur the image before processing to reduce noise
            if apply_blur:
                processed_image_np = blur_image(processed_image_np, blur_rate)

            # quantize colors for effective color space filtering
            if apply_color_reduction:
                processed_image_np = reduce_color(processed_image_np, color_reduction_divisor)

            # crop image to background
            if 'coordinates' in st.session_state:
                cropped_img, coordinates = st_cropper(cv2_to_pil(processed_image_np), realtime_update=True, box_color='#0000FF', return_type="both")

            else:
                st.session_state.coordinates = calculate_corner_points(image_width, image_height, 30)
                coordinates = st.session_state.coordinates
                cropped_img = st_cropper(cv2_to_pil(processed_image_np), realtime_update=True, box_color='#0000FF', return_type="image")
        
            # create Mask from cropped image Colorspace
            # get HSV color range of selected area
            hue_min, hue_max, sat_min, sat_max, val_min, val_max = get_HSV_colorspace(RGB_to_HSV(pil_to_cv2(cropped_img)))

            # apply color space deviation
            hue_min -= color_space_deviation
            hue_max += color_space_deviation
            sat_min -= color_space_deviation
            sat_max += color_space_deviation
            val_min -= color_space_deviation
            val_max += color_space_deviation

            # add sidebar slider for finetuning HSV Colorspace
            with st.sidebar.expander("Fine Adjust HSV Colorspace"):
                hue_min = int_to_uint8(st.slider("hue min", min_value=0, max_value=255, value=hue_min))
                hue_max = int_to_uint8(st.slider("hue max", min_value=0, max_value=255, value=hue_max))
                sat_min = int_to_uint8(st.slider("sat min", min_value=0, max_value=255, value=sat_min))
                sat_max = int_to_uint8(st.slider("sat max", min_value=0, max_value=255, value=sat_max))
                val_min = int_to_uint8(st.slider("val min", min_value=0, max_value=255, value=val_min))
                val_max = int_to_uint8(st.slider("val max", min_value=0, max_value=255, value=val_max))

            # set bounds
            lower_bound = np.array([hue_min, sat_min, val_min])
            upper_bound = np.array([hue_max, sat_max, val_max])

            # create mask
            image_hsv = RGB_to_HSV(processed_image_np)
            mask = get_mask(image_hsv, lower_bound, upper_bound)

            if st.checkbox("Show Mask"):
                st.image(cv2_mask_to_pil(mask))

            masked_image = apply_mask(np.array(original_image), mask=mask)

            st.text("Masked Image:")
            st.image(masked_image)

        outline_container = st.empty()    

        with outline_container.container(border=True):
            st.title("Step 2: Generate Outline")
            with st.expander("Tutorial", expanded=False):
                st.markdown(
                    '''
                    ### Step 5: Define Number of Objects

                    - Use the slider in the sidebar to pack the number of objects
                    - The biggest objects will be picked first

                    ### Step 6: Define Outline Threshold And Blur the Mask

                    - By blurring the Mask and Adjusting the Outline Threshold you can increase the size of the outline
                    - You can use the Checkbox to show the Outlines overlayed on the mask to see your results better

                    ### Step 7: Reduce the Number of Points (optional)

                    - You can reduce the number of points by using the slider
                    - Less points make it easier to handle and manipulate the outline in CAD-Software

                    ### Step 8: Adjust Scaling (optional)

                    - Select two Points in the image below and provide the distance between them in mm
                    - This will automatically size your DXF file correctly
                    - Use any reference in your Image
                    - You can just measure any object and provide the distance
                    ''')

            # add sidebar slider
            with st.sidebar.expander("Adjust Outline", expanded=True):
                # Number of Objects
                outline_count = st.slider("Number of Objects", min_value=1, max_value=10, value=3)

                # blur mask
                apply_mask_blur = st.checkbox('Blur Mask', value=True)
                mask_blur_rate = st.slider("Blur Mask", min_value=0.5, max_value=5.0, value=1.5)

                # Outline Threshold
                outline_threshold = st.slider("Outline Threshold", min_value=0, max_value=255, value=128)

                # simplify outline
                simplify_outline = st.checkbox('Reduce Number of Points', value=False)
                outline_simplify_rate = st.slider("Reduction Factor", min_value=1, max_value=300, value=10)
            
            if apply_mask_blur:
                mask = blur_image(mask, mask_blur_rate)

            contours = get_contours(mask, outline_threshold, outline_count)

            if simplify_outline:
                contours = reduce_contours(contours, outline_simplify_rate/100000)

            if st.checkbox("Show Outline on Mask"):
                mask_contours = draw_contours(cv2_mask_to_RGB(mask), contours)
                st.image(cv2_to_pil(mask_contours))

            image_contours = draw_contours(np.array(original_image), contours)
            st.image(cv2_to_pil(image_contours))

            with st.expander("Adjust Scaling (Optional)", expanded=True):
                st.markdown(
                    '''
                    Select two Points in the image and provide the distance between them in mm to get the right scaling in the exported DXF file. 
                    ''')


                resized_image_x_size, resized_image_y_size = 700, 700

                resized_image, scaling_factor = proportional_resize_image(original_image, resized_image_x_size, resized_image_y_size)

                with resized_image as img:

                    draw = ImageDraw.Draw(img)

                    if 'points' not in st.session_state:
                        st.session_state.points = []

                    for point in st.session_state.points:
                        draw.ellipse(get_ellipse_coords(point, 2), fill="red")

                    if len(st.session_state.points) == 2:
                        coordinates_tuple = tuple(coord for tup in st.session_state.points for coord in tup)
                        draw.line(coordinates_tuple, fill="red", width=1)

                    # get clicked point and transform into np array
                    clicked_point = streamlit_image_coordinates(resized_image)
                    
                    if clicked_point is not None:
                        clicked_point = tuple([clicked_point['x'], clicked_point['y']])

                        # store only last two points
                        if len(st.session_state.points) >= 2:
                            st.session_state.points.pop(0)
                            st.session_state.points.append(clicked_point)
                        else:
                            st.session_state.points.append(clicked_point)

                        st.rerun()
                
                if st.button("Reset", use_container_width=True):
                    st.session_state.points = []
                    st.rerun()

                distance = st.text_input("Distance Between Points in mm", value="50")

                # calculate distance between two points
                if len(st.session_state.points) == 2:
                    point_a, point_b = st.session_state.points
                    pixel_distance = np.linalg.norm(np.array(point_a) - np.array(point_b))

                    st.write(f"Distance between points: {pixel_distance:.2f} Pixels")

                    pixel_per_mm = pixel_distance / float(distance)
                    st.text("Pixels/mm: " + str(pixel_per_mm))


        export_container = st.empty()

        with export_container.container(border=True):
            st.title("Step 3: Export DXF File")
        
            # svg = write_svg(contours, scaling_factor=1, height=image_height, width=image_width)
            # print("svg", svg)
            # st.download_button(
            #     label="Download Outline Vectors as SVG",
            #     data=write_svg(contours, scaling_factor=10, height=image_height, width=image_width),
            #     file_name='outline_vector.svg',
            #     mime='svg',
            #     use_container_width=True
            # )

            if st.button("Generate DXF File", use_container_width=True):
                points_list = convert_contours_to_list(contours)
                points_list = mirror_points_around_center(points_list, resized_image_x_size, resized_image_y_size, 'x')
                points_list = scale_points_list(points_list, pixel_per_mm, scaling_factor)
                # create_dxf_from_contours("object_outlines.dxf", points_list)
                dxf = create_dxf_from_contours("object_outlines.dxf", points_list)
                
                # write dxf to file using st_DownloadButton
                with open('object_outlines.dxf', 'wb') as f:
                    f.write(bytes(dxf, 'utf-8'))
                st.download_button(
                    label="Download Outline Vectors as DXF (file)",
                    data=open('object_outlines.dxf', 'rb'),
                    file_name='outline_vector.dxf',
                    mime='dxf',
                    use_container_width=True
                )

    
if __name__ == '__main__':
    main_loop()