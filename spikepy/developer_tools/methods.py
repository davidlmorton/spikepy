"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from spikepy.common.valid_types import ValidType

class SpikepyMethod(object):
    #     If True, this method will pool all the inputs from multiple trials
    # and run on the pooled data, otherwise, the method is run on each trial
    # separately. (i.e. clustering_method has pooling=True by default)
    pooling = False

    #     Is this method stochastic in nature (generally gives different results
    # with the same inputs)?
    is_stochastic = False

    # what resources or attributes (of Trial objects) does this method need 
    # in order to run?
    requires = []
    provides = [] 

    def run(*args, **kwargs):
        raise NotImplementedError 

    def get_parameter_attributes(self):
        ''' Return a dictionary of ValidType attributes. '''
        attrs = {}
        attribute_names = dir(self)
        for name in attribute_names:
            value = getattr(self, name)
            if isinstance(value, ValidType):
                attrs[name] = value
        return attrs
    
    def get_parameter_defaults(self):
        ''' Return a dictionary containing the default parameter values.  '''
        kwargs = {}
        for attr_name, attr in self.get_parameter_attributes().items():
            kwargs[attr_name] = attr()
        return kwargs

    def validate_parameters(self, parameter_dict):
        '''
            Attempts to validate parameters in a dictionary.  If parameters are 
        invalid an exception is raised.  If parameters are valid, None is 
        returned.
        '''
        for key, value in parameter_dict.items():
            getattr(self, key)(value)


class FilteringMethod(SpikepyMethod):
    '''
    This class should be subclassed in order for developers to add a new 
filtering method to spikepy.
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Methods that subclasses are REQUIRED to implement:
    - run(raw_traces, sampling_freq, **kwargs)
        -- This method returns the filtered results and the new sampling_freq.
           It should return a list of filtered signals and the sampling_freq 
           of the new signals.  kwargs are all the arguments to the filtering 
           code.
    '''
    requires = ['pf_traces', 'pf_sampling_freq']
    provides = ['<stage_name>_traces', '<stage_name>_sampling_freq'] 
    # <stage_name> is one of "df" or "ef" for detection and extraction.
    # <stage_name>_traces is a 2D numpy array where
    #    len(<stage_name>_traces) == num_channels


class DetectionMethod(SpikepyMethod):
    '''
    This class should be subclassed in order for developers to add a new 
spike detection method to spikepy.
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Methods that subclasses are REQUIRED to implement:
    - make_control_panel(parent, **kwargs)
        -- This method returns a wx.Panel object (or a subclass) that acts as 
           the control panel for the new method.  kwargs should be 
           passed to the wx.Panel constructor.
    - run(signal_list, sampling_freq, **kwargs)
        -- This method returns the list of spike locations (index of spike).  
           kwargs are all the arguments to the new method's code.
    '''
    requires = ['df_traces', 'df_sampling_freq']
    provides = ['event_times']
    # event_times is a list of "list of indexes" where 
    #    len(events) == num_channels
    #    len(events[i]) == number of events on the ith channel
    #    events[i][j] == index of jth event on the ith channel


class ExtractionMethod(SpikepyMethod):
    '''
    This class should be subclassed in order for developers to add a new 
feature-extraction method to spikepy.
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Methods that subclasses are REQUIRED to implement:
    - make_control_panel(parent, **kwargs)
        -- This method returns a wx.Panel object (or a subclass) that acts as 
           the control panel for the new method.  kwargs should be 
           passed to the wx.Panel constructor.
    - run(signal_list, sampling_freq, events, **kwargs)
        -- This method returns the features.  kwargs are all the arguments
           to the feature-extraction code.
    '''
    requires = ['ef_traces', 'ef_sampling_freq', 'event_times']
    provides = ['features', 'feature_times']
    # features is 2D numpy array with shape = (n, m) where
    #    n == the total number of kept events
    #    m == the number of features describing each event
    #    features[k][l] == feature l of event k
    # feature_locations is a 1D numpy array of indexes.
    #    time of kth feature == feature_locations[k]/ef_sampling_freq


class ClusteringMethod(SpikepyMethod):
    '''
    This class should be subclassed in order for developers to add a new 
clustering method to spikepy.
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Methods that subclasses are REQUIRED to implement:
    - make_control_panel(parent, **kwargs)
        -- This method returns a wx.Panel object (or a subclass) that acts as 
           the control panel for the new method.  kwargs should be 
           passed to the wx.Panel constructor.
    - run(features, feature_locations, ef_sampling_freq, **kwargs)
        -- This method returns the clustered results.  kwargs 
           are all the arguments to the new method's code.
    NOTE: Clustering is unique among stages in spikepy because it takes input
          from multiple trials.  This is so that you can cluster using 
          data from multiple trials together.  Spikepy automatically compiles
          features from multiple trials into a list before calling a
          clustering method.  Spikepy also automatically parses out results
          to the appropriate trials when clustering methods return.  What this
          means is that the clustering-method author need not worry about
          if the provided features are from multiple trials or a single trial.
    '''
    pooling = True
    requires = ['features', 'feature_times', 'ef_sampling_freq'] 
    provides = ['clusters']
    # clusters is a 1D numpy array of integers (cluster ids).
    #   clusters[k] == id of cluster to which the kth feature belongs.
    # NOTE: while you cannot leave features 'unclustered', you may simply
    #       place all 'unclustered' features in a cluster with id=-1.


class AuxiliaryMethod(SpikepyMethod):
    '''
    This class should be subclassed in order for developers to add a new 
auxiliary method to spikepy.  For example, a method to calculate the
principal components of a set of features, or the L factor of a cluster set.
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Method that subclasses are REQUIRED to implement:
    - run(*args, **kwargs)
        -- This method returns the auxiliary result.  *args is built by
           spikepy based on the <_requires> class-variable defined below or
           in subclasses.  **kwargs are any additional arguments you wish to
           pass in.
        -- The <_provides> class-variable tells spikepy where to store the
           results in the trial object.  Spikepy will create a resource for
           storing the result if the name(s) provided do not already correspond
           to resources previously defined.
    '''
    group = None
    runs_with_stage = 'auxiliary'



            
