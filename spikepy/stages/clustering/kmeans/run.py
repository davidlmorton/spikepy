import random

def run(feature_set_list):
    result = [random.randint(-1,2) for i in xrange(len(feature_set_list))]
    print result
    return result

