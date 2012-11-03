
import bisect
from collections import defaultdict
import copy
import datetime
import os
import uuid

import wx
import numpy
import scipy.io

try:
    from callbacks import supports_callbacks
except ImportError:
    from spikepy.other.callbacks.callbacks import supports_callbacks

from spikepy.common import program_text as pt
from spikepy.utils.substring_dict import SubstringDict 
from spikepy.utils.cluster_data import cluster_data
from spikepy.common.errors import *
from spikepy.common.task_manager import Resource

def zero_mean(a):
    return a - numpy.average(a)

def format_traces(trace_list):
    result = numpy.empty((len(trace_list), len(trace_list[0])), 
            dtype=numpy.float64)
    for i, trace in enumerate(trace_list):
        result[i,:] = zero_mean(numpy.array(trace, dtype=numpy.float64))
    return result

class TrialManager(object):
    """
        The TrialManager keeps track of all the trials currently in the
    session.  It handles marking/unmarking, adding/removing trials, and 
    assigning unique display names to trials.
    """
    def __init__(self):
        self._trial_index = {}
        self._display_names = set()

    def mark_trial(self, name, status):
        """Mark trial with display_name=<name> according to <status>."""
        trial = self.get_trial_with_name(name)
        assert type(status) is bool

        if self.marked_trials:
            num_channels = self.marked_trials[0].num_channels
            if trial.num_channels != num_channels and status:
                raise CannotMarkTrialError('Cannot mark a trial with %d channels, since trials with %d channels are already marked.' % (trial.num_channels, num_channels))
        trial.mark(status=status)
        return trial.trial_id, trial.is_marked

    @supports_callbacks 
    def add_trials(self, trial_list, marked=True):
        """
            Add all the trials in <trial_list> and ensure they have unique
        names.
        """
        new_names = []
        for trial in trial_list:
            if trial.trial_id in self._trial_index.keys():
                trial.reset_trial_id()
            new_name = self._get_unique_display_name(trial.display_name)
            trial.display_name = new_name
            new_names.append(new_name)
            self._trial_index[trial.trial_id] = trial

        for name in new_names:
            try:
                self.mark_trial(name, marked)
            except CannotMarkTrialError:
                pass
        return trial_list

    def remove_trial(self, trial):
        self._display_names.remove(trial.display_name)
        del self._trial_index[trial.trial_id]
        return trial.trial_id

    def _get_unique_display_name(self, proposed_display_name):
        count = 1
        new_display_name = proposed_display_name
        while new_display_name in self._display_names:
            new_display_name = '%s(%d)' % (proposed_display_name, count)
            count += 1
        self._display_names.add(new_display_name)
        return new_display_name

    @property
    def all_display_names(self):
        return self._display_names 

    def rename_trial(self, old_name, proposed_name):
        """Find trial named <old_name> and rename it to <proposed_name>."""
        trial = self.get_trial_with_name(old_name)
        self._display_names.remove(trial.display_name)
        trial.display_name = self._get_unique_display_name(proposed_name)
        return trial

    @property
    def marked_trials(self):
        '''Return all currently marked trials.'''
        return [trial for trial in self._trial_index.values()
                if trial.is_marked]

    @property
    def marked_trial_ids(self):
        """Return the trial_ids for all currently marked trials"""
        marked_ids = [trial.trial_id for trial in self.get_marked_trials()]
        return marked_ids

    @property
    def trials(self):
        '''Return all currently marked and unmarked trials.'''
        return self._trial_index.values()

    def get_trial_with_id(self, trial_id):
        """
        Find the trial with trial_id=<trial_id> and return it.
        Raises MissingTrialError if trial cannot be found.
        """
        try:
            return self._trial_index[trial_id]
        except KeyError:
            raise MissingTrialError('No trial with id "%s" found.' % 
                    str(trial_id))

    @property
    def _trial_name_index(self):
        tni = SubstringDict()
        for trial in self._trial_index.values():
            tni[trial.display_name] = trial
        return tni

    def get_trial_with_name(self, name):
        """
        Find the trial with display_name=<name> and return it.
        Raises MissingTrialError if trial cannot be found.
        """
        try:
            return self._trial_name_index[name]
        except KeyError:
            raise MissingTrialError('No trial named "%s" found.' % name)

    def __str__(self):
        return_str =     ['Trial Manager with trials:']
        return_str.append('    Marked  Display Name')
        return_str.append('    ------  ------------')
        marked = {False:' ', True:'X'}
        for trial in self._trial_index.values():
            return_str.append('       [%s]  %s' % 
                    (marked[trial.is_marked], trial.display_name))
        return '\n'.join(return_str) 
    

class Trial(object):
    """
        The Trial class carries attributes and resources pertaining to one
    recording.  The resources can be locked(checked out) and unlocked
    (checked in) allowing only one process access at a time.
    """
    def __init__(self, origin=None, display_name="DEFAULT_DISPLAY_NAME"):
        self._marked = False
        self.display_name = display_name
        self._id = uuid.uuid4() 
        self.origin = origin
        self.originates = [] # list of resources the trial originally has.

    @property
    def num_channels(self):
        if hasattr(self, 'raw_traces'):
            return self.raw_traces.shape[0]
        else:
            return 0

    def get_times(self, signal, sampling_freq):
        return numpy.arange(0, signal.shape[1], 
                dtype=signal.dtype)/sampling_freq*1000.0

    def _setup_basic_attributes(self, raw_traces, sampling_freq):
        self.raw_traces = format_traces(raw_traces)
        self.raw_times = self.get_times(self.raw_traces, sampling_freq)
        self.sampling_freq = sampling_freq

        # -------------------------------------
        # -- main processing stage resources --
        # pf_traces is a 2D numpy array where (pre-filtering)
        #    len(pf_traces) == num_channels
        self.add_resource(Resource('pf_traces', data=self.raw_traces))
        self.add_resource(Resource('pf_sampling_freq', data=self.sampling_freq))
        
        # df_traces is a 2D numpy array where (detection-filtering)
        #    len(df_traces) == num_channels
        self.add_resource(Resource('df_traces'))
        self.add_resource(Resource('df_sampling_freq'))

        self.add_resource(Resource('df_psd'))
        self.add_resource(Resource('df_freqs'))

        # events is a list of "list of times" where 
        #    len(event_times) == num_channels
        #    len(event_times[i]) == number of events on the ith channel
        #    events[i][j] == time of jth event on the ith channel
        self.add_resource(Resource('event_times'))

        # ef_traces is a 2D numpy array where (extraction-filtering)
        #    len(ef_traces) == num_channels
        self.add_resource(Resource('ef_traces'))
        self.add_resource(Resource('ef_sampling_freq'))

        self.add_resource(Resource('ef_psd'))
        self.add_resource(Resource('ef_freqs'))

        # features is 2D numpy array with shape = (n, m) where
        #    n == the total number of events with features
        #    m == the number of features describing each event
        #    features[k][l] == feature l of event k
        self.add_resource(Resource('features'))
        self.add_resource(Resource('feature_times'))

        # clusters is a 1D numpy array of integers (cluster ids).
        #   clusters[k] == id of cluster to which the kth feature belongs.
        self.add_resource(Resource('clusters'))

    @classmethod
    def from_raw_traces(cls, sampling_freq=None, raw_traces=None, 
            origin=None, display_name=None):
        '''Create a trial object using the raw voltage traces.'''
        result = cls(origin=origin, display_name=display_name)
        result._setup_basic_attributes(raw_traces, sampling_freq)
        result.originates = [result.pf_traces, result.pf_sampling_freq]
        return result

    @classmethod
    def from_spike_windows(cls, sampling_freq=None, spike_windows=None,
            spike_times=None):
        '''
            Create a trial object using just spike_windows and the times when
        they were gathered.  The only stages which still make sense after
        that are feature_extraction and clustering.
        '''
        raise NotImplementedError

    @classmethod
    def from_dict(cls, info_dict):
        '''Create a trial from a dictionary, likely from an archive.'''
        new_trial = cls()
        for key, value in info_dict.items():
            if not isinstance(value, dict):
                setattr(new_trial, key, value)
            else: # is a resource
                setattr(new_trial, key, Resource.from_dict(value))
        return new_trial

    @property
    def as_dict(self):
        '''
            Create the dictionary that has all data from this trial, 
        for archiving.
        '''
        info_dict = {}
        info_dict['_id'] = self.trial_id
        info_dict['origin'] = self.origin
        info_dict['display_name'] = self.display_name
        for resource in self.resources:
            info_dict[resource.name] = resource.as_dict
        return info_dict

    def _cluster_data(self, data):
        if self.clusters.data is not None:
            clusters = self.clusters.data
            return cluster_data(clusters, data)
        else:
            raise NoClustersError('Cannot fetch clustered data, clustering not yet run.')
        
    @property
    def clustered_features(self):
        return self._cluster_data(self.features.data)

    @property
    def clustered_feature_times(self):
        return self._cluster_data(self.feature_times.data)

    @property
    def clustered_df_spike_windows(self):
        if not hasattr(self, 'df_spike_windows') or not\
                hasattr(self, 'df_spike_window_times'):
            raise MissingResourceError(
                    'Missing "df_spike_windows" or "df_spike_window_times')

        spike_windows = self.df_spike_windows.data
        spike_window_times = self.df_spike_window_times.data
        return self._cluster_spike_windows(spike_windows, spike_window_times)

    @property
    def clustered_ef_spike_windows(self):
        if not hasattr(self, 'ef_spike_windows') or not\
                hasattr(self, 'ef_spike_window_times'):
            raise MissingResourceError(
                    'Missing "ef_spike_windows" or "ef_spike_window_times')

        spike_windows = self.ef_spike_windows.data
        spike_window_times = self.ef_spike_window_times.data
        return self._cluster_spike_windows(spike_windows, spike_window_times)

    def _cluster_spike_windows(self, spike_windows, spike_window_times):
        cft = self.clustered_feature_times
        window_len = spike_windows.shape[1]
        
        result = {}
        for cluster_id, feature_times in cft.items():
            result[cluster_id] = numpy.empty((len(feature_times), window_len),
                    dtype=spike_windows.dtype)
            for i, feature_time in enumerate(feature_times):
                sw_index = bisect.bisect_left(spike_window_times, feature_time)
                result[cluster_id][i] = spike_windows[sw_index]
        return result

    @property
    def clustered_features_as_list(self):
        return self._clustered_thing_as_list(self.clustered_features)

    @property
    def clustered_feature_times_as_list(self):
        return self._clustered_thing_as_list(self.clustered_feature_times)

    def _clustered_thing_as_list(self, thing):
        return_list = []
        for cluster_id in sorted(thing.keys()):
            return_list.append(thing[cluster_id])
        return return_list

    @property
    def resources(self):
        '''Return all resources this trial contains in a list.'''
        result = []
        for key, value in self.__dict__.items():
            if isinstance(value, Resource):
                result.append(value)
        return result
        
    def add_resource(self, resource):
        '''Add <resource> to this trial.'''
        if hasattr(self, resource.name):
            raise AddResourceError(pt.RESOURCE_EXISTS % resource.name)
        else:
            setattr(self, resource.name, resource)

    @property
    def trial_id(self):
        return self._id

    def reset_trial_id(self):
        self._id = uuid.uuid4()

    @property
    def is_marked(self):
        return self._marked

    def mark(self, status=True):
        """Mark this trial according to <status>"""
        self._marked = status



