
import numpy

def isolation_distance(clustered_mahalanobis_squared_dict):
    cmsd = clustered_mahalanobis_squared_dict 

    return_dict = {}
    for key in cmsd.keys():
        if key is not 'Rejected':
            other_distances = [cmsd[key][k] for k in cmsd.keys() if
                    k not in [key, 'Rejected']]
            other_distances = numpy.sort(numpy.hstack(other_distances))
            if len(other_distances) >= len(cmsd[key][key]):
                return_dict[key] = other_distances[len(cmsd[key][key])]
            else:
                return_dict[key] = -1.0
    return return_dict
