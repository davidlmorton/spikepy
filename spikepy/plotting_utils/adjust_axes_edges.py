

def as_fraction(x=None, y=None, canvas_size_in_pixels=None):
    if x is not None and y is not None:
        return x/canvas_size_in_pixels[0], y/canvas_size_in_pixels[1]
    elif x is not None:
        return x/canvas_size_in_pixels[0]
    elif y is not None:
        return y/canvas_size_in_pixels[1]

def adjust_axes_edges(axes, canvas_size_in_pixels=None, 
                            top=0.0, 
                            bottom=0.0, 
                            left=0.0, 
                            right=0.0):
    '''
    Adjusts the axes edge positions relative to the center of the axes.
        POSITIVE -> OUTWARD or growing the axes
        NEGATIVE -> INWARD or shrinking the axes
    If canvas_size_in_pixels is provided and not None then adjustments
        are in pixels, otherwise they are in percentage of the figure size.
    Returns:
        box         : the bbox for the axis after it has been adjusted.
    '''
    # adjust to percentages of canvas size.
    if canvas_size_in_pixels is not None: 
        left, top = as_fraction(left, top, canvas_size_in_pixels)
        right, bottom = as_fraction(right, bottom, canvas_size_in_pixels)
        
    'Moves given edge of axes by a fraction of the figure size.'
    box = axes.get_position()
    if top is not None:
        box.p1 = (box.p1[0], box.p1[1]+top)
    if bottom is not None:
        box.p0 = (box.p0[0], box.p0[1]-bottom)
    if left is not None:
        box.p0 = (box.p0[0]-left, box.p0[1])
    if right is not None:
        box.p1 = (box.p1[0]+right, box.p1[1])
    axes.set_position(box)
    return box

