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

from spikepy.developer_tools.registering_class import RegisteringClass

class ClusteringMethod(object):
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
    # --- CAN OVERWRITE ---
    _is_stochastic = False

    # --- DO NOT ALTER ---
    __metaclass__ = RegisteringClass
    _skips_registration = True
    _is_base_class = True
    _is_stochastic = False
    _requires = ['features', 'feature_locations', 'ef_sampling_freq'] 

    _provides = ['clusters']
    # clusters is a 1D numpy array of integers (cluster ids).
    #   clusters[k] == id of cluster to which the kth feature belongs.
    # NOTE: while you cannot leave features 'unclustered', you may simply
    #       place all 'unclustered' features in a cluster with id=-1.
