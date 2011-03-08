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
from wx.lib.buttons import GenButton

from spikepy.developer_tools.named_controls import NamedChoiceCtrl
from .utils import recursive_layout, strip_unicode
from spikepy.common.config_manager import config_manager as config
from spikepy.common import program_text as pt
from spikepy.common.strategy_manager import StrategyManager
from spikepy.common.strategy import Strategy
from spikepy.gui.save_strategy_dialog import SaveStrategyDialog
from spikepy.common import plugin_utils


def add_settings(stage_name):
    return "%s %s" % (stage_name, pt.SETTINGS)


class StrategyPane(ScrolledPanel):
    def __init__(self, parent, **kwargs):
        ScrolledPanel.__init__(self, parent, **kwargs)
        
        self.strategy_chooser = NamedChoiceCtrl(self, name=pt.STRATEGY_NAME)
        self.strategy_summary = StrategySummary(self)
        stage_choicebook = wx.Choicebook(self, wx.ID_ANY)

        # ==== PANELS ====
        detection_filter_panel = DetectionFilterStagePanel(stage_choicebook, 
                                            stage_num=1,
                                            display_name=pt.DETECTION_FILTER,
                                            stage_name='detection_filter')
        detection_panel = StagePanel(stage_choicebook, 
                                     stage_num=2,
                                     display_name=pt.DETECTION,
                                     stage_name='detection')
        extraction_filter_panel = StagePanel(stage_choicebook,
                                             stage_num=3,
                                             display_name=pt.EXTRACTION_FILTER,
                                             stage_name='extraction_filter')
        extraction_panel = StagePanel(stage_choicebook,
                                      stage_num=4,
                                      display_name=pt.EXTRACTION,
                                      stage_name='extraction')
        clustering_panel = StagePanel(stage_choicebook, 
                                      stage_num=5,
                                      display_name=pt.CLUSTERING,
                                      stage_name='clustering')

        # ==== CHOICEBOOK PAGES ====
        stage_choicebook.AddPage(detection_filter_panel, 
                                 add_settings(pt.DETECTION_FILTER))
        stage_choicebook.AddPage(detection_panel, 
                                 add_settings(pt.DETECTION))
        stage_choicebook.AddPage(extraction_filter_panel, 
                                 add_settings(pt.EXTRACTION_FILTER))
        stage_choicebook.AddPage(extraction_panel, 
                                 add_settings(pt.EXTRACTION))
        stage_choicebook.AddPage(clustering_panel, 
                                 add_settings(pt.CLUSTERING))
        self.stage_choicebook = stage_choicebook 
        
        # ==== SETUP SIZER ====
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.EXPAND|wx.ALL
        border = config['gui']['strategy_pane']['border']
        sizer.Add(self.strategy_chooser,                proportion=0, 
                  flag=flag|wx.ALIGN_CENTER_HORIZONTAL,  border=border)
        sizer.Add(self.strategy_summary,  proportion=0, 
                                          flag=flag|wx.ALIGN_CENTER_HORIZONTAL, 
                                          border=border)
        # ++ buttons ++
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
        # -- buttons --

        sizer.Add(button_sizer,        proportion=0,
                  flag=flag,            border=1)
        sizer.Add(wx.StaticLine(self), proportion=0, 
                  flag=flag|wx.ALIGN_CENTER_HORIZONTAL, 
                                        border=border)
        sizer.Add(stage_choicebook,    proportion=1, 
                  flag=flag,            border=border)

        self.strategy_summary.select_stage(1)
        self.SetSizer(sizer)
        self.do_layout()

        self._should_sync = True
                                
        ''' Decouple results notebook and strategy pane
        pub.subscribe(self._results_notebook_page_changed, 
                      topic='RESULTS_NOTEBOOK_PAGE_CHANGED')
        '''
        pub.subscribe(self._set_run_buttons_state,
                      topic='SET_RUN_BUTTONS_STATE')
        pub.subscribe(self._enact_strategy, 
                      topic='ENACT_STRATEGY')

        self.stage_panels = [detection_filter_panel,
                             detection_panel,
                             extraction_filter_panel,
                             extraction_panel,
                             clustering_panel]

        self.strategy_manager = StrategyManager()
        self.strategy_manager.load_all_strategies()
        self._temp_strategies = {}

        self.Bind(wx.EVT_IDLE, self._sync)
        self.Bind(wx.EVT_BUTTON, self._save_button_pressed, self.save_button)
        self.Bind(wx.EVT_BUTTON, self._run_stage, self.run_stage_button)
        self.Bind(wx.EVT_BUTTON, self._run_strategy, self.run_strategy_button)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self._page_changed)
        self.Bind(wx.EVT_CHOICE, self._strategy_choice_made, 
                                 self.strategy_chooser.choice) 

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

    # --- SYNC ---
    def _toggle_should_sync(self):
        self._should_sync = not self._should_sync 

    def _sync(self, event=None):
        '''
        Makes sure the strategy_chooser is syncronized with what the
            control panels are set to.
        '''
        if self._should_sync:
            self._should_sync = False
            wx.CallLater(config['gui']['strategy_pane']['wait_time'], 
                         self._toggle_should_sync)
            current_strategy      = self.get_current_strategy()
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

    def _update_strategy_choices(self):
        old_items = self.strategy_chooser.GetItems()
        new_items = self.strategy_manager.strategies.keys()
        new_items.extend(self._temp_strategies.keys())
        if old_items != new_items:
            self.strategy_chooser.SetItems(new_items)

    # --- GET CURRENT STRATEGY AND HELPER FNs ---
    def get_current_strategy(self):
        methods_used = self.get_current_methods_used()
        settings     = self.get_current_settings()
        strategy = Strategy(methods_used=methods_used, settings=settings)
        strategy.name = self.strategy_manager.get_strategy_name(strategy)
        return strategy

    def get_current_methods_used(self):
        methods_used = {}
        for stage_panel in self.stage_panels:
            method_chosen = stage_panel.method_name_chosen
            stage_name = stage_panel.stage_name
            methods_used[stage_name] = method_chosen
        return methods_used

    def get_current_settings(self):
        settings     = {}
        for stage_panel in self.stage_panels:
            method_name_chosen = stage_panel.method_name_chosen
            control_panel = stage_panel.methods[
                                method_name_chosen]['control_panel']
            try:
                _settings = control_panel.get_parameters()
            except ValueError:
                _settings = None

            stage_name = stage_panel.stage_name
            settings[stage_name] = _settings
        return settings

    # -- STRATEGY CHOOSER --
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

    def _enact_strategy(self, message=None, strategy=None):
        if message is not None:
            strategy = message.data
        for stage_panel in self.stage_panels:
            stage_name = stage_panel.stage_name
            method_name = strategy.methods_used[stage_name]        
            if method_name in stage_panel.methods.keys():
                # set method
                stage_panel.method_choice_made(method_name=method_name)
                control_panel = stage_panel.methods[method_name][
                                                    'control_panel'] 
                stage_settings = strategy.settings[stage_name]
                non_unicode_stage_settings = strip_unicode(stage_settings)
                # set parameters
                control_panel.set_parameters(**non_unicode_stage_settings)

    def _results_notebook_page_changed(self, message=None):
        old_page_num, new_page_num = message.data
        if new_page_num < 5: # don't try to change if changing to summary
            self.stage_choicebook.ChangeSelection(new_page_num)

    def _page_changed(self, event=None):
        if event is not None:
            old_page_num = event.GetOldSelection()
            new_page_num = event.GetSelection()
            self.strategy_summary.select_stage(new_page_num+1)
            ''' Decouple strategy pane from results notebook
            pub.sendMessage(topic='STRATEGY_CHOICEBOOK_PAGE_CHANGED', 
                            data=(new_page_num, old_page_num))
            '''

    def do_layout(self):
        self.SetupScrolling()
        self.Layout()

    def get_stage_from_display_name(self, display_name):
        '''
        Return the stage with the given display_name
        '''
        for stage in self.stages:
            if stage.display_name == display_name:
                return stage
        return None

    @property
    def current_stage(self):
        return self.stage_choicebook.GetCurrentPage()

    def _run_stage(self, event):
        # disable run buttons
        self.set_run_buttons_state()
        wx.Yield()

        strategy = self.get_current_strategy()
        stage_name = self.current_stage.stage_name
        pub.sendMessage("RUN_STAGE_ON_MARKED", 
                        data={'strategy':strategy, 
                              'stage_name':stage_name})

    def _run_strategy(self, event):
        # disable run buttons
        self.set_run_buttons_state()
        wx.Yield()

        strategy = self.get_current_strategy()
        pub.sendMessage("RUN_STRATEGY_ON_MARKED", 
                        data={'strategy':strategy})

    def set_run_buttons_state(self, states=[False, False]):
        self.run_stage_button.Enable(states[0])
        self.run_strategy_button.Enable(states[1])

    def _set_run_buttons_state(self, message=None):
        run_state = message.data
        stage_name = self.current_stage.stage_name

        run_stage_state    = run_state[stage_name]
        run_strategy_state = run_state['strategy']

        self.set_run_buttons_state(states=[run_stage_state, 
                                           run_strategy_state])


class StrategySummary(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        
        pub.subscribe(self._update_methods, "UPDATE_STRATEGY_SUMMARY")
        s = []
        stages = [pt.DETECTION_FILTER, pt.DETECTION, pt.EXTRACTION_FILTER, 
                  pt.EXTRACTION, pt.CLUSTERING]
        self.method_text_list = []
        for stage in stages:
            s.append(wx.StaticText(self, label=stage+':',
                               style=wx.ALIGN_RIGHT))
            self.method_text_list.append(wx.StaticText(self,label='', 
                               style=wx.ALIGN_LEFT))

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        lsizer = wx.BoxSizer(orient=wx.VERTICAL)
        rsizer = wx.BoxSizer(orient=wx.VERTICAL)
        rsizer_flag = wx.ALL|wx.ALIGN_LEFT
        rsizer_border = config['gui']['strategy_pane']['summary_border']

        for method_text in self.method_text_list:
            rsizer.Add(method_text, proportion=0, flag=rsizer_flag, 
                       border=rsizer_border)
        
        flag = wx.ALL|wx.ALIGN_RIGHT
        border = config['gui']['strategy_pane']['summary_border']
        for stage_text in s:
            lsizer.Add(stage_text, proportion=0, flag=flag, 
                                  border=border)
        sizer.Add(lsizer, proportion=0)
        sizer.Add(rsizer, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)
        self.stage_text_list = s
        lsizer.SetMinSize(self._get_lsizer_minsize())
        self._selected_stage = 1
        self.lsizer = lsizer
        self.rsizer = rsizer

    def select_stage(self, stage_num):
        old_stage_text = self.stage_text_list[self._selected_stage-1]
        old_method_text = self.method_text_list[self._selected_stage-1]
        stage_font = old_stage_text.GetFont()
        stage_font.SetWeight(wx.FONTWEIGHT_NORMAL)
        old_stage_text.SetFont(stage_font)
        old_method_text.SetFont(stage_font)

        new_stage_text = self.stage_text_list[stage_num-1]
        new_method_text = self.method_text_list[stage_num-1]
        stage_font = new_stage_text.GetFont()
        stage_font.SetWeight(wx.FONTWEIGHT_BOLD)
        new_stage_text.SetFont(stage_font)
        new_method_text.SetFont(stage_font)
        self._selected_stage = stage_num
        self.Layout()

    def _get_lsizer_minsize(self):
        stage_text_widths = []
        for stage_text in self.stage_text_list:
            font = stage_text.GetFont()
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            stage_text.SetFont(font)
            stage_text_widths.append(stage_text.GetSize()[0])
            font.SetWeight(wx.FONTWEIGHT_NORMAL)
            stage_text.SetFont(font)
        minwidth = max(stage_text_widths)
        minwidth = minwidth + 2*config['gui']['strategy_pane']['summary_border']
        minsize = (minwidth, 1)
        return minsize 

    def _update_methods(self, message):
        stage_num, method_string = message.data
        method_statictext = self.method_text_list[stage_num-1]
        method_statictext.SetLabel(method_string)

        self.Layout()


class StagePanel(wx.Panel):
    def __init__(self, parent, stage_num=None, 
                               display_name=None,
                               stage_name=None, 
                               **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.stage_num = stage_num
        self.display_name = display_name
        self.stage_name = stage_name

        # --- METHODS ---
        self.methods = self.load_methods()

        self.method_names = sorted(self.methods.keys())
        if self.method_names:
            self._method_name_chosen = self.method_names[0]

        self.method_chooser = NamedChoiceCtrl(self, name=pt.METHOD+":",
                                 choices=self.method_names)

        # --- SIZER ---
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        ea_flag = wx.EXPAND|wx.ALL
        sizer.Add(self.method_chooser,          proportion=0, 
                      flag=ea_flag,              border=3)
        for method in self.methods.values():
            sizer.Add(method['control_panel'],  proportion=0,
                      flag=ea_flag,              border=6)
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_CHOICE, self.method_choice_made,
                  self.method_chooser.choice)
        
        pub.subscribe(self._set_stage_parameters, topic='SET_PARAMETERS')
        self.method_choice_made(method_name=self.method_names[0])

    def load_methods(self):
        methods = {}
        ms, mcs = plugin_utils.get_methods_for_stage(self.stage_name)
        for method in ms:
            methods[method.name] = {}
            methods[method.name]['control_panel'] =\
                    method.make_control_panel(self, style=wx.BORDER_SUNKEN)
            methods[method.name]['control_panel'].Show(False)
            methods[method.name]['description'] = method.description
        return methods

    def _set_stage_parameters(self, message=None):
        kwargs = message.data
        stage_name = kwargs['stage_name']
        if stage_name != self.stage_name:
            message = "Message sent to incorrect panel.\n"
            message += "This panel is named: %s\n" % self.stage_name
            message += "Intended panel is named: %s" % stage_name
            raise RuntimeError(message)
            return # not the right stage_panel
        method_name = kwargs['method_name']
        parameters = {}
        for key, value in kwargs.items():
            if (key != 'stage_name' and 
                key != 'method_name'):
                parameters[key] = value
        self.methods[method_name]['control_panel'].set_parameters(**parameters)
        self.method_choice_made(method_name=method_name)

    @property
    def method_name_chosen(self):
        return self._method_name_chosen 

    def method_choice_made(self, event=None, method_name=None):
        self.methods[self.method_name_chosen]['control_panel'].Show(False)

        if method_name is not None:
            self._method_name_chosen = method_name
            self.method_chooser.SetStringSelection(method_name)
        else:
            self._method_name_chosen = self.method_chooser.GetStringSelection()

        self.methods[self.method_name_chosen]['control_panel'].Show(True)
        self.Layout()
        pub.sendMessage(topic="UPDATE_STRATEGY_SUMMARY", 
                        data=(self.stage_num, self.method_name_chosen))

    def run(self):
        control_panel = self.methods[self.method_name_chosen]['control_panel']
        settings = control_panel.get_parameters()
        wx.Yield() # about to let scipy hog cpu, so process all wx events.
        data = {'stage_name' :self.stage_name,
                'method_name':self.method_name_chosen,
                'settings'   :settings}

        pub.sendMessage(topic='RUN_MARKED', data=data)

class DetectionFilterStagePanel(StagePanel):
    def load_methods(self):
        methods = StagePanel.load_methods(self)
        if 'Copy Detection Filtering' in  methods.keys():
            del methods['Copy Detection Filtering']
        return methods
    
