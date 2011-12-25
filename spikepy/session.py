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
import threading
import multiprocessing
import uuid
import cPickle
import os

try:
    from callbacks import supports_callbacks
except ImportError:
    from spikepy.other.callbacks.callbacks import supports_callbacks

from spikepy.common.trial_manager import TrialManager, Trial
from spikepy.common.process_manager import ProcessManager
from spikepy.common.config_manager import ConfigManager
from spikepy.common.plugin_manager import PluginManager
from spikepy.common.strategy_manager import StrategyManager, Strategy
from spikepy.common import path_utils

class Session(object):
    def __init__(self):
        path_utils.setup_user_directories(app_name='spikepy')

        self.config_manager   = ConfigManager()
        self.trial_manager    = TrialManager(self.config_manager)
        self.plugin_manager   = PluginManager(self.config_manager, 
                app_name='spikepy')
        self.strategy_manager = StrategyManager(self.config_manager)
        self.strategy_manager.load_all_strategies()
        self.strategy_manager.current_strategy = self._make_default_strategy()
        self.process_manager  = ProcessManager(self.config_manager, 
                self.trial_manager, self.plugin_manager)

        # register callback for open_files
        self.process_manager.open_files.add_callback(self._files_opened,
                takes_target_results=True)


    # FILE RELATED
    def export(self, data_interpreter_name, base_path=None, **kwargs):
        if base_path is None:
            base_path = os.getcwd()

        di = self.plugin_manager.data_interpreters[data_interpreter_name]
        return di.write_data_file(self.marked_trials, base_path, **kwargs)

    def load(self, filename):
        """Load session from a file."""
        return self.open_file(filename)

    def open_file(self, fullpath):
        """Open file located at fullpath."""
        return self.process_manager.open_file(fullpath)

    @supports_callbacks
    def open_files(self, fullpaths):
        """Open the files located at fullpaths"""
        return self.process_manager.open_files(fullpaths)

    def save(self, filename):
        """Save this session."""
        if not filename.endswith('.ses'):
            filename = '%s.ses' % filename

        trial_dicts = []
        for trial in self.trials:
            trial_dicts.append(trial.as_dict)
        strategy_dict = self.current_strategy.as_dict
        session_dict = {'trials':trial_dicts, 'strategy':strategy_dict}
        with open(filename, 'wb') as ofile:
            cPickle.dump(session_dict, ofile, protocol=-1)
        return filename

    # TRIAL RELATED
    def get_trial(self, name_or_id):
        """Return the trial with the given name or id"""
        if isinstance(name_or_id, uuid.UUID):
            return self.trial_manager.get_trial_with_id(name_or_id)
        else:
            return self.trial_manager.get_trial_with_name(name_or_id)

    def get_trial_with_name(self, name):
        """
        Find the trial with display_name=<name> and return it.
        Raises RuntimeError if trial cannot be found.
        """
        return self.trial_manager.get_trial_with_name(name)

    def mark_all_trials(self, status=True):
        """Mark all trials according to <status>"""
        for trial in self.trials.values():
            try:
                self.mark_trial(trial.name, status)
            except CannotMarkTrialError:
                pass

    @supports_callbacks
    def mark_trial(self, name_or_id, status=True):
        """Mark trial with name_or_id according to <status>."""
        trial = self.get_trial(name_or_id)
        return self.trial_manager.mark_trial(trial.display_name, status=status)

    @property
    def marked_trials(self):
        '''Return all currently marked trials.'''
        return self.trial_manager.marked_trials

    def remove_marked_trials(self):
        """Remove all currently marked trials."""
        results = []
        for trial in self.marked_trials:
            results.append(self.remove_trial(self.marked_trials))
        return results

    @supports_callbacks
    def remove_trial(self, name_or_id):
        """Remove the trial with name or id given."""
        trial = self.get_trial(name_or_id)
        return self.trial_manager.remove_trial(trial)

    @supports_callbacks
    def rename_trial(self, old_name_or_id, proposed_name):
        """Find trial with <old_name_or_id> and rename it to <proposed_name>."""
        trial = self.get_trial(old_name_or_id)
        return self.trial_manager.rename_trial(trial.display_name, 
                proposed_name)

    @property
    def trials(self):
        '''Return all currently marked and unmarked trials.'''
        return self.trial_manager.trials

    def visualize(self, trial_name, visualization_name, **kwargs):
        """
            Generate and display the visualization with the given 
        <visualization_name> (or name subset) using the trial with 
        name <trial_name>.
        """
        visualization = self.plugin_manager.visualizations[visualization_name]
        trial = self.get_trial(trial_name)

        return visualization.draw(trial, **kwargs)

    # STRATEGY RELATED
    @property
    def current_strategy(self):
        """The currently selected strategy."""
        return self.strategy_manager.current_strategy

    @current_strategy.setter
    def current_strategy(self, strategy_or_name):
        """Make <strategy> the current strategy."""
        strategy = self.strategy_manager.get_strategy(strategy_or_name)
        self.strategy_manager.current_strategy = strategy

    def save_current_strategy(self, strategy_name):
        """Save the current strategy, giving it the name <strategy_name>"""
        self.strategy_manager.save_current_strategy(strategy_name)

    # RUN RELATED
    def join_run(self):
        """Join the run thread (if there is one)."""
        if hasattr(self, '_run_thread'):
            self._run_thread.join()

    @property
    def is_running(self):
        if hasattr(self, '_run_thread'):
            return self._run_thread.is_alive()
        else:
            return False

    def run(self, strategy=None, stage_name=None, 
            message_queue=multiprocessing.Queue(),
            async=False):
        '''
            Run the given strategy (defaults to current_strategy), or a stage 
        from that strategy.  Results are placed into the appropriate 
        trial's resources.
        Inputs:
            strategy: A Strategy object.  If not passed, 
                    session.current_strategy will be used.
            stage_name: If passed, only that stage will be run.
            message_queue: If passed, will be populated with run messages.
            async: If True, processing will run in a separate thread.  This 
                    thread can be joined with session.join_run()
        '''
        if strategy is None:
            strategy = self.current_strategy 
        self.process_manager.prepare_to_run_strategy(strategy, 
                stage_name=stage_name)

        self._run_thread = threading.Thread(
                target=self.process_manager.run_tasks,
                kwargs={'message_queue':message_queue})
        self._run_thread.start()
        if not async:
            self._run_thread.join()

    # PRIVATE FNS
    def _make_default_strategy(self):
        methods_used = {'detection_filter':'Infinite Impulse Response',
                        'detection':'Voltage Threshold',
                        'extraction_filter':'Copy Detection Filtering',
                        'extraction':'Spike Window',
                        'clustering':'K-means'}
        settings = {}
        for key, value in methods_used.items():
            possible_plugins = self.plugin_manager.get_plugins_by_stage(key)
            default_settings = None
            for name, plugin in possible_plugins.items():
                if name == value:
                    default_settings = plugin.get_parameter_defaults()
                    break
            if default_settings is not None:
                settings[key] = default_settings
            else:
                raise RuntimeError('Cannot find plugin with name %s.' % value)
        # add auxiliary stages
        auxiliary_stages = {}
        auxiliary_stages['Detection Spike Window'] = \
                {'pre_padding':5.0,
                 'post_padding':5.0,
                 'exclude_overlappers':False,
                 'min_num_channels':3,
                 'peak_drift':0.3}
        auxiliary_stages['Extraction Spike Window'] = \
                {'pre_padding':3.0,
                 'post_padding':6.0,
                 'exclude_overlappers':False,
                 'min_num_channels':3,
                 'peak_drift':0.3}
        auxiliary_stages['Resample after Detection Filter'] = \
                {'new_sampling_frequency':25000}
        auxiliary_stages['Resample after Extraction Filter'] = \
                {'new_sampling_frequency':25000}
        auxiliary_stages['Power Spectral Density (Pre-Filtering)'] =\
                {'frequency_resolution':5.0}
        auxiliary_stages['Power Spectral Density (Post-Detection-Filtering)'] =\
                {'frequency_resolution':5.0}
        auxiliary_stages['Power Spectral Density (Post-Extraction-Filtering)'] \
                = {'frequency_resolution':5.0}
        default_strategy = Strategy(methods_used=methods_used, 
                settings=settings, auxiliary_stages=auxiliary_stages)
        return default_strategy 

    def _files_opened(self, results):
        # Called after process_manager opens a file
        trials = []
        for result in results:
            if isinstance(result, Trial):
                trials.append(result)
            elif isinstance(result, Strategy):
                try:
                    self.strategy_manager.add_strategy(result)
                except: # may be a name conflict or something.
                    pass
                self.current_strategy = result
        self.trial_manager.add_trials(trials)


            





    
