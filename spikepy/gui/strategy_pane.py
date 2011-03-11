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


import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib import buttons

from spikepy.developer_tools.named_controls import NamedChoiceCtrl
from .utils import recursive_layout, strip_unicode
from spikepy.common.config_manager import config_manager as config
from spikepy.common import program_text as pt
from spikepy.common.strategy_manager import StrategyManager
from spikepy.common.strategy import Strategy
from spikepy.gui.save_strategy_dialog import SaveStrategyDialog
from spikepy.common import plugin_utils
from spikepy.gui import utils

stage_names = ['detection_filter', 'detection', 'extraction_filter', 
               'extraction', 'clustering']

def load_stages(control_panel_parent):
    return_dict = {}
    for stage_name in stage_names:
        methods = {}
        ms, mcs = plugin_utils.get_methods_for_stage(stage_name)
        for method in ms:
            methods[method.name] = {}
            methods[method.name]['control_panel'] =\
                    method.make_control_panel(control_panel_parent, 
                                              style=wx.BORDER_SUNKEN)
            methods[method.name]['control_panel'].Show(False)
            methods[method.name]['description'] = method.description
        return_dict[stage_name] = methods
    return return_dict


class StrategyPane(ScrolledPanel):
    def __init__(self, parent, **kwargs):
        ScrolledPanel.__init__(self, parent, **kwargs)
        self.SetBackgroundColour(wx.WHITE)
        
        self.stages = load_stages(self)

        self.strategy_chooser = NamedChoiceCtrl(self, name=pt.STRATEGY_NAME, 
                                                background_color=wx.WHITE)
        self.strategy_summary = StrategySummary(self, self.stages) 

        # ==== SETUP SIZER ====
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.EXPAND|wx.ALL
        border = config['gui']['strategy_pane']['border']
        sizer.Add(self.strategy_chooser,                proportion=0, 
                  flag=flag|wx.ALIGN_CENTER_HORIZONTAL,  border=border)

        sizer.Add(wx.StaticLine(self), proportion=0, 
                  flag=flag|wx.ALIGN_CENTER_HORIZONTAL, 
                                        border=border)

        sizer.Add(self.strategy_summary,  proportion=0, 
                                          flag=flag|wx.ALIGN_CENTER_HORIZONTAL, 
                                          border=border)

        self._setup_buttons()
        sizer.Add(self.button_sizer,        proportion=0,
                  flag=flag,            border=1)

        # method control panels
        for stage in self.stages.values():
            for method in stage.values():
                sizer.Add(method['control_panel'], 
                          flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 
                          border=8)

        self.SetSizer(sizer)
        self.do_layout()
            
        # other initialization
        self.strategy_summary.select_stage(stage_name=stage_names[0])
        self.strategy_summary.select_stage(stage_name=stage_names[0], 
                                           results=True)
        self._should_sync = True
        self.strategy_manager = StrategyManager()
        self.strategy_manager.load_all_strategies()
        self._temp_strategies = {}
        self._setup_subscriptions()
        self._setup_bindings()
                                
    # -- INITIALIZATION METHODS --
    def _setup_subscriptions(self):
        pub.subscribe(self._results_notebook_page_changed, 
                      topic='RESULTS_NOTEBOOK_PAGE_CHANGED')
        pub.subscribe(self._set_run_buttons_state,
                      topic='SET_RUN_BUTTONS_STATE')
        pub.subscribe(self._method_chosen, topic='METHOD_CHOSEN')
        pub.subscribe(self._stage_chosen, topic='STAGE_CHOSEN')
        pub.subscribe(self._enact_strategy, 
                      topic='ENACT_STRATEGY')

    def _setup_buttons(self):
        button_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.run_strategy_button = wx.Button(self, label=pt.RUN_STRATEGY)
        self.run_stage_button    = wx.Button(self, label=pt.RUN_STAGE)
        self.save_button         = wx.Button(self, label=pt.SAVE_STRATEGY)

        button_sizer.Add(self.run_strategy_button,   proportion=0, 
                         flag=wx.ALL,                 border=3)
        button_sizer.Add(self.save_button,           proportion=1, 
                         flag=wx.ALL,                 border=3)
        button_sizer.Add(self.run_stage_button,      proportion=0, 
                         flag=wx.ALL,                 border=3)
        self.button_sizer = button_sizer


    def _setup_bindings(self):
        self.Bind(wx.EVT_IDLE, self._sync)
        self.Bind(wx.EVT_BUTTON, self._save_button_pressed, self.save_button)
        self.Bind(wx.EVT_BUTTON, self._run_stage, self.run_stage_button)
        self.Bind(wx.EVT_BUTTON, self._run_strategy, self.run_strategy_button)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self._page_changed)
        self.Bind(wx.EVT_CHOICE, self._strategy_choice_made, 
                                 self.strategy_chooser.choice) 

    # -- PUBLIC METHODS --
    def set_run_buttons_state(self, states=[False, False]):
        self.run_stage_button.Enable(states[0])
        self.run_strategy_button.Enable(states[1])

    def get_current_strategy(self):
        methods_used = self.get_current_methods_used()
        settings     = self.get_current_settings()
        strategy = Strategy(methods_used=methods_used, settings=settings)
        strategy.name = self.strategy_manager.get_strategy_name(strategy)
        return strategy

    def get_current_methods_used(self):
        return self.strategy_summary.get_current_methods()

    def get_current_settings(self):
        methods_used = self.get_current_methods_used()
        settings     = {}
        for stage_name, method_name in methods_used.items():
            control_panel = self.stages[stage_name][method_name][
                                                    'control_panel']
            try:
                _settings = control_panel.get_parameters()
            except ValueError:
                _settings = None

            settings[stage_name] = _settings
        return settings

    def do_layout(self):
        self.SetupScrolling(scroll_x=False)
        self.Layout()

    @property
    def current_stage(self):
        return self.strategy_summary.current_stage


    # -- HELPER METHODS --
    def _update_strategy_choices(self):
        '''
        Adds any strategies in self._temp_strategies to the
            chooser.
        '''
        old_items = self.strategy_chooser.GetItems()
        new_items = self.strategy_manager.strategies.keys()
        new_items.extend(self._temp_strategies.keys())
        if old_items != new_items:
            self.strategy_chooser.SetItems(new_items)

    def _toggle_should_sync(self):
        self._should_sync = not self._should_sync 

    # -- MESSAGE HANDLERS --
    def _method_chosen(self, message):
        '''
        Show the appropriate stage's control panel.
        '''
        stage_name, method_name = message.data
        if stage_name == self.current_stage:
            for sn, stage in self.stages.items():
                for mn, method in stage.items():
                    should_show = (sn == stage_name and mn == method_name)
                    method['control_panel'].Show(should_show)
            self.do_layout()

    def _stage_chosen(self, message):
        stage_name = message.data
        method_name = self.get_current_methods_used()[stage_name]
        for sn, stage in self.stages.items():
            for mn, method in stage.items():
                should_show = (sn == stage_name and mn == method_name)
                method['control_panel'].Show(should_show)
        self.do_layout()

    def _enact_strategy(self, message=None, strategy=None):
        if message is not None:
            strategy = message.data
        for stage_name in stage_names:
            method_name = strategy.methods_used[stage_name]
            if method_name in self.stages[stage_name].keys():
                # set method
                self.strategy_summary.make_method_choice(stage_name, 
                                                         method_name)
                control_panel = self.stages[stage_name][method_name][
                                                'control_panel']
                settings = strategy.settings[stage_name]
                non_unicode_settings = strip_unicode(settings)
                # set settings
                control_panel.set_parameters(**non_unicode_settings)

    def _results_notebook_page_changed(self, message=None):
        self.strategy_summary.select_stage(stage_name=message.data, 
                                           results=True)

    def _set_run_buttons_state(self, message=None):
        run_state = message.data
        stage_name = self.current_stage

        run_stage_state    = run_state[stage_name]
        run_strategy_state = run_state['strategy']

        self.set_run_buttons_state(states=[run_stage_state, 
                                           run_strategy_state])

    # -- EVENT HANDLERS --
    def _run_strategy(self, event):
        # disable run buttons
        self.set_run_buttons_state()
        wx.Yield()

        strategy = self.get_current_strategy()
        pub.sendMessage("RUN_STRATEGY_ON_MARKED", 
                        data={'strategy':strategy})

    def _save_button_pressed(self, event=None):
        current_strategy = self.get_current_strategy()
        all_names = self.strategy_manager.strategies.keys()
        all_names.extend(self._temp_strategies.keys())
        dlg = SaveStrategyDialog(self, current_strategy.name,
                                 all_names)
        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg.get_strategy_name()
            del self._temp_strategies[current_strategy.name]
            current_strategy.name = new_name
            self.strategy_manager.add_strategy(current_strategy)
            self._update_strategy_choices()
        dlg.Destroy()

    def _run_stage(self, event):
        # disable run buttons
        self.set_run_buttons_state()
        wx.Yield()

        strategy = self.get_current_strategy()
        stage_name = self.current_stage
        pub.sendMessage("RUN_STAGE_ON_MARKED", 
                        data={'strategy':strategy, 
                              'stage_name':stage_name})

    def _sync(self, event=None): # handles IDLE events.
        '''
        Makes sure the strategy_chooser is syncronized with what the
            control panels are set to.
        '''
        if self._should_sync:
            self._should_sync = False
            wx.CallLater(config['gui']['strategy_pane']['wait_time'], 
                         self._toggle_should_sync)
            current_strategy = self.get_current_strategy()
            button_state = pt.CUSTOM_LC in current_strategy.name.lower()

            # -- add current_strategy to temp strategies if it is custom
            if button_state:
                self._temp_strategies[current_strategy.name] = current_strategy
                self._update_strategy_choices()

            # -- update strategy_chooser's selection if needed
            strategy_chooser = self.strategy_chooser
            if current_strategy.name != strategy_chooser.GetStringSelection():
                strategy_chooser.SetStringSelection(current_strategy.name)

            # -- ensure that the save button is in the correct state
            self.save_button.Enable(button_state)

            # -- set the run buttons state 
            data = (current_strategy.methods_used, current_strategy.settings)
            pub.sendMessage(topic='CALCULATE_RUN_BUTTONS_STATE', data=data)

    def _strategy_choice_made(self, event=None):
        'Update The Strategy Pane based on the choice made.'
        strategy_name = self.strategy_chooser.GetStringSelection()
        strategy = None
        if strategy_name in self._temp_strategies.keys():
            strategy = self._temp_strategies[strategy_name]
        if strategy_name in self.strategy_manager.strategies.keys():
            strategy = self.strategy_manager.get_strategy_by_name(strategy_name)
        if strategy is not None:
            self._enact_strategy(strategy=strategy)

    def _page_changed(self, event=None):
        if event is not None:
            old_page_num = event.GetOldSelection()
            new_page_num = event.GetSelection()
            self.strategy_summary.select_stage(new_page_num+1)
            ''' Decouple strategy pane from results notebook
            pub.sendMessage(topic='STRATEGY_CHOICEBOOK_PAGE_CHANGED', 
                            data=(new_page_num, old_page_num))
            '''

class StrategyStageChooser(wx.Panel):
    def __init__(self, parent, stage_name, stage_display_name, 
                 method_names, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.SetBackgroundColour(wx.WHITE)

        self.stage_name = stage_name
        self.method_names = method_names

        if stage_name == 'detection_filter':
            self.method_names.remove('Copy Detection Filtering')
        
        stage_icon = buttons.GenBitmapButton(self, wx.ID_ANY, 
                                     utils.get_bitmap_image('down_bar_arrow'),
                                     size=(30,30),
                                     style=wx.NO_BORDER)
        stage_text = buttons.GenButton(self, 
                                       wx.ID_ANY, "%s:" % stage_display_name, 
                                       size=(130,30),
                                       style=wx.NO_BORDER|wx.ALIGN_RIGHT)
        method_chooser = wx.Choice(self, choices=method_names)
        results_icon = buttons.GenBitmapButton(self, wx.ID_ANY, 
                                     utils.get_bitmap_image('right_arrow'),
                                     size=(30,30),
                                     style=wx.NO_BORDER)

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALL|wx.ALIGN_CENTER_VERTICAL
        sizer.Add(stage_icon,     flag=flag, border=3)
        sizer.Add(stage_text,     flag=flag|wx.ALIGN_RIGHT, border=3)
        sizer.Add(method_chooser, flag=flag|wx.ALIGN_LEFT, border=3,
                                   proportion=1)
        sizer.Add(results_icon,   flag=flag, border=3)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_click, self)
        self.Bind(wx.EVT_CHOICE, self.on_method_choice, method_chooser)
        self.Bind(wx.EVT_BUTTON, self.on_click, stage_icon)
        self.Bind(wx.EVT_BUTTON, self.on_click, results_icon)
        self.Bind(wx.EVT_BUTTON, self.on_click, stage_text)

        self.method_chooser = method_chooser
        self.stage_icon = stage_icon
        self.results_icon = results_icon

    def get_current_method(self):
        return self.method_chooser.GetStringSelection()

    def set_current_method(self, method_name):
        if method_name in self.method_names:
            self.method_chooser.SetStringSelection(method_name)
            pub.sendMessage(topic='METHOD_CHOSEN', 
                            data=(self.stage_name, method_name))
        else:
            raise RuntimeError("Method %s is not a valid choice for stage %s" % (method_name, self.stage_name))
        
    def on_method_choice(self, event):
        event.Skip()
        method_name = self.get_current_method()
        pub.sendMessage(topic='METHOD_CHOSEN', 
                        data=(self.stage_name, method_name))
        pub.sendMessage(topic='STAGE_CHOSEN', 
                        data=self.stage_name)
    
    def on_click(self, event):
        event.Skip()
        pub.sendMessage(topic='STAGE_CHOSEN', 
                        data=self.stage_name)

    def show_results_icon(self, state):
        self.results_icon.Show(state)

    def show_stage_icon(self, state):
        self.stage_icon.Show(state)

class StrategySummary(wx.Panel):
    def __init__(self, parent, stages, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.SetBackgroundColour(wx.WHITE)

        self.stage_choosers = []
        for stage_name in stage_names:
            methods_dict = stages[stage_name]
            stage_display_name = eval("pt.%s" % stage_name.upper())
            method_names = methods_dict.keys()
            self.stage_choosers.append(StrategyStageChooser(self, stage_name,
                                                        stage_display_name,
                                                        sorted(method_names)))
        
        pub.subscribe(self._update_methods, "UPDATE_STRATEGY_SUMMARY")
        pub.subscribe(self.select_stage, "STAGE_CHOSEN")

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        for stage_chooser in self.stage_choosers:
            sizer.Add(stage_chooser, flag=wx.EXPAND)

        self.SetMaxSize((config['gui']['strategy_pane']['min_width']-10,-1))
        self.SetSizerAndFit(sizer)

    def make_method_choice(self, stage_name, method_name):
        for stage_chooser in self.stage_choosers:
            if stage_chooser.stage_name == stage_name:
                stage_chooser.set_current_method(method_name)

    def get_current_methods(self):
        return_dict = {}
        for stage_chooser in self.stage_choosers:
            current_method = stage_chooser.get_current_method()
            return_dict[stage_chooser.stage_name] = current_method
        return return_dict

    def select_stage(self, message=None, stage_name=None, results=False):
        if stage_name is None:
            stage_name = message.data
        for stage_chooser in self.stage_choosers:
            if results: 
                show_fn = stage_chooser.show_results_icon
            else:
                show_fn = stage_chooser.show_stage_icon
            show_fn(stage_chooser.stage_name == stage_name)

        if not results:
            self._current_stage = stage_name

        self.Layout()

    @property
    def current_stage(self):
        return self._current_stage

    def _update_methods(self, message):
        return
        stage_num, method_string = message.data
        method_statictext = self.method_text_list[stage_num-1]
        method_statictext.SetLabel(method_string)

        self.Layout()

