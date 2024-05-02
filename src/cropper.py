import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image

def convert_coordinates_dict_to_tuple(data):
    left = data['left'] + 2
    top = data['top'] + 2
    width = data['width']
    height = data['height']
    right = left + width + 4
    bottom = top + height + 4
    return (left, right, top, bottom)

# Upload an image and set some options for demo purposes
st.header("Cropper Demo")

image = st.file_uploader("Upload Your Image", type=['jpg', 'png', 'jpeg'], accept_multiple_files=False)

if image:
    img_file = Image.open(image)

    # check if coordinates already available, if not use cropper box algorythm
    if 'coordinates' in st.session_state:
        print("coordinates already available")
        # st.session_state.coordinates = (10, 100, 10, 100)
        print("before moving",st.session_state.coordinates)
        cropped_img, st.session_state.coordinates= st_cropper(img_file, realtime_update=True, box_color='#0000FF', return_type="both", default_coords=st.session_state.coordinates)
        st.session_state.coordinates = convert_coordinates_dict_to_tuple(st.session_state.coordinates)
        print("after moving ", st.session_state.coordinates)

    else:
        print("no coordinates")
        cropped_img, st.session_state.coordinates = st_cropper(img_file, realtime_update=True, box_color='#0000FF', return_type="both")
        st.session_state.coordinates = convert_coordinates_dict_to_tuple(st.session_state.coordinates)
        print("new coordinates", st.session_state.coordinates)

    st.image(cropped_img)