import json

import wx

from . import program_text as pt
from .utils import HashableDict, make_dict_hashable
from .look_and_feel_settings import lfs


class StrategyManager(object):
    def __init__(self, strategy_pane):
        self.strategy_pane = strategy_pane
        # dictionaries are named by their values.
        self.methods        = {}
        self.methods_names  = {}
        self.settings       = {}
        self.settings_names = {}
        self.load_archived_strategies()

        self._should_sync = True
        self.strategy_pane.Bind(wx.EVT_IDLE, self._sync)

    @property
    def strategy_names(self):
        return sorted(self.settings_names.values())

    def load_archived_strategies(self, 
            strategy_archive_file='strategies_archive.txt'):
        with open(strategy_archive_file) as infile:
            saved_strategies = json.load(infile)
            del saved_strategies['__comment']
            make_dict_hashable(saved_strategies)
        
        self._add_strategy(saved_strategies)

    def _sync(self, event=None):
        if self._should_sync:
            self._should_sync = False
            wx.CallLater(lfs.STRATEGY_WAIT_TIME, self._toggle_should_sync)
            current_strategy      = self.get_current_strategy()
            current_strategy_name = current_strategy.keys()[0]

            if not self.settings.has_key(current_strategy_name):
                self._add_strategy(current_strategy)
            self.strategy_pane.strategy_chooser.SetStringSelection(
                    current_strategy_name)

            if 'custom' in current_strategy_name.lower():
                self.strategy_pane.save_button.Enable()
            else:
                self.strategy_pane.save_button.Enable(False)

    def _add_strategy(self, strategy):
        for key, value in strategy.items():
            method_name = key.split('(')[0]
            method_dict = value['methods_used']
            self.methods[method_name]       = method_dict
            self.methods_names[method_dict] = method_name

            settings_name = key
            settings_dict = value['settings'] 
            self.settings[settings_name]       = settings_dict
            self.settings_names[settings_dict] = settings_name
        self._update_strategy_choices()

    def _update_strategy_choices(self):
        chooser = self.strategy_pane.strategy_chooser
        chooser.SetItems(self.strategy_names)

    def _toggle_should_sync(self):
        self._should_sync = not self._should_sync 

    def get_strategy_name(self, methods_used, settings):
        if self.methods_names.has_key(methods_used):
            strategy_main_name = self.methods_names[methods_used]
            if self.settings_names.has_key(settings):
                return self.settings_names[settings]
            else:
                strategy_sub_name = 'custom'
        else:
            strategy_main_name = 'Custom'
            strategy_sub_name  = 'custom'

        strategy_name = strategy_main_name + '(%s)' % strategy_sub_name 
        return strategy_name 

    def get_current_strategy(self):
        methods_used = HashableDict()
        settings     = HashableDict()
        for stage in self.strategy_pane.stages:
            method_chosen = stage._method_name_chosen
            control_panel = stage.methods[method_chosen]['control_panel']
            hashable_settings = HashableDict(control_panel.get_parameters())

            stage_name = stage.stage_name.lower().replace(' ', '_')
            methods_used[stage_name] = method_chosen
            settings[stage_name]     = hashable_settings

        strategy_name = self.get_strategy_name(methods_used, settings)
        return_dict = {}
        return_dict[strategy_name] = {'methods_used':methods_used, 
                                      'settings':settings}
        return return_dict
        
