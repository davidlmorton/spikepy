#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from spikepy.common.valid_types import ValidType
from spikepy.developer.spikepy_plugin import SpikepyPlugin

class SpikepyMethod(SpikepyPlugin):
    #     If is_pooling = True, this method will pool all the inputs from 
    # multiple trials and run on the pooled data, otherwise, the method is 
    # run on each trial separately. 
    # (i.e. clustering_method has is_pooling=True by default)
    is_pooling = False
    #     If is_pooling, this variable determines how the pooling is actually
    # carried out.  silent_pooling = True will pool the 'requires' resources
    # in such a way that the plugin doesn't know whether the resource came
    # from one trial or many trials.  If silent_pooling = False then the
    # pooler will pool the resources just by sending a list of resources,
    # where the list is equal in length to the number of trials.
    silent_pooling = True
    #     unpool_as is a list of 'requires' resource names or None
    # equal in length to the length of the 'provides' list.  Each element
    # in this list tells the pooler how to unpool the resource, since the
    # pooler knows how it pooled the corresponding 'requires' resource.
    # if unpool_as is not a list but is None, data are provided identically
    # to all trials.
    # Note: unpool_as is ignored if silent_pooling is False
    unpool_as = None # if None then no unpooling will be done
    #     Is this method stochastic in nature (generally gives different results
    # with the same inputs)?
    is_stochastic = False

    #     What resources does this method need in order to run?
    requires = []
    provides = [] 

    def run(self, *args, **kwargs):
        raise NotImplementedError 


class FilteringMethod(SpikepyMethod):
    '''
        This class should be subclassed in order for developers to add a new 
    filtering method to spikepy.
        There is no need to instantiate (create an object from) the subclass, 
    spikepy will handle that internally.  Therefore it is important to have 
    an __init__ method which requires no arguments (aside from 'self' 
    of course).

    Method that subclasses are REQUIRED to implement:
        - run(*args, **kwargs)
            -- This method returns the method's result.  *args is built by
               spikepy based on the <_requires> class-variable defined below or
               in subclasses.  **kwargs are any additional arguments you wish to
               pass in.
            -- The <_provides> class-variable tells spikepy where to store the
               results in the trial object.  Spikepy will create a resource for
               storing the result if the name(s) provided do not already 
               correspond to resources that already exist.
    '''
    requires = ['pf_traces', 'pf_sampling_freq']
    # <stage_name> is one of "df" or "ef" for detection and extraction.
    # <stage_name>_traces is a 2D numpy array where
    #    len(<stage_name>_traces) == num_channels
    provides = ['<stage_name>_traces', '<stage_name>_sampling_freq'] 


class DetectionMethod(SpikepyMethod):
    '''
        This class should be subclassed in order for developers to add a new 
    spike detection method to spikepy.
        There is no need to instantiate (create an object from) the subclass, 
    spikepy will handle that internally.  Therefore it is important to have 
    an __init__ method which requires no arguments (asside from 'self' 
    of course).

    Method that subclasses are REQUIRED to implement:
        - run(*args, **kwargs)
            -- This method returns the method's result.  *args is built by
               spikepy based on the <_requires> class-variable defined below or
               in subclasses.  **kwargs are any additional arguments you wish to
               pass in.
            -- The <_provides> class-variable tells spikepy where to store the
               results in the trial object.  Spikepy will create a resource for
               storing the result if the name(s) provided do not already 
               correspond to resources that already exist.
    '''
    requires = ['df_traces', 'df_sampling_freq']
    # event_times is a list of "list of indexes" where 
    #    len(event_times) == num_channels
    #    len(event_times[i]) == number of events on the ith channel
    #    event_times[i][j] == time of jth event on the ith channel
    provides = ['event_times']


class ExtractionMethod(SpikepyMethod):
    '''
        This class should be subclassed in order for developers to add a new 
    feature-extraction method to spikepy.
        There is no need to instantiate (create an object from) the subclass, 
    spikepy will handle that internally.  Therefore it is important to have 
    an __init__ method which requires no arguments (asside from 'self' 
    of course).

    Method that subclasses are REQUIRED to implement:
        - run(*args, **kwargs)
            -- This method returns the method's result.  *args is built by
               spikepy based on the <_requires> class-variable defined below or
               in subclasses.  **kwargs are any additional arguments you wish to
               pass in.
            -- The <_provides> class-variable tells spikepy where to store the
               results in the trial object.  Spikepy will create a resource for
               storing the result if the name(s) provided do not already 
               correspond to resources that already exist.
    '''
    requires = ['ef_traces', 'ef_sampling_freq', 'event_times']
    # features is 2D numpy array with shape = (n, m) where
    #    n == the total number of kept events
    #    m == the number of features describing each event
    #    features[k][l] == feature l of event k
    # feature_locations is a 1D numpy array of indexes.
    #    time of kth feature == feature_locations[k]/ef_sampling_freq
    provides = ['features', 'feature_times']


class ClusteringMethod(SpikepyMethod):
    '''
        This class should be subclassed in order for developers to add a new 
    clustering method to spikepy.
        There is no need to instantiate (create an object from) the subclass, 
    spikepy will handle that internally.  Therefore it is important to have 
    an __init__ method which requires no arguments (asside from 'self' 
    of course).

    NOTE: Clustering is unique among stages in spikepy because it takes input
          from multiple trials.  This is so that you can cluster using 
          data from multiple trials together.  Spikepy automatically compiles
          features from multiple trials into a single array before calling a
          clustering method.  Spikepy also automatically parses out results
          to the appropriate trials when clustering methods return.  What this
          means is that the clustering-method author need not worry about
          if the provided features are from multiple trials or a single trial.

    Method that subclasses are REQUIRED to implement:
            -- This method returns the method's result.  *args is built by
               spikepy based on the <_requires> class-variable defined below or
               in subclasses.  **kwargs are any additional arguments you wish to
               pass in.
            -- The <_provides> class-variable tells spikepy where to store the
               results in the trial object.  Spikepy will create a resource for
               storing the result if the name(s) provided do not already 
               correspond to resources that already exist.
    '''
    is_pooling = True
    silent_pooling = True
    requires = ['features'] 
    # clusters is a 1D numpy array of integers (cluster ids).
    #   clusters[k] == id of cluster to which the kth feature belongs.
    # NOTE: while you cannot leave features unclustered, you can *reject*
    # features by placing all rejected features in a cluster with id=-1.
    provides = ['clusters']
    unpool_as = ['features']


class AuxiliaryMethod(SpikepyMethod):
    '''
        This class should be subclassed in order for developers to add a new 
    auxiliary method to spikepy.  For example, a method to calculate the
    principal components of a set of features, or the L factor of a cluster set.
        There is no need to instantiate (create an object from) the subclass, 
    spikepy will handle that internally.  Therefore it is important to have 
    an __init__ method which requires no arguments (asside from 'self' 
    of course).

    Method that subclasses are REQUIRED to implement:
        - run(*args, **kwargs)
            -- This method returns the method's result.  *args is built by
               spikepy based on the <_requires> class-variable defined below or
               in subclasses.  **kwargs are any additional arguments you wish to
               pass in.
            -- The <_provides> class-variable tells spikepy where to store the
               results in the trial object.  Spikepy will create a resource for
               storing the result if the name(s) provided do not already 
               correspond to resources that already exist.
    '''
    #     Control Panel for this method will be grouped with the following
    # stage.  Also, this method will run with the given stage if the user 
    # chooses to run a single stage instead of a complete strategy (Assuming 
    # this method is part of the current strategy).  Must be one of 
    # 'detection_filter', 'detection', 'extraction_filter', 'extraction', 
    # 'clustering', or 'auxiliary'.
    runs_with_stage = 'auxiliary'

            
