
from scipy.stats import chi2

def l_ratio(clustered_mahalanobis_squared_dict,
        degrees_of_freedom):
    cmsd = clustered_mahalanobis_squared_dict 
    df = degrees_of_freedom 

    return_dict = {}
    for key in cmsd.keys():
        if key is not 'Rejected':
            l_value = 0.0
            other_keys = [k for k in cmsd[key].keys() if 
                    k not in ['Rejected', key]]
            for other_key in other_keys:
                for d_sqrd in cmsd[key][other_key]:
                    l_value += 1.0 - chi2.cdf(d_sqrd, df)
            l_ratio = l_value/len(cmsd[key][key])
            return_dict[key] = {'l_value':l_value, 'l_ratio':l_ratio}
    return return_dict
