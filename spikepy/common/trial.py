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
import datetime
import os
import uuid

import wx
from wx.lib.pubsub import Publisher as pub
import numpy
import scipy.io

from spikepy.common import program_text as pt
from spikepy.common import utils

text_delimiters = {pt.PLAIN_TEXT_TABS: '\t',
                   pt.PLAIN_TEXT_SPACES: ' ',
                   pt.CSV: ','}
format_extentions = {pt.PLAIN_TEXT_SPACES:'txt',
                     pt.PLAIN_TEXT_TABS:'txt',
                     pt.CSV:'csv',
                     pt.MATLAB:'mat',
                     pt.NUMPY_BINARY:'npz'}


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
        trial.mark(status=status)

    def mark_all_trials(self, status):
        """Mark all trials according to <status>"""
        for trial in self._trial_index.values():
            trial.mark(status=status)

    def add_trials(self, trial_list, proposed_name_list):
        """
            Add all the trials in <trial_list> and give them the names from
        <proposed_name_list>.
        """
        for trial, proposed_name in zip(trial_list, proposed_name_list):
            trial.display_name = self._get_unique_display_name(proposed_name)
            self._trial_index[trial.trial_id] = trial

    def remove_trial_with_name(self, name):
        """Remove the trial with display_name=<name>."""
        trial = self.get_trial_with_name(name)
        self._remove_trial(trial)

    def _remove_trial(self, trial):
        self._display_names.remove(trial.display_name)
        del self._trial_index[trial.trial_id]

    def remove_marked_trials(self):
        """Remove all currently marked trials."""
        for trial_id in self.get_marked_trial_ids():
            trial = self._trial_index[trial_id]
            self._remove_trial(trial)

    def _get_unique_display_name(self, proposed_display_name):
        count = 1
        new_display_name = proposed_display_name
        while new_display_name in self._display_names:
            new_display_name = '%s(%d)' % (proposed_display_name, count)
            count += 1
        self._display_names.add(new_display_name)
        return new_display_name

    def rename_trial(self, old_name, proposed_name):
        """Find trial named <old_name> and rename it to <proposed_name>."""
        trial = self.get_trial_with_name(old_name)
        self._display_names.remove(self.display_name)
        trial.display_name = self._get_unique_display_name(proposed_name)
        pub.sendMessage(topic='TRIAL_RENAMED', data=trial)

    def get_marked_trial_ids(self):
        """Return the trial_ids for all currently marked trials"""
        marked_ids = [trial.trial_id for trial in self._trial_index.values()
                      if trial.is_marked]
        return marked_ids

    def get_trial_with_id(self, trial_id):
        """
        Find the trial with trial_id=<trial_id> and return it.
        Raises RuntimeError if trial cannot be found.
        """
        try:
            return self._trial_index[trial_id]
        except KeyError:
            raise RuntimeError('No trial with id "%s" found.' % str(trial_id))

    def get_trial_with_name(self, name):
        """
        Find the trial with display_name=<name> and return it.
        Raises RuntimeError if trial cannot be found.
        """
        for trial in self._trial_index.values():
            if trial.display_name == name:
                return trial
        raise RuntimeError('No trial named "%s" found.' % name)
    

class Trial(object):
    """
        The Trial class carries attributes and resources pertaining to one
    recording.  The resources can be locked(checked out) and unlocked
    (checked in) allowing only one process access at a time.
    """
    def __init__(self, origin=None):
        self._marked = False
        self.display_name = None
        self._id = uuid.uuid4() 
        self.origin = origin

    def _setup_basic_attributes(self, raw_traces, sampling_freq)
        self.raw_traces = utils.format_traces(raw_traces)
        self.raw_times = numpy.arange(0, raw_traces.shape[1])/sampling_freq
        self.sampling_freq = sampling_freq
        self.num_channels = raw_traces.shape[0]

        # -------------------------------------
        # -- main processing stage resources --

        # df_traces is a 2D numpy array where
        #    len(df_traces) == num_channels
        self._add_resource(Resource('df_traces'))
        self._add_resource(Resource('df_sampling_freq')

        # events is a list of "list of indexes" where 
        #    len(events) == num_channels
        #    len(events[i]) == number of events on the ith channel
        #    events[i][j] == index of jth event on the ith channel
        self._add_resource(Resource('events'))

        # ef_traces is a 2D numpy array where
        #    len(ef_traces) == num_channels
        self._add_resource(Resource('ef_traces'))
        self._add_resource(Resource('ef_sampling_freq')

        # features is 2D numpy array with shape = (n, m) where
        #    n == the total number of events
        #    m == the number of features describing each event
        #    features[k][l] == feature l of event k
        self._add_resource(Resource('features'))

        # feature_locations is a 1D numpy array of indexes.
        #    time of kth feature == feature_locations[k]/ef_sampling_freq
        self._add_resource(Resource('feature_locations'))

        # clusters is a 1D numpy array of integers (cluster ids).
        #   clusters[k] == id of cluster to which the kth feature belongs.
        self._add_resource(Resource('clusters'))

    @classmethod
    def from_raw_traces(cls, sampling_freq=None, raw_traces=None, 
        '''Create a trial object using the raw voltage traces.'''
            origin=None, display_name=None):
        result = cls(origin=origin, display_name=display_name)
        result._setup_basic_attributes(raw_traces, sampling_freq)
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
        
    def _add_resource(self, resource):
        if hasattr(self, resource.name):
            raise RuntimeError(pt.RESOURCE_EXISTS % resource.name)
        else:
            setattr(self, resource.name, resource)

    @property
    def trial_id(self):
        return self._id

    @property
    def is_marked(self):
        return self._marked

    def mark(self, status=True):
        """Mark this trial according to <status>"""
        self._marked = status

    def get_archive(self, archive_name='archive'):
        # TODO refactor using new resources idea.
        '''
        Create and return a dictionary that includes all the data needed to
        recreate the trial object.
        '''
        return_dict = {}
        return_dict['raw_traces'] = self.raw_traces
        # obscure the fullpath in archives for security reasons.
        return_dict['fullpath'] = os.path.join(archive_name, self.display_name)
        return_dict['sampling_freq'] = self.sampling_freq
        for stage in self.stages:
            return_dict[stage.name] = self.get_data_from_stage(stage.name)
        return return_dict

    @classmethod
    def from_archive(cls, archive):
        # TODO refactor using new resources idea.
        return_trial = Trial(sampling_freq=archive['sampling_freq'],
                             raw_traces=archive['raw_traces'], 
                             fullpath=archive['fullpath'])
        for stage in return_trial.stages:
            if stage.name in archive.keys():
                data_for_stage = archive[stage.name]
                return_trial.set_data_for_stage(stage.name, **data_for_stage)
        return return_trial

    def export(self, path=None, stages_selected=[], file_format=None):
        # TODO refactor into another file using the new resources idea.
        '''
        Store the results of the stages in <stage_list> to files in <path>.
        Inputs:
            path            : The export directory (must exist)
            stage_list      : A list of strings denoting the stages results to
                              export.
            rows_or_cols    : Should sequences be stored as rows or columns.
            format          : The file format
        Returns:
            None
        '''
        for stage_name in stages_selected:
            extention = format_extentions[file_format]
            base_name = '%s-%s' % (self.display_name, stage_name)
            filename = '%s.%s' % (base_name, extention)
            fullpath = os.path.join(path, filename)
            times = self.times
            if 'raw_traces' == stage_name:
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    results = [times]
                    for trace in self.raw_traces:
                        results.append(trace)
                    delimiter = text_delimiters[file_format]
                    utils.save_list_txt(fullpath, results, 
                                  delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, times=times, 
                                raw_traces=self.raw_traces)
                elif file_format == pt.MATLAB:
                    results = {'times': times,
                               'raw_traces': self.raw_traces}
                    scipy.io.savemat(fullpath, results)
                continue
            stage_data = self.get_stage_data(stage_name)
            if stage_data.results is None:
                continue # this stage hasn't been run.
            # EXPORT FILTER STAGE
            if 'filter' in stage_name:
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    results = [times]
                    for trace in stage_data.results['traces']:
                        results.append(trace)
                    delimiter = text_delimiters[file_format]
                    utils.save_list_txt(fullpath, results, 
                                        delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, **stage_data.results)
                elif file_format == pt.MATLAB:
                    scipy.io.savemat(fullpath, stage_data.results)
            # EXPORT DETECTION STAGE
            if stage_name == 'detection':
                spike_times        = stage_data.results['spike_times']
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    delimiter = text_delimiters[file_format]
                    results = [spike_times]
                    utils.save_list_txt(fullpath, results, 
                                  delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, **stage_data.results)
                elif file_format == pt.MATLAB:
                    scipy.io.savemat(fullpath, stage_data.results)
            # EXPORT EXTRACTION STAGE
            if stage_name == 'extraction':
                features = numpy.array(stage_data.results['features'])
                feature_times = numpy.array(stage_data.results['feature_times'])
                feature_times = feature_times.reshape(1,-1)
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    for f, ft in zip(features, feature_times):
                        results.append([ft, f])
                    delimiter = text_delimiters[file_format]
                    utils.save_list_txt(fullpath, results, 
                                  delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, **stage_data.results)
                elif file_format == pt.MATLAB:
                    scipy.io.savemat(fullpath, stage_data.results)
            # EXPORT CLUSTERING STAGE
            if stage_name == 'clustering':
                sr = stage_data.results
                # store results the way you should for .mat files.
                results_dict = {}
                st_dict = sr['clustered_spike_times']
                for cluster_id, spike_times in st_dict.items():
                    key = 'cluster_%s_spike_times' % cluster_id
                    results_dict[key] = spike_times
                f_dict = sr['clustered_features']
                for cluster_id, features in f_dict.items():
                    key = 'cluster_%s_features' % cluster_id
                    results_dict[key] = features
                sw_dict = self.get_clustered_spike_windows()
                for cluster_id, sw in sw_dict.items():
                    key = 'cluster_%s_spike_windows'% cluster_id
                    results_dict[key] = sw
                # format results for .txt files.
                clustered_spike_times = sr['clustered_spike_times']
                cluster_keys = sorted(clustered_spike_times.keys())
                results = [clustered_spike_times[key] for key in cluster_keys]
                string_dict = {}
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    delimiter = text_delimiters[file_format]
                    utils.save_list_txt(fullpath, results, 
                                        delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, **sr)
                elif file_format == pt.MATLAB:
                    scipy.io.savemat(fullpath, results_dict)


class Resource(object):
    """
        The Resource class handles locking(checkout) and unlocking(checkin)
    allowing only one process to access the resource at a time.  Additionally,
    resources store metadata about how and when they were last changed and 
    by whom.
    """
    def __init__(self, name, data=None):
        self.name = name
        self._locked = False
        self._locking_key = None

        self._data = data

    def checkout(self):
        '''
            Check out this resource, locking it so that noone else can check it
        out until you've checked it in via <checkin>.
        '''
        if self.is_locked:
            raise RuntimeError(pt.RESOURCE_LOCKED % self.name)
        else:
            self._locking_key = uuid.uuid4()
            self._locked = True
            return {'name':self.name, 
                    'data':self._data, 
                    'locking_key':self._locking_key}

    def checkin(self, data_dict=None, key=None):
        '''
            Check in resource so others may use it.  If <data_dict> is
        supplied it should be a dictionary with:
            'data': the data 
            'change_info': see docstring on self.change_info
                           NOTE: This function adds 'at' and 'change_id' to
                                 'change_info' automatically, so those can
                                 be left out of the 'change_info' dictionary.
        '''
        if not self.is_locked:
            raise RuntimeError(pt.RESOURCE_NOT_LOCKED % self.name)
        else:
            if key == self._locking_key:
                self._locking_key = None
                if data_dict is not None:
                    self._data = data_dict['data']
                    self._change_info = data_dict['change_info']
                    self._change_info['at'] = datetime.datetime.now()
                    self._change_info['change_id'] = uuid.uuid4()
                self._locked = False
            else:
                raise RuntimeError(pt.RESOURCE_KEY_INVALID % 
                        (str(key), self.name))

    @property
    def is_locked(self):
        return self._locked

    @property
    def data(self):
        return self._data

    @property
    def change_info(self):
        '''
            Information describing how this resource was last changed.
        Keys:
            by : string, name of the plugin function that changed this resource.
            at : datetime, the date/time of the last change to this resource.
            with : dict, a dictionary of keyword args for the <by> function.
            using : list, a list of (trial_id, resource_name, uuid) that 
                    were used as arguments to the <by> function.  If any 
                    arguments to <by> were not resources, then entry will be 
                    (trial_id, attribute_name) of the attribute which was
                    used by the <by> function.
            change_id : a uuid generated when this resource was last changed.
        '''
        return self._change_info

    

