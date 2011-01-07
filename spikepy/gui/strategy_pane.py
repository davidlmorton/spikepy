
import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.buttons import GenButton

from .named_controls import NamedChoiceCtrl
from .utils import recursive_layout, strip_unicode
from ..stages import filtering, detection, extraction, clustering
from .look_and_feel_settings import lfs
from spikepy.common import program_text as pt
from spikepy.common.strategy_manager import StrategyManager
from spikepy.common.strategy import Strategy
from spikepy.gui.save_strategy_dialog import SaveStrategyDialog


def add_settings(stage_name):
    return "%s %s" % (stage_name, pt.SETTINGS)


class StrategyPane(ScrolledPanel):
    def __init__(self, parent, **kwargs):
        ScrolledPanel.__init__(self, parent, **kwargs)
        
        self.strategy_chooser = NamedChoiceCtrl(self, name=pt.STRATEGY_NAME)
        self.strategy_summary = StrategySummary(self)
        self.save_button = wx.Button(self, label=pt.SAVE_STRATEGY)
        line = wx.StaticLine(self)
        stage_choicebook = wx.Choicebook(self, wx.ID_ANY)

        # ==== PANELS ====
        detection_filter_panel = StagePanel(stage_choicebook, 
                                            stage_num=1,
                                            display_name=pt.DETECTION_FILTER,
                                            stage_name='detection_filter',
                                            module=filtering)
        detection_panel = StagePanel(stage_choicebook, 
                                     stage_num=2,
                                     display_name=pt.DETECTION,
                                     stage_name='detection',
                                     module=detection)
        extraction_filter_panel = StagePanel(stage_choicebook,
                                             stage_num=3,
                                             display_name=pt.EXTRACTION_FILTER,
                                             stage_name='extraction_filter',
                                             module=filtering)
        extraction_panel = StagePanel(stage_choicebook,
                                      stage_num=4,
                                      display_name=pt.EXTRACTION,
                                      stage_name='extraction',
                                      module=extraction)
        clustering_panel = StagePanel(stage_choicebook, 
                                      stage_num=5,
                                      display_name=pt.CLUSTERING,
                                      stage_name='clustering',
                                      module=clustering)

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
        border = lfs.STRATEGY_PANE_BORDER
        sizer.Add(self.strategy_chooser, proportion=0, 
                                          flag=flag|wx.ALIGN_CENTER_HORIZONTAL, 
                                          border=border)
        sizer.Add(self.strategy_summary,  proportion=0, 
                                          flag=flag|wx.ALIGN_CENTER_HORIZONTAL, 
                                          border=border)
        sizer.Add(self.save_button, proportion=0, flag=wx.ALL|wx.ALIGN_RIGHT, 
                                          border=border)
        
        sizer.Add(line,  proportion=0, 
                                          flag=flag|wx.ALIGN_CENTER_HORIZONTAL, 
                                          border=border)
        sizer.Add(stage_choicebook,  proportion=1, flag=flag, border=border)
        self.strategy_summary.select_stage(1)
        self.SetSizer(sizer)
        self.do_layout()

        self._should_sync = True
                                
        pub.subscribe(self._results_notebook_page_changing, 
                      topic='RESULTS_NOTEBOOK_PAGE_CHANGING')

        self.stage_panels = [detection_filter_panel,
                             detection_panel,
                             extraction_filter_panel,
                             extraction_panel,
                             clustering_panel]

        self.strategy_manager = StrategyManager()
        self._temp_strategies = {}

        self.Bind(wx.EVT_IDLE, self._sync)
        self.Bind(wx.EVT_BUTTON, self._save_button_pressed, self.save_button)
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
            wx.CallLater(lfs.STRATEGY_WAIT_TIME, self._toggle_should_sync)
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
            # set method
            stage_panel.method_choice_made(method_name=method_name)
            control_panel = stage_panel.methods[method_name]['control_panel'] 
            stage_settings = strategy.settings[stage_name]
            non_unicode_stage_settings = strip_unicode(stage_settings)
            # set parameters
            control_panel.set_parameters(**non_unicode_stage_settings)

    def _results_notebook_page_changing(self, message=None):
        old_page_num, new_page_num = message.data
        if new_page_num < 5: # don't try to change if changing to summary
            self.stage_choicebook.SetSelection(new_page_num)

    def _page_changed(self, event=None):
        if event is not None:
            new_page_num = event.GetSelection()
            self.strategy_summary.select_stage(new_page_num+1)
            pub.sendMessage(topic='STRATEGY_CHOICEBOOK_PAGE_CHANGED', 
                            data=new_page_num)

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
        rsizer_border = lfs.STRATEGY_SUMMARY_BORDER

        for method_text in self.method_text_list:
            rsizer.Add(method_text, proportion=0, flag=rsizer_flag, 
                       border=rsizer_border)
        
        flag = wx.ALL|wx.ALIGN_RIGHT
        border = lfs.STRATEGY_SUMMARY_BORDER
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
        minwidth = minwidth + 2*lfs.STRATEGY_SUMMARY_BORDER
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
                               module=None, 
                               **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.stage_num = stage_num
        self.display_name = display_name
        self.stage_name = stage_name
        stage_module = module

        # --- METHODS ---
        self.methods = {}
        self.method_names = stage_module.method_names
        for method_module, method_name in zip(stage_module.method_modules, 
                                              self.method_names):
            self.methods[method_name] = {}
            self.methods[method_name]['control_panel'] = \
                    method_module.ControlPanel(self, style=wx.BORDER_SUNKEN)
            self.methods[method_name]['control_panel'].Show(False)
            self.methods[method_name]['description'] = method_module.description
        self._method_name_chosen = self.method_names[0]

        self.method_chooser = NamedChoiceCtrl(self, name=pt.METHOD+":",
                                 choices=self.method_names)

        # --- RUN BUTTONS ---
        button_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.run_all_button    = wx.Button(self, label=pt.RUN_ALL)
        self.run_marked_button = wx.Button(self, label=pt.RUN_MARKED)
        button_sizer.Add(self.run_marked_button,  proportion=0, 
                      flag=wx.ALL,                 border=3)
        button_sizer.Add(wx.StaticText(self),     proportion=1)
        button_sizer.Add(self.run_all_button,     proportion=0, 
                      flag=wx.ALL,  border=3)

        # --- SIZER ---
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        ea_flag = wx.EXPAND|wx.ALL
        sizer.Add(self.method_chooser,          proportion=0, 
                      flag=ea_flag,              border=3)
        for method in self.methods.values():
            sizer.Add(method['control_panel'],  proportion=0,
                      flag=ea_flag,              border=6)
        sizer.Add(button_sizer,                 proportion=0,
                      flag=ea_flag,               border=1)
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_CHOICE, self.method_choice_made,
                  self.method_chooser.choice)
        self.Bind(wx.EVT_BUTTON, self._on_run_all, self.run_all_button)
        self.Bind(wx.EVT_BUTTON, self._on_run_marked, self.run_marked_button)
        
        pub.subscribe(self._set_stage_parameters, topic='SET_PARAMETERS')
        pub.subscribe(self._enable_run_buttons, topic='ABLE_TO_RUN_AGAIN')
        self.method_choice_made(method_name=self.method_names[0])

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

    def _on_run_marked(self, event=None):
        self._run(run_all=False)

    def _on_run_all(self, event=None):
        self._run(run_all=True)

    def _run(self, run_all=True):
        self.run_all_button.Disable()
        self.run_marked_button.Disable()
        control_panel = self.methods[self.method_name_chosen]['control_panel']
        settings = control_panel.get_parameters()
        wx.Yield() # about to let scipy hog cpu, so process all wx events.
        data = {'stage_name' :self.stage_name,
                'method_name':self.method_name_chosen,
                'settings'   :settings}
        if run_all:
            pub.sendMessage(topic='RUN_ALL', data=data)
        else:
            pub.sendMessage(topic='RUN_MARKED', data=data)

    def _enable_run_buttons(self, message=None):
        self.run_all_button.Enable()
        self.run_marked_button.Enable()

