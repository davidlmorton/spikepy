#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


from numpy import roll, argwhere

def fast_thresh_detect(input_array, threshold=0.0):
    """
    This function finds the indexes of an input_array where 
        a threshold crossing is about to occur.
    Inputs:
        input_array              : a numpy array (1-dimensional) holding 
                                   floats.
        --kwargs--
        threshold=0.0            : the threshold value
    Returns:
        crossings       : a numpy array of index values.
    """
    ia = input_array - threshold
    crossings = argwhere( (ia * roll(ia,  -1))<0.0 ).flatten()
    
    return crossings

        
