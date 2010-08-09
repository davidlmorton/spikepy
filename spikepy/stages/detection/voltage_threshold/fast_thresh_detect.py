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

        
