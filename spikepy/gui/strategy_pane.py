

import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib import buttons

from spikepy.gui.named_controls import NamedChoiceCtrl 
import spikepy.common.program_text as pt
from spikepy.common import stages
from spikepy.gui import utils
from spikepy.common.config_manager import config_manager as config
from spikepy.gui.save_strategy_dialog import SaveStrategyDialog 
from spikepy.common.strategy_manager import Strategy
from spikepy.gui.control_panels import ControlPanel, OptionalControlPanel
from spikepy.gui.stage_ctrl import StageCtrl, AuxiliaryCtrl
from spikepy.common.path_utils import get_image_path


class StrategyPane(wx.Panel):
    def __init__(self, parent, plugin_manager, strategy_manager, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        
        self.save_button         = wx.Button(self, label=pt.SAVE_STRATEGY)
        self.strategy_chooser = NamedChoiceCtrl(self, name=pt.STRATEGY_NAME, 
                selection_callback=self._strategy_chooser_updated)
        choices = strategy_manager.managed_strategy_names 
        self.strategy_chooser.SetItems(choices)

        border = config['gui']['strategy_pane']['border']
        flag = wx.EXPAND|wx.ALL
        top_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        top_sizer.Add(self.strategy_chooser, proportion=1, 
                flag=flag|wx.ALIGN_CENTER_HORIZONTAL, border=border)
        top_sizer.Add(self.save_button, 
                flag=flag|wx.ALIGN_CENTER_HORIZONTAL, border=border)

        self.strategy_summary = StrategySummary(self, plugin_manager) 
        self.plugin_manager = plugin_manager 
        self.strategy_manager = strategy_manager 

        # ==== SETUP SIZER ====
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(top_sizer, proportion=0, 
                flag=flag|wx.ALIGN_CENTER_HORIZONTAL, border=border)
        sizer.Add(wx.StaticLine(self), proportion=0, 
                flag=flag|wx.ALIGN_CENTER_HORIZONTAL, border=border)
        sizer.Add(self.strategy_summary,  proportion=0, 
                flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP|
                        wx.ALIGN_CENTER_HORIZONTAL, border=border)

        self._setup_buttons()
        sizer.Add(self.button_sizer, proportion=0, 
                flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=border)
        sizer.Add(wx.StaticLine(self), proportion=0, 
                flag=flag|wx.ALIGN_CENTER_HORIZONTAL, border=border)

        self.control_panels_scroller = ScrolledPanel(self)
        sizer.Add(self.control_panels_scroller, proportion=1, flag=flag, 
                border=border)
        self._setup_control_panels(plugin_manager)

        self.SetSizer(sizer)
        self.do_layout()
            
        self._setup_subscriptions()
        self._setup_bindings()

        # other initialization
        pub.sendMessage('STAGE_CHOSEN', data=stages.stages[0])
        self.strategy_summary.select_stage(stage_name=stages.stages[0], 
                                           results=True)
        if choices:
            self._strategy_choice_made(selection=choices[0])
        self._set_run_buttons_state()

    def _setup_control_panels(self, plugin_manager):
        cp_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.control_panels = {}
        # method control panels
        for stage_name in stages.stages:
            self.control_panels[stage_name] = {}
            for plugin_name, plugin in plugin_manager.get_plugins_by_stage(
                    stage_name).items():
                control_panel = ControlPanel(self.control_panels_scroller, 
                        plugin,
                        valid_entry_callback=self._update_strategy)
                cp_sizer.Add(control_panel,
                          flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 
                          border=5)
                self.control_panels[stage_name][plugin_name] = control_panel

        # auxiliary control panels
        self.auxiliary_control_panels = {}
        for plugin_name, plugin in plugin_manager.get_plugins_by_stage(
                'auxiliary').items():
            control_panel = OptionalControlPanel(self.control_panels_scroller, 
                    plugin,
                    valid_entry_callback=self._update_strategy)

            cp_sizer.Add(control_panel, 
                    flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 
                    border=5)
            self.auxiliary_control_panels[plugin_name] = control_panel
        self.control_panels_scroller.SetSizer(cp_sizer)

    def _setup_buttons(self):
        button_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.run_strategy_button = wx.Button(self, label=pt.RUN_STRATEGY)
        self.run_stage_button    = wx.Button(self, label='run stage button')

        down_arrow = wx.Image(get_image_path('down_arrow.png'), 
                wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        da_image = wx.StaticBitmap(self, wx.ID_ANY, down_arrow, 
                size=(down_arrow.GetWidth(), down_arrow.GetHeight()))

        button_sizer.Add(da_image)
        button_sizer.Add(self.run_strategy_button, proportion=0, 
                         flag=wx.ALL, border=3)
        button_sizer.Add((6,6))
        button_sizer.Add(self.run_stage_button, proportion=1, 
                         flag=wx.ALL, border=3)
        self.button_sizer = button_sizer

    def _setup_subscriptions(self):
        pub.subscribe(self._set_run_buttons_state,
                      topic='SET_RUN_BUTTONS_STATE' )
        pub.subscribe(self._method_chosen, topic='METHOD_CHOSEN')
        pub.subscribe(self._stage_chosen, topic='STAGE_CHOSEN')
        pub.subscribe(self._strategy_added, topic='STRATEGY_ADDED')
        pub.subscribe(self._current_strategy_updated, 
                topic='CURRENT_STRATEGY_UPDATED')

    def _setup_bindings(self):
        self.Bind(wx.EVT_BUTTON, self._save_button_pressed, self.save_button)
        self.Bind(wx.EVT_BUTTON, self._run_stage, self.run_stage_button)
        self.Bind(wx.EVT_BUTTON, self._run_strategy, self.run_strategy_button)
        self.Bind(wx.EVT_CHOICE, self._strategy_choice_made, 
                                 self.strategy_chooser.choice) 

    def _set_run_buttons_state(self, message=None, states=[False, False]):
        if message is not None:
            states = message.data
        self.run_stage_button.Enable(states[0])
        self.run_strategy_button.Enable(states[1])

    def _strategy_added(self, message):
        strategy = message.data
        current_strategy_choices = self.strategy_chooser.GetItems()
        current_strategy_choices.append(strategy.name)
        current_selection = self.strategy_chooser.GetStringSelection()
        self.strategy_chooser.SetItems(sorted(current_strategy_choices))
        self.strategy_chooser.SetStringSelection(current_selection)
        self._strategy_chooser_updated(current_selection)

    def _current_strategy_updated(self, message=None, strategy=None):
        if message is not None:
            strategy = message.data
        self._push_strategy(strategy=strategy)

        managed_names = self.strategy_manager.managed_strategy_names
        if strategy.name not in managed_names:
            all_names = managed_names + [strategy.name]
        else:
            all_names = managed_names
        self.strategy_chooser.SetItems(all_names)

        self.strategy_chooser.SetStringSelection(strategy.name)
        self._strategy_chooser_updated(strategy.name)

    def get_current_methods_used(self):
        return self.strategy_summary.get_current_methods()

    def get_current_settings(self):
        methods_used = self.get_current_methods_used()
        settings     = {}
        for stage_name, method_name in methods_used.items():
            control_panel = self.control_panels[stage_name][method_name]
            settings[stage_name] = control_panel.pull()
        return settings

    def get_current_auxiliary_stages(self):
        auxiliary_stages = {}
        for cp in self.auxiliary_control_panels.values():
            if cp.active:
                auxiliary_stages[cp.plugin.name] = cp.pull()
        return auxiliary_stages

    def get_current_strategy(self):
        methods_used = self.get_current_methods_used()
        settings = self.get_current_settings()
        auxiliary_stages = self.get_current_auxiliary_stages()
        cs = Strategy(methods_used=methods_used,
                settings=settings,
                auxiliary_stages=auxiliary_stages)
        cs.name = self.strategy_manager.get_strategy_name(cs)
        return cs

    def _update_strategy(self, value=None):
        '''
            Called when a control_panel's value is changed and is valid.  Also
        called when the user changes the method of a stage.
        '''
        strategy = self.get_current_strategy()
        pub.sendMessage('SET_CURRENT_STRATEGY', data=strategy)

    def do_layout(self):
        self.control_panels_scroller.SetupScrolling(scrollToTop=False)
        self.control_panels_scroller.Layout()
        self.Layout()

    @property
    def current_stage(self):
        return self.strategy_summary.current_stage

    # -- MESSAGE HANDLERS --
    def _method_chosen(self, message=None, stage_name=None, method_name=None):
        ''' Show the appropriate stage's control panel. '''
        if stage_name is None and method_name is None:
            stage_name, method_name = message.data
        self._set_method(stage_name=stage_name, method_name=method_name)
        self._update_strategy()

    def _set_method(self, stage_name=None, method_name=None):
        for sn, s_dict in self.control_panels.items():
            for mn, control_panel in s_dict.items():
                should_show = (sn == stage_name and mn == method_name and
                        self.current_stage == sn)
                control_panel.Show(should_show)
        self.do_layout()

    def _stage_chosen(self, message):
        stage_name = message.data
        if stage_name == 'auxiliary':
            for stage in self.control_panels.values():
                for panel in stage.values():
                    panel.Show(False)
            for panel in self.auxiliary_control_panels.values():
                panel.Show(panel.plugin.runs_with_stage == stage_name)
            self.run_stage_button.SetLabel(pt.RUN_AUXILIARY_PLUGINS)
            self.do_layout()
        else:
            for panel in self.auxiliary_control_panels.values():
                panel.Show(panel.plugin.runs_with_stage == stage_name)
            method_name = self.get_current_methods_used()[stage_name]
            self._set_method(stage_name=stage_name, method_name=method_name)
            self.run_stage_button.SetLabel(pt.RUN_STAGE % 
                    stages.get_stage_display_name(stage_name))
            self.do_layout()

    def _push_strategy(self, strategy):
        for stage_name in stages.stages:
            method_name = strategy.methods_used[stage_name]
            self.strategy_summary.make_method_choice(stage_name, method_name)
            control_panel = self.control_panels[stage_name][method_name]
            control_panel.push(strategy.settings[stage_name])
            if self.current_stage == stage_name:
                self._set_method(stage_name=stage_name, 
                        method_name=method_name)
            auxiliary_plugins_used = strategy.auxiliary_stages.keys()
            for cp in self.auxiliary_control_panels.values():
                if cp.plugin.name in auxiliary_plugins_used:
                    cp.active = True
                    cp.push(strategy.auxiliary_stages[cp.plugin.name])
                else:
                    cp.active = False

    # -- EVENT HANDLERS --
    def _run_strategy(self, event):
        event.Skip()
        # disable run buttons
        self._set_run_buttons_state()
        wx.Yield()

        pub.sendMessage("RUN_STRATEGY", 
                        data={'strategy':self.get_current_strategy()})

    def _save_button_pressed(self, event=None):
        event.Skip()
        cs = self.get_current_strategy()
        old_name = self.strategy_manager.get_strategy_name(cs)
        all_names = self.strategy_manager.managed_strategy_names
        dlg = SaveStrategyDialog(self, old_name, all_names)
        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg.get_strategy_name()
            self.strategy_manager.add_strategy(cs, name=new_name)
            self.strategy_manager.save_strategies()
            pub.sendMessage('SET_CURRENT_STRATEGY', data=cs)
        dlg.Destroy()

    def _run_stage(self, event):
        # disable run buttons
        event.Skip()
        self._set_run_buttons_state(states=[False,False])
        wx.Yield()

        stage_name = self.current_stage
        pub.sendMessage("RUN_STAGE", 
                        data={'strategy':self.get_current_strategy(),
                              'stage_name':stage_name})

    def _strategy_chooser_updated(self, new_value):
        """
            Called whenever the value of the strategy_chooser is changed by
        the user, called manually by other parts of the code too.
        """
        status = (pt.CUSTOM_LC in new_value)
        self.save_button.Enable(status)

    def _strategy_choice_made(self, event=None, selection=None):
        """
            Called when the user chooses a strategy from the chooser.
        """
        if event is not None:
            event.Skip()
        if event is None and selection is not None:
            strategy_name = selection
            self.strategy_chooser.SetStringSelection(selection)
        else:
            strategy_name = self.strategy_chooser.selection

        if pt.CUSTOM_LC not in strategy_name.lower():
            strategy = self.strategy_manager.get_strategy(strategy_name)
            self._push_strategy(strategy=strategy)
            pub.sendMessage('SET_CURRENT_STRATEGY', data=strategy)

class StrategySummary(wx.Panel):
    '''
        The StrategySummary shows what methods are chosen for each of the
    processing stages.  Users can select a stage by clicking on them.
    '''
    def __init__(self, parent, plugin_manager, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.stage_choosers = []
        for stage_name in stages.stages:
            stage_display_name = stages.get_stage_display_name(stage_name)
            method_names = plugin_manager.get_plugins_by_stage(
                    stage_name).keys()
            self.stage_choosers.append(StageCtrl(self, stage_name,
                                                        stage_display_name,
                                                        sorted(method_names)))
        self.stage_choosers.append(AuxiliaryCtrl(self, 'auxiliary',
                stages.get_stage_display_name('auxiliary')))
        
        # issued when user chooses a stage to adjust its parameters, not when
        # user clicks on results tab.
        pub.subscribe(self.select_stage, "STAGE_CHOSEN")

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        for stage_chooser in self.stage_choosers:
            sizer.Add(stage_chooser, flag=wx.EXPAND)

        self.SetSizer(sizer)

        pub.subscribe(self._results_notebook_page_changed, 
                      topic='RESULTS_NOTEBOOK_PAGE_CHANGED')

        self._current_stage = stages.stages[0]

    def _results_notebook_page_changed(self, message=None):
        self.select_stage(stage_name=message.data, results=True)

    def make_method_choice(self, stage_name, method_name):
        for stage_chooser in self.stage_choosers:
            if stage_chooser.stage_name == stage_name:
                stage_chooser.set_current_method(method_name)

    def get_current_methods(self):
        return_dict = {}
        for stage_chooser in self.stage_choosers:
            if not isinstance(stage_chooser, AuxiliaryCtrl):
                current_method = stage_chooser.get_current_method()
                return_dict[stage_chooser.stage_name] = current_method
        return return_dict

    def select_stage(self, message=None, stage_name=None, results=False):
        '''
            Show either the results icon or the stage icon for a 
        specific stage.
        '''
        if stage_name is None:
            stage_name = message.data
        for stage_chooser in self.stage_choosers:
            if results: 
                show_fn = stage_chooser.show_results_icon
            else:
                show_fn = stage_chooser.show_stage_icon
                stage_chooser.show_left_bar(False)
            show_fn(stage_chooser.stage_name == stage_name)

        if not results:
            if stage_name != 'auxiliary':
                chooser_index = stages.stages.index(stage_name)
                for stage_chooser in self.stage_choosers:
                    if stage_chooser.stage_name != 'auxiliary':
                        index = stages.stages.index(stage_chooser.stage_name)
                        stage_chooser.show_left_bar(index > chooser_index)
                    else:
                        stage_chooser.show_left_bar(True)

        if not results:
            self._current_stage = stage_name

        self.wiggle()
        self.Layout()

    def wiggle(self):
        '''
        Resize main frame up one pixel in each direction then back down... so
        as to fix drawing bugs.
        '''
        if wx.Platform == '__WXMSW__':
            s = self.GetSize()
            self.SetSize((s[0]+1, s[1]+1))
            self.SendSizeEvent()
            self.SetSize(s)
            self.SendSizeEvent()
        else:
            pass

    @property
    def current_stage(self):
        return self._current_stage

