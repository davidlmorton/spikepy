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
import multiprocessing

from spikepy.common.trial_manager import TrialManager
from spikepy.common.process_manager import ProcessManager
from spikepy.common.config_manager import ConfigManager
from spikepy.common.plugin_manager import PluginManager
from spikepy.common.strategy_manager import StrategyManager, Strategy

class Session(object):
    def __init__(self):
        self.config_manager   = ConfigManager()
        self.trial_manager    = TrialManager(self.config_manager)
        self.plugin_manager   = PluginManager(self.config_manager, 
                app_name='spikepy')
        self.strategy_manager = StrategyManager(self.config_manager)
        self.strategy_manager.current_strategy = self._make_default_strategy()
        self.process_manager  = ProcessManager(self.config_manager, 
                self.trial_manager, self.plugin_manager)

        # register callback for open_files
        self.process_manager.open_files.add_callback(self._trials_created,
                takes_target_results=True)

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
        #auxiliary_stages['Resample after Detection Filter'] = \
        #        {'new_sampling_freq':25000}
        #auxiliary_stages['Resample after Extraction Filter'] = \
        #        {'new_sampling_freq':25000}
        default_strategy = Strategy(methods_used=methods_used, 
                settings=settings, auxiliary_stages=auxiliary_stages)
        return default_strategy 

    # --- OPEN FILE(S) ---
    def open_file(self, fullpath):
        """Open file located at fullpath."""
        return self.process_manager.open_file(fullpath)

    def open_files(self, fullpaths):
        """Open the files located at fullpaths"""
        return self.process_manager.open_files(fullpaths)

    def _trials_created(self, trials):
        # Called after process_manager opens a file
        self.trial_manager.add_trials(trials)

    # --- TRIAL ---
    def rename_trial(self, old_name, proposed_name):
        """Find trial named <old_name> and rename it to <proposed_name>."""
        self.trial_manager.rename_trial(old_name, proposed_name)

    def remove_trial_with_name(self, name):
        """Remove the trial with display_name=<name>."""
        self.trial_manager.remove_trial_with_name(name)

    def remove_marked_trials(self):
        """Remove all currently marked trials."""
        self.trial_manager.remove_marked_trials()

    def mark_trial(self, name, status=True):
        """Mark trial with display_name=<name> according to <status>."""
        self.trial_manager.mark_trial(name, status=status)

    def mark_all_trials(self, status=True):
        """Mark all trials according to <status>"""
        self.trial_manager.mark_all_trials(status=status)

    @property
    def trials(self):
        '''Return all currently marked and unmarked trials.'''
        return self.trial_manager.trials

    @property
    def marked_trials(self):
        '''Return all currently marked trials.'''
        return self.trial_manager.marked_trials
        
    def get_trial_with_name(self, name):
        """
        Find the trial with display_name=<name> and return it.
        Raises RuntimeError if trial cannot be found.
        """
        return self.trial_manager.get_trial_with_name(name)

    # --- STRATEGY ---
    def select_strategy(self, strategy_name):
        """Make the strategy with name <strategy_name>, the current strategy."""
        self.strategy_manager.select_strategy(strategy_name)

    @property
    def current_strategy(self):
        """The currently selected strategy."""
        return self.strategy_manager.current_strategy

    @current_strategy.setter
    def current_strategy(self, strategy):
        """Make <strategy> the current strategy."""
        self.strategy_manager.current_strategy = strategy

    def save_current_strategy(self, strategy_name):
        """Save the current strategy, giving it the name <strategy_name>"""
        self.strategy_manager.save_current_strategy(strategy_name)

    def run(self, strategy=None, stage_name=None, 
            message_queue=multiprocessing.Queue()):
        '''
            Run the given strategy (defaults to current_strategy), or a stage 
        from that strategy.  Results are placed into the appropriate 
        trial's resources.
        '''
        if strategy is None:
            strategy = self.current_strategy 
        self.process_manager.prepare_to_run_strategy(strategy, 
                stage_name=stage_name)
        self.process_manager.run_tasks(message_queue=message_queue)






    
