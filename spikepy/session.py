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
from spikepy.common.trial_manager import TrialManager
from spikepy.common.process_manager import ProcessManager
from spikepy.common.config_manager import ConfigManager
from spikepy.common.strategy_manager import StrategyManager

class Session(object):
    def __init__(self):
        self.trial_manager = TrialManager()
        self.process_manager = ProcessManager()
        self.config_manager = ConfigManager()
        self.strategy_manager = StrategyManager()

    # --- OPEN FILE(S) ---
    def open_file(self, fullpath):
        """Open file located at fullpath."""
        self.process_manager.open_file(fullpath, 
                created_trials_callback=self._trials_created)

    def open_files(self, fullpaths):
        """Open the files located at fullpaths"""
        self.process_manager.open_files(fullpaths, 
                created_trials_callback=self._trials_created)

    def _trials_created(self, trials, proposed_names):
        # Called after process_manager opens a file
        self.trial_manager.add_trials(trials, proposed_names)

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

    def get_trial_with_name(self, name):
        """
        Find the trial with display_name=<name> and return it.
        Raises RuntimeError if trial cannot be found.
        """
        self.trial_manager.get_trial_with_name(name)

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




    
