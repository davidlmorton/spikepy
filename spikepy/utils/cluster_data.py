
from collections import defaultdict

import numpy


def cluster_data(clusters, data):
    '''
        Given the cluster identities and data return a dictionary keyed on
    cluster identity with data in the form of a numpy array.
    '''
    adict = defaultdict(list)
    for cluster_id, thing in zip(clusters, data):
        if cluster_id == -1:
            adict['Rejected'].append(thing)
        else:
            adict[cluster_id].append(thing)

    for key in adict.keys():
        adict[key] = numpy.array(adict[key])

    return dict(adict)
    
