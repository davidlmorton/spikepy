

import numpy

def rotate_point(old_x, old_y, angle_deg):
    '''
    Given an x and y coordinate, return the rotated point, rotating <angle_deg>
    counter-clockwise.
    '''
    angle_rad = angle_deg * numpy.pi/180
    new_x = old_x * numpy.cos(angle_rad) - old_y * numpy.sin(angle_rad)
    new_y = old_x * numpy.sin(angle_rad) + old_y * numpy.cos(angle_rad)
    return (new_x, new_y)

