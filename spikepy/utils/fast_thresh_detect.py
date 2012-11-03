
    ia = input_array - threshold
    crossings = argwhere( (ia * roll(ia,  -1))<0.0 ).flatten()
    
    return crossings

        
