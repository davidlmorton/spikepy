import scipy.weave as weave

def fast_thresh_detect(input_array, threshold=0.0, 
                                    refractory_period=10):
    """
    This function finds the indexes of an input_array where 
        a threshold crossing is about to occur.  All is done with
        scipy.weave so it should be wicked fast.
    Inputs:
        input_array              : a numpy array (1-dimensional) holding 
                                   floats.
        --kwargs--
        threshold=0.0            : the threshold value
        refractory_period=10     : how many data points must exist between
                                   two crossings of the same type (pos/neg).
    Returns:
        p_crossings     : indexes where next value in input_array would have 
                          rose above the threshold from below.
        n_crossings     : indexes where next value in input_array would have 
                          fallen below the threshold from above.
    """
    p_crossings = []
    n_crossings = []
    
    # write the c code:
    c_code = r"""
        int i;
        int p=-refractory_period;
        int n=-refractory_period;
        for(i=0; i<Ninput_array[0]; i++){
            if(i >= p+refractory_period &&
               input_array[i] < threshold &&
               input_array[i+1] >= threshold){
                p = i;
                p_crossings.append(i);
                }
            else if(i >= n+refractory_period && 
                    input_array[i] > threshold &&
                    input_array[i+1] <= threshold){
                n = i;
                n_crossings.append(i);
                }
            }
        """
    # compile and exicute the c code.
    '''
    try:
        weave.inline(c_code, ['input_array', 'threshold', 'refractory_period', 'p_crossings', 'n_crossings'])       
    except:
    '''
    # do it all in python.
    if 1:
        p = -refractory_period
        n = -refractory_period
        for i in xrange(len(input_array)-1):
            if ( i >= p+refractory_period and
                 input_array[i] < threshold and
                 input_array[i+1] >= threshold ):
                p = i
                p_crossings.append(i)
            elif ( i >= n+refractory_period and
                    input_array[i] > threshold and
                    input_array[i+1] <= threshold ):
                n = i
                n_crossings.append(i)
    return p_crossings, n_crossings
        
