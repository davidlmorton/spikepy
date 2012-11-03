

from spikepy.developer.methods import FilteringMethod

class NoFiltering(FilteringMethod):
    ''' This class implements a NULL filtering method.  '''
    name = "No Filtering"
    description = "No Filtering, simply use the raw traces."
    is_stochastic = False

    def run(self, signal, sampling_freq, **kwargs):
        return [signal, sampling_freq]

