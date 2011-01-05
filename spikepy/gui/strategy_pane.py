
import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.buttons import GenButton

from .named_controls import NamedChoiceCtrl
from .utils import recursive_layout
from ..stages import filtering, detection, extraction, clustering
from .look_and_feel_settings import lfs
from . import program_text as pt
from .strategy_manager import StrategyManager

        
class RunManager(object):
    def __init__(self):
        pass

    def _recalc_run_state(self, message=None):
        self._should_calculate_stage_run_state = True


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
                                 pt.DETECTION_FILTER+" "+pt.SETTINGS)
        stage_choicebook.AddPage(detection_panel, 
                                 pt.DETECTION+" "+pt.SETTINGS)
        stage_choicebook.AddPage(extraction_filter_panel, 
                                 pt.EXTRACTION_FILTER+" "+pt.SETTINGS)
        stage_choicebook.AddPage(extraction_panel, 
                                 pt.EXTRACTION+" "+pt.SETTINGS)
        stage_choicebook.AddPage(clustering_panel, 
                                 pt.CLUSTERING+" "+pt.SETTINGS)
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
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self._page_changed)
        self.strategy_pane.Bind(wx.EVT_IDLE, self._sync)
        self.strategy_pane.Bind(wx.EVT_CHOICE, self._strategy_choice_made, 
                                self.strategy_chooser.choice) 
                                
        pub.subscribe(self._results_notebook_page_changing, 
                      topic='RESULTS_NOTEBOOK_PAGE_CHANGING')
        pub.subscribe(self._set_run_buttons_state, 
                      topic='SET_RUN_BUTTONS_STATE')
        pub.subscribe(self.save_all_strategies, topic='SAVE_ALL_STRATEGIES')
        pub.subscribe(self._set_strategy, topic='SET_STRATEGY')
        pub.subscribe(self._recalc_run_state, topic='FILE_OPENED')
        pub.subscribe(self._recalc_run_state, topic='TRIAL_FILTERED')
        pub.subscribe(self._recalc_run_state, topic='TRIAL_SPIKE_DETECTED')
        pub.subscribe(self._recalc_run_state, topic='TRIAL_FEATURE_EXTRACTED')
        pub.subscribe(self._recalc_run_state, topic='TRIAL_CLUSTERED')
        pub.subscribe(self._recalc_run_state, topic='TRIAL_MARKS_CHANGED')
        self.stages = [detection_filter_panel,
                       detection_panel,
                       extraction_filter_panel,
                       extraction_panel,
                       clustering_panel]
        self.strategy_manager = StrategyManager(self)

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


    def get_current_methods_used(self)
        methods_used = {}
        for stage in self.strategy_pane.stages:
            method_chosen = stage._method_name_chosen
            stage_name = stage.stage_name
            methods_used[stage_name] = method_chosen
        return methods_used


    def _toggle_should_sync(self):
        self._should_sync = not self._should_sync 

    def _update_strategy_choices(self):
        old_items = self.strategy_chooser.GetItems()
        if old_items != self.strategy_names:
            self.strategy_chooser.SetItems(self.strategy_names)


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
    
    def _set_run_buttons_state(self, message=None):
        run_all_states, run_marked_states = message.data
        for stage in self.stages:
            stage_name = stage.stage_name
            stage.run_all_button.Enable(run_all_states[stage_name])
            stage.run_marked_button.Enable(run_marked_states[stage_name])
            
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
        
        self.Bind(wx.EVT_CHOICE, self._method_choice_made,
                  self.method_chooser.choice)
        self.Bind(wx.EVT_BUTTON, self._on_run_all, self.run_all_button)
        self.Bind(wx.EVT_BUTTON, self._on_run_marked, self.run_marked_button)
        
        pub.subscribe(self._set_stage_parameters, topic='SET_PARAMETERS')
        self._method_choice_made(method_name=self.method_names[0])

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
        self._method_choice_made(method_name=method_name)

    def _method_choice_made(self, event=None, method_name=None):
        self.methods[self._method_name_chosen]['control_panel'].Show(False)

        if method_name is not None:
            self._method_name_chosen = method_name
            self.method_chooser.SetStringSelection(method_name)
        else:
            self._method_name_chosen = self.method_chooser.GetStringSelection()

        self.methods[self._method_name_chosen]['control_panel'].Show(True)
        self.Layout()
        pub.sendMessage(topic="UPDATE_STRATEGY_SUMMARY", 
                        data=(self.stage_num, self._method_name_chosen))

    def _on_run_marked(self, event=None):
        self._run(run_all=False)

    def _on_run_all(self, event=None):
        self._run(run_all=True)

    def _run(self, run_all=True):
        control_panel = self.methods[self._method_name_chosen]['control_panel']
        settings = control_panel.get_parameters()
        wx.Yield() # about to let scipy hog cpu, so process all wx events.
        data = {'stage_name' :self.stage_name,
                'method_name':self._method_name_chosen,
                'settings'   :settings}
        if run_all:
            pub.sendMessage(topic='RUN_ALL', data=data)
        else:
            pub.sendMessage(topic='RUN_MARKED', data=data)

