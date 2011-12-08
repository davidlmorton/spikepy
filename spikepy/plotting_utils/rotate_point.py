"""
Copyright (C) 2011  jeff pobst 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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

