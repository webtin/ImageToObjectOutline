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