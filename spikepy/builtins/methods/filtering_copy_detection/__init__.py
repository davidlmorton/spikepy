

from spikepy.developer.methods import FilteringMethod

class FilteringCopyDetection(FilteringMethod):
    '''
    This class represents using the results of detection filtering.
    '''
    name = 'Copy Detection Filtering'
    description = 'Copy the results of the detection filtering stage.'
    is_stochastic = False
    requires = ['df_traces', 'df_sampling_freq'] # different from defaults.
    provides = ['ef_traces', 'ef_sampling_freq']

    def run(self, signal, sampling_freq, **kwargs):
        return [signal, sampling_freq]

