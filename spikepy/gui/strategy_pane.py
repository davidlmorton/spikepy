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

from spikepy.utils.string_formatting import start_case
from spikepy.gui.valid_controls import make_control
from spikepy.gui.named_controls import NamedChoiceCtrl 
import spikepy.common.program_text as pt
from spikepy.common import stages
from spikepy.gui import utils
from spikepy.common.config_manager import config_manager as config
from spikepy.gui.save_strategy_dialog import SaveStrategyDialog 
from spikepy.common.strategy_manager import Strategy

class ControlPanel(wx.Panel):
    '''
        A ControlPanel allows the user to set the parameters of a single
    method.
    '''
    def __init__(self, parent, plugin, valid_entry_callback=None, 
            background_color=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.plugin = plugin
        self.valid_entry_callback = valid_entry_callback
        self.background_color = background_color 

        if background_color is not None:
            self.SetBackgroundColour(background_color)

        self.build_controls()
        self.layout_ui()
        self.push(plugin.get_parameter_defaults())

    def layout_ui(self):
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        title = wx.StaticText(self, label=self.plugin.name)
        f = title.GetFont()
        f.SetWeight(wx.BOLD)
        title.SetFont(f)
        sizer.Add(title, flag=wx.ALIGN_LEFT|wx.ALL, border=5)
        for ctrl_name in sorted(self.ctrls.keys()):
            sizer.Add(self.ctrls[ctrl_name], flag=wx.EXPAND|wx.ALIGN_RIGHT)
            self.ctrls[ctrl_name].register_valid_entry_callback(
                    self.valid_entry_callback)
        self.SetSizer(sizer)

    def build_controls(self):
        self.ctrls = {}
        for pname, valid_type in self.plugin.get_parameter_attributes().items():
            display_name = start_case(pname)
            self.ctrls[pname] = make_control(self, display_name, valid_type,
                    background_color=self.background_color)

    def pull(self):
        return_dict = {}
        for name, ctrl in self.ctrls.items():
            return_dict[name] = ctrl.GetValue()
        return return_dict

    def push(self, value_dict):
        for name, value in value_dict.items():
            self.ctrls[name].SetValue(value)

class OptionalControlPanel(ControlPanel):
    '''
        A ControlPanel that is optional and has a checkbox to turn
    on/off.
    '''
    def __init__(self, parent, plugin, valid_entry_callback=None, 
            background_color=None, 
            optional=True, 
            **kwargs):
        self.optional = optional
        ControlPanel.__init__(self, parent, plugin, valid_entry_callback,
                background_color, **kwargs)

    def layout_ui(self):
        active_checkbox = wx.CheckBox(self, label='')
        active_checkbox.Enable(self.optional)
        active_checkbox.Show(self.optional)
        active_checkbox.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self._activate, active_checkbox)

        title = wx.StaticText(self, label=self.plugin.name)
        f = title.GetFont()
        f.SetWeight(wx.BOLD)
        title.SetFont(f)
        title_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        title_sizer.Add(active_checkbox, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, 
                border=5)
        title_sizer.Add(title, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(title_sizer, flag=wx.ALIGN_LEFT)
        for ctrl_name in sorted(self.ctrls.keys()):
            sizer.Add(self.ctrls[ctrl_name], flag=wx.EXPAND|wx.ALIGN_RIGHT)
            self.ctrls[ctrl_name].register_valid_entry_callback(
                    self.valid_entry_callback)
        sizer.Add(wx.StaticLine(self), flag=wx.EXPAND|wx.ALL, border=3)
        self.SetSizer(sizer)
        self.active_checkbox = active_checkbox
        self.title = title

    def _activate(self, event):
        event.Skip()
        for ctrl in self.ctrls.values():
            ctrl.Enable(self.active)
        self.title.Enable(self.active)
        if self.valid_entry_callback is not None:
            self.valid_entry_callback(self.active)

    @property
    def active(self):
        return self.active_checkbox.GetValue()

    @active.setter
    def active(self, value):
        self.active_checkbox.SetValue(value)
        for ctrl in self.ctrls.values():
            ctrl.Enable(self.active)
        self.title.Enable(self.active)
        if self.valid_entry_callback is not None:
            self.valid_entry_callback(self.active)

    def pull(self):
        if self.active:
            return_dict = {}
            for name, ctrl in self.ctrls.items():
                return_dict[name] = ctrl.GetValue()
            return return_dict
        else:
            return None

    def push(self, value_dict=None):
        if value_dict is None:
            self.active = False
        else:
            self.active = True
            for name, value in value_dict.items():
                self.ctrls[name].SetValue(value)


class StrategyPane(wx.Panel):
    def __init__(self, parent, plugin_manager, strategy_manager, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.SetBackgroundColour(wx.WHITE)
        
        self.strategy_chooser = NamedChoiceCtrl(self, name=pt.STRATEGY_NAME, 
                background_color=wx.WHITE, 
                selection_callback=self._strategy_chooser_updated)
        self.strategy_chooser.SetItems(strategy_manager.managed_strategy_names)

        self.strategy_summary = StrategySummary(self, plugin_manager) 
        self.plugin_manager = plugin_manager 
        self.strategy_manager = strategy_manager 

        # ==== SETUP SIZER ====
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.EXPAND|wx.ALL
        border = config['gui']['strategy_pane']['border']
        sizer.Add(self.strategy_chooser, proportion=0, 
                flag=flag|wx.ALIGN_CENTER_HORIZONTAL, border=border)
        sizer.Add(wx.StaticLine(self), proportion=0, 
                flag=flag|wx.ALIGN_CENTER_HORIZONTAL, border=border)
        sizer.Add(self.strategy_summary,  proportion=0, 
                flag=flag|wx.ALIGN_CENTER_HORIZONTAL, border=border)

        self._setup_buttons()
        sizer.Add(self.button_sizer, proportion=0, flag=flag, border=1)

        self.control_panels_scroller = ScrolledPanel(self)
        sizer.Add(self.control_panels_scroller, proportion=1, flag=flag, 
                border=border)

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
                          border=8)
                self.control_panels[stage_name][plugin_name] = control_panel

        # auxiliary control panels
        self.auxiliary_control_panels = {}
        for plugin_name, plugin in plugin_manager.get_plugins_by_stage(
                'auxiliary').items():
            control_panel = OptionalControlPanel(self.control_panels_scroller, 
                    plugin,
                    valid_entry_callback=self._update_strategy,
                    optional=plugin.optional_in_gui)

            cp_sizer.Add(control_panel, 
                    flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 
                    border=8)
            self.auxiliary_control_panels[plugin_name] = control_panel
        self.control_panels_scroller.SetSizer(cp_sizer)

        self.SetSizer(sizer)
        self.do_layout()
            
        self._setup_subscriptions()
        self._setup_bindings()

        self._push_strategy(strategy=strategy_manager.current_strategy)

        # other initialization
        pub.sendMessage('STAGE_CHOSEN', data=stages.stages[0])
        self.strategy_summary.select_stage(stage_name=stages.stages[0], 
                                           results=True)
        self._set_run_buttons_state()

                                
    # -- INITIALIZATION METHODS --
    def _setup_buttons(self):
        button_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.run_strategy_button = wx.Button(self, label=pt.RUN_STRATEGY)
        self.run_stage_button    = wx.Button(self, label=pt.RUN_STAGE)
        self.save_button         = wx.Button(self, label=pt.SAVE_STRATEGY)

        button_sizer.Add(self.run_strategy_button, proportion=0, 
                         flag=wx.ALL, border=3)
        button_sizer.Add(self.save_button, proportion=1, 
                         flag=wx.ALL, border=3)
        button_sizer.Add(self.run_stage_button, proportion=0, 
                         flag=wx.ALL, border=3)
        self.button_sizer = button_sizer

    def _setup_subscriptions(self):
        pub.subscribe(self._set_run_buttons_state,
                      topic='SET_RUN_BUTTONS_STATE' )
        pub.subscribe(self._method_chosen, topic='METHOD_CHOSEN')
        pub.subscribe(self._stage_chosen, topic='STAGE_CHOSEN')

    def _setup_bindings(self):
        self.Bind(wx.EVT_BUTTON, self._save_button_pressed, self.save_button)
        self.Bind(wx.EVT_BUTTON, self._run_stage, self.run_stage_button)
        self.Bind(wx.EVT_BUTTON, self._run_strategy, self.run_strategy_button)
        self.Bind(wx.EVT_CHOICE, self._strategy_choice_made, 
                                 self.strategy_chooser.choice) 

    # -- PUBLIC METHODS --
    def _set_run_buttons_state(self, message=None, states=[False, False]):
        if message is not None:
            states = message.data
        self.run_stage_button.Enable(states[0])
        self.run_strategy_button.Enable(states[1])

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
        cs = self.get_current_strategy()

        if cs.name not in self.strategy_chooser.GetItems():
            managed_names = self.strategy_manager.managed_strategy_names
            all_names = managed_names + [cs.name]
            self.strategy_chooser.SetItems(all_names)
        self.strategy_chooser.selection = cs.name

        self.strategy_manager.current_strategy = cs

    def do_layout(self):
        self.control_panels_scroller.SetupScrolling()
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
        for sn, s_dict in self.control_panels.items():
            for mn, control_panel in s_dict.items():
                should_show = (sn == stage_name and mn == method_name and
                        self.current_stage == sn)
                control_panel.Show(should_show)
        self._update_strategy()
        self.do_layout()

    def _stage_chosen(self, message):
        stage_name = message.data
        if stage_name == 'auxiliary':
            for stage in self.control_panels.values():
                for panel in stage.values():
                    panel.Show(False)
            for panel in self.auxiliary_control_panels.values():
                panel.Show(True)
            self.do_layout()
        else:
            for panel in self.auxiliary_control_panels.values():
                panel.Show(False)
            method_name = self.get_current_methods_used()[stage_name]
            self._method_chosen(stage_name=stage_name, method_name=method_name)

    def _push_strategy(self, strategy):
        for stage_name in stages.stages:
            method_name = strategy.methods_used[stage_name]
            self.strategy_summary.make_method_choice(stage_name, method_name)
            control_panel = self.control_panels[stage_name][method_name]
            control_panel.push(strategy.settings[stage_name])
            if self.current_stage == stage_name:
                self._method_chosen(stage_name=stage_name, 
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
        cs = self.strategy_manager.current_strategy
        old_name = self.strategy_manager.get_strategy_name(cs)
        all_names = self.strategy_manager.managed_strategy_names
        dlg = SaveStrategyDialog(self, old_name, all_names)
        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg.get_strategy_name()
            self.strategy_manager.add_strategy(cs, name=new_name)
            self.strategy_manager.current_strategy = \
                    self.strategy_manager.get_strategy(new_name)
            self.strategy_chooser.SetItems(all_names + [new_name])
            self.strategy_chooser.selection = new_name
            self.strategy_manager.save_strategies()
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
            Called whenever the value of the strategy_chooser is changed, both
        by the user and programmatically.
        """
        status = (pt.CUSTOM_LC in new_value)
        self.save_button.Enable(status)

    def _strategy_choice_made(self, event=None):
        """
            Called when the user chooses a new strategy from the chooser."""
        event.Skip()
        strategy_name = self.strategy_chooser.selection
        if pt.CUSTOM_LC not in strategy_name.lower():
            strategy = self.strategy_manager.get_strategy(strategy_name)
            self.strategy_manager.current_strategy = strategy
            self._push_strategy(strategy=strategy)
            self.strategy_chooser.SetItems(
                    self.strategy_manager.managed_strategy_names)
            self.strategy_chooser.selection = strategy_name

class StrategyStageChooser(wx.Panel):
    '''
        These are the elements in a StrategySummary that the user can
    select to choose a stage.  They also have a wxChoice control to allow
    the user to select the method for this stage.
    '''
    def __init__(self, parent, stage_name, stage_display_name, 
                 method_names, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.SetBackgroundColour(wx.WHITE)

        self.stage_name = stage_name
        self.method_names = method_names

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

class StrategyAuxiliaryChooser(wx.Panel):
    '''
        These are the elements in a StrategySummary that the user can
    select to choose a stage.
    '''
    def __init__(self, parent, stage_name, stage_display_name, 
                 **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.SetBackgroundColour(wx.WHITE)

        self.stage_name = stage_name

        stage_icon = buttons.GenBitmapButton(self, wx.ID_ANY, 
                                     utils.get_bitmap_image('down_bar_arrow'),
                                     size=(30,30),
                                     style=wx.NO_BORDER)
        stage_text = buttons.GenButton(self, 
                                       wx.ID_ANY, "%s" % stage_display_name, 
                                       size=(130,30),
                                       style=wx.NO_BORDER|wx.ALIGN_RIGHT)

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALL|wx.ALIGN_CENTER_VERTICAL
        sizer.Add(stage_icon,     flag=flag, border=3)
        sizer.Add(stage_text,     flag=flag|wx.ALIGN_RIGHT,  proportion=1,
                border=3)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_click, self)
        self.Bind(wx.EVT_BUTTON, self.on_click, stage_icon)
        self.Bind(wx.EVT_BUTTON, self.on_click, stage_text)

        self.stage_icon = stage_icon

    def on_click(self, event):
        event.Skip()
        pub.sendMessage(topic='STAGE_CHOSEN', 
                        data=self.stage_name)

    def show_results_icon(self, state):
        pass

    def show_stage_icon(self, state):
        self.stage_icon.Show(state)

class StrategySummary(wx.Panel):
    '''
        The StrategySummary shows what methods are chosen for each of the
    processing stages.  Users can select a stage by clicking on them.
    '''
    def __init__(self, parent, plugin_manager, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.SetBackgroundColour(wx.WHITE)

        self.stage_choosers = []
        for stage_name in stages.stages:
            stage_display_name = stages.get_stage_display_name(stage_name)
            method_names = plugin_manager.get_plugins_by_stage(
                    stage_name).keys()
            self.stage_choosers.append(StrategyStageChooser(self, stage_name,
                                                        stage_display_name,
                                                        sorted(method_names)))
        self.stage_choosers.append(StrategyAuxiliaryChooser(self, 'auxiliary',
                stages.get_stage_display_name('auxiliary')))
        
        # issued when user chooses a stage to adjust its parameters, not when
        # user clicks on results tab.
        pub.subscribe(self.select_stage, "STAGE_CHOSEN")

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        for stage_chooser in self.stage_choosers:
            sizer.Add(stage_chooser, flag=wx.EXPAND)

        self.SetMaxSize((config['gui']['strategy_pane']['min_width']-10,-1))
        self.SetSizerAndFit(sizer)

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
            if hasattr(stage_chooser, 'get_current_method'):
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
            show_fn(stage_chooser.stage_name == stage_name)

        if not results:
            self._current_stage = stage_name

        self.Layout()

    @property
    def current_stage(self):
        return self._current_stage

