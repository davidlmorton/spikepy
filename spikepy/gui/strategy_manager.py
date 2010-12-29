import json

import wx
from wx.lib.pubsub import Publisher as pub

from . import program_text as pt
from .utils import strip_unicode
from .look_and_feel_settings import lfs
from .save_strategy_dialog import SaveStrategyDialog
from .strategy_utils import (make_strategy, make_methods_set_name, 
                             make_settings_name, make_strategy_name)

STRATEGIES_ARCHIVE_FILE= 'strategies_archive.txt'

class StrategyManager(object):
    def __init__(self, strategy_pane):
        self.strategy_pane    = strategy_pane
        self.strategy_chooser = self.strategy_pane.strategy_chooser
        self.save_button = self.strategy_pane.save_button
        # dictionaries are named by their values.
        self.methods        = {}
        self.settings       = {}
        self.load_archived_strategies()

        self._should_sync = True
        self.strategy_pane.Bind(wx.EVT_IDLE, self._sync)
        self.strategy_pane.Bind(wx.EVT_CHOICE, self._strategy_choice_made, 
                                self.strategy_chooser.choice) 
        pub.subscribe(self.save_all_strategies, topic='SAVE_ALL_STRATEGIES')
        pub.subscribe(self._set_strategy, topic='SET_STRATEGY')
        pub.subscribe(self._recalc_run_state, topic='FILE_OPENED')
        pub.subscribe(self._recalc_run_state, topic='TRIAL_FILTERED')
        pub.subscribe(self._recalc_run_state, topic='TRIAL_SPIKE_DETECTED')
        pub.subscribe(self._recalc_run_state, topic='TRIAL_FEATURE_EXTRACTED')
        pub.subscribe(self._recalc_run_state, topic='TRIAL_CLUSTERED')
        pub.subscribe(self._recalc_run_state, topic='TRIAL_MARKS_CHANGED')
        self.strategy_pane.Bind(wx.EVT_BUTTON, self.save_button_pressed, 
                                self.save_button)
        self._last_current_strategy = None
        self._should_calculate_stage_run_state = False

    def _recalc_run_state(self, message=None):
        self._should_calculate_stage_run_state = True

    @property
    def strategy_names(self):
        return sorted(self.settings.keys())

    def load_archived_strategies(self, 
            strategy_archive_file=STRATEGIES_ARCHIVE_FILE):
        with open(strategy_archive_file) as infile:
            saved_strategies = json.load(infile)
            del saved_strategies['__comment']
        self._add_strategy(saved_strategies)

    def save_all_strategies(self, message=None):
        strategy_list = []
        for strategy_name in self.strategy_names:
            methods_set_name = make_methods_set_name(strategy_name)
            methods_dict  = self.methods[methods_set_name]
            settings_dict = self.settings[strategy_name]
            this_strategy_dict = make_strategy(strategy_name, 
                                               methods_dict, 
                                               settings_dict)
            strategy_list.append(this_strategy_dict)
        self.save_strategies(strategy_list)
        
    def save_strategies(self, strategy_list, filename=STRATEGIES_ARCHIVE_FILE):
        all_strategies_dict = {}
        for strategy in strategy_list:
            all_strategies_dict.update(strategy)

        comment = "DO NOT EDIT THIS DOCUMENT (BAD THINGS WILL HAPPEN)" 
        all_strategies_dict['__comment'] = comment
        with open(filename, 'w') as ofile:
            json.dump(all_strategies_dict, ofile, indent=4)
        
    def _strategy_choice_made(self, event=None):
        'Update The Strategy Pane based on the choice made.'
        strategy_name = self.strategy_chooser.GetStringSelection()
        methods_set_name = make_methods_set_name(strategy_name)
        methods_used = self.methods[methods_set_name]
        settings     = self.settings[strategy_name]
        self._set_strategy_pane(methods_used, settings)

    def _set_strategy(self, message):
        methods_used, settings = message.data
        self._set_strategy_pane(methods_used, settings)

    def _set_strategy_pane(self, methods_used, settings):
        for stage in self.strategy_pane.stages:
            stage_name = stage.stage_name
            method_name = methods_used[stage_name]        
            if method_name is not None:
                stage._method_choice_made(method_name=method_name)
            else:
                continue

            control_panel = stage.methods[method_name]['control_panel'] 
            stage_settings = settings[stage_name]
            if stage_settings is not None:
                non_unicode_stage_settings = strip_unicode(stage_settings)
                control_panel.set_parameters(**non_unicode_stage_settings)

    def _sync(self, event=None):
        if self._should_sync:
            self._should_sync = False
            wx.CallLater(lfs.STRATEGY_WAIT_TIME, self._toggle_should_sync)
            current_strategy      = self.get_current_strategy()
            current_strategy_name = current_strategy.keys()[0]

            if (not self.settings.has_key(current_strategy_name) or
                pt.CUSTOM_LC in current_strategy_name.lower()):
                self._add_strategy(current_strategy)
            strategy_chooser = self.strategy_chooser
            if current_strategy_name != strategy_chooser.GetStringSelection():
                strategy_chooser.SetStringSelection(current_strategy_name)

            button_state = pt.CUSTOM_LC in current_strategy_name.lower()
            self.strategy_pane.save_button.Enable(button_state)
            if (current_strategy != self._last_current_strategy or
                    self._should_calculate_stage_run_state):
                name = current_strategy_name
                methods_used = current_strategy[name]['methods_used']
                settings     = current_strategy[name]['settings']
                pub.sendMessage(topic='CALCULATE_RUN_BUTTONS_STATE', 
                                data=(methods_used, settings))
                self._should_calculate_stage_run_state = False
            self._last_current_strategy = current_strategy

    def save_button_pressed(self, event=None):
        current_strategy = self.get_current_strategy() 
        current_strategy_name = current_strategy.keys()[0]
        dlg = SaveStrategyDialog(self.strategy_pane, current_strategy_name,
                                 self.strategy_names,
                                 title=pt.SAVE_STRATEGY_DIALOG_TITLE,
                                 style=wx.DEFAULT_DIALOG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg.get_strategy_name()
            dlg.Destroy()
            if new_name in self.strategy_names:
                confirm_dlg = wx.MessageDialog(self.strategy_pane,
                        new_name + pt.ALREADY_EXISTS_LINE,
                        caption=pt.CONFIRM_OVERWRITE,
                        style=wx.YES_NO|wx.ICON_WARNING)
                if confirm_dlg.ShowModal() == wx.ID_NO:
                    confirm_dlg.Destroy()
                    self.save_button_pressed()
                    return
                confirm_dlg.Destroy()

            self._remove_strategy(current_strategy)
            renamed_strategy = self._get_renamed_strategy(current_strategy, 
                                                          new_name)
            self._add_strategy(renamed_strategy)

    def _get_renamed_strategy(self, strategy, new_name):
        new_strategy = {}
        old_name = strategy.keys()[0]
        methods_used = strategy[old_name]['methods_used']
        settings     = strategy[old_name]['settings']
        new_strategy[new_name] = {'methods_used':methods_used,
                                  'settings':settings}
        return new_strategy
        
    def _add_strategy(self, strategy):
        for strategy_name, value in strategy.items():
            method_name = make_methods_set_name(strategy_name)
            method_dict = value['methods_used']
            self.methods[method_name]    = method_dict

            settings_name = strategy_name
            settings_dict = value['settings'] 
            self.settings[settings_name] = settings_dict
        self._update_strategy_choices()

    def _remove_strategy(self, strategy):
        strategy_name = strategy.keys()[0]
        method_name   = make_methods_set_name(strategy_name)
        settings_name = strategy_name
        del self.methods[method_name]
        del self.settings[settings_name]

        self._update_strategy_choices()
        
    def _update_strategy_choices(self):
        old_items = self.strategy_chooser.GetItems()
        if old_items != self.strategy_names:
            self.strategy_chooser.SetItems(self.strategy_names)

    def _toggle_should_sync(self):
        self._should_sync = not self._should_sync 

    def get_strategy_name(self, methods_used, settings):
        for strategy_name, settings_dict in self.settings.items():
            if settings == settings_dict:
                # potential match
                name = strategy_name
                method_set_name = make_methods_set_name(name)
                if self.methods[method_set_name] == methods_used:
                    return name

        for method_set_name, methods_dict in self.methods.items():
            if methods_dict == methods_used:
                return method_set_name + '(' + pt.CUSTOM_LC + ')'

        return pt.CUSTOM_SC + '(' + pt.CUSTOM_LC + ')'

    def get_current_methods_used(self):
        methods_used = {}
        for stage in self.strategy_pane.stages:
            method_chosen = stage._method_name_chosen
            stage_name = stage.stage_name
            methods_used[stage_name] = method_chosen
        return methods_used

    def get_current_settings(self):
        settings     = {}
        for stage in self.strategy_pane.stages:
            method_chosen = stage._method_name_chosen
            control_panel = stage.methods[method_chosen]['control_panel']
            try:
                _settings = control_panel.get_parameters()
            except ValueError:
                _settings = None

            stage_name = stage.stage_name
            settings[stage_name] = _settings
        return settings

    def get_current_strategy(self):
        methods_used = self.get_current_methods_used()
        settings      = self.get_current_settings()
        strategy_name = self.get_strategy_name(methods_used, settings)
        return make_strategy(strategy_name, methods_used, settings)


