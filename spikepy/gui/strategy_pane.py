
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

