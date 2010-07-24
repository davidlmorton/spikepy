
import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.buttons import GenButton

from .named_controls import NamedChoiceCtrl
from .utils import recursive_layout
from ..stages import filtering, detection, extraction
from .look_and_feel_settings import lfs
from . import program_text as pt
from .strategy_manager import StrategyManager

class StrategyPane(ScrolledPanel):
    def __init__(self, parent, **kwargs):
        ScrolledPanel.__init__(self, parent, **kwargs)
        
        self.strategy_chooser = NamedChoiceCtrl(self, name=pt.STRATEGY_NAME)
        self.strategy_summary = StrategySummary(self)
        self.save_button = wx.Button(self, label=pt.SAVE_STRATEGY)
        line = wx.StaticLine(self)
        stage_choicebook = wx.Choicebook(self, wx.ID_ANY)

        # ===== PANELS =====
        detection_filter_panel = StagePanel(stage_choicebook, 
                                             1, pt.DETECTION_FILTER, filtering)
        detection_panel = StagePanel(stage_choicebook, 
                                             2, pt.DETECTION, detection)
        extraction_filter_panel = StagePanel(stage_choicebook, 
                                             3, pt.EXTRACTION_FILTER, filtering)
        extraction_panel = StagePanel(stage_choicebook, 
                                             4, pt.EXTRACTION, extraction)
        clustering_panel = wx.Panel(stage_choicebook)

        # ===== CHOICEBOOK PAGES =====
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
        
        # ===== SETUP SIZER =====
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

        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self._page_changed)
        pub.subscribe(self._results_notebook_page_changing, 
                      topic='RESULTS_NOTEBOOK_PAGE_CHANGING')
        self.stages = [detection_filter_panel,
                       detection_panel,
                       extraction_filter_panel,
                       extraction_panel,
                       clustering_panel][:-1]
        self.strategy_manager = StrategyManager(self)
    
    def _results_notebook_page_changing(self, message=None):
        old_page_num, new_page_num = message.data
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
    def __init__(self, parent, stage_num, stage_name, stage_module, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.stage_num = stage_num
        self.stage_name = stage_name
        
        title_panel = TitlePanel(self, stage_num, stage_name)

        # --- setup methods ---
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

        # --- setup other panel elements ---
        self.method_chooser = NamedChoiceCtrl(self, name=pt.METHOD+":",
                                 choices=self.method_names)
#        self.method_description_text = StaticBoxText(self, label='Description') 
        self.run_button = wx.Button(self, label=pt.RUN)
        self.run_button.Show(False)

        # --- sizer config ---
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        ea_flag = wx.EXPAND|wx.ALL
        sizer.Add(title_panel,                  proportion=0, 
                      flag=ea_flag,                        border=3)
        sizer.Add(self.method_chooser,          proportion=0, 
                      flag=ea_flag,                        border=3)
 #       sizer.Add(self.method_description_text, proportion=0, 
 #                     flag=ea_flag,                        border=3)
        for method in self.methods.values():
            sizer.Add(method['control_panel'],  proportion=0,
                      flag=ea_flag,                        border=6)
        sizer.Add(self.run_button,              proportion=0, 
                      flag=wx.ALL,                         border=1)
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_CHOICE, self._method_choice_made,
                  self.method_chooser.choice)
        self.Bind(wx.EVT_BUTTON, self._run, self.run_button)
#        self._method_choice_made(method_name=self._method_name_chosen)
        
        pub.subscribe(self._running_completed, topic='RUNNING_COMPLETED')
        pub.subscribe(self._set_stage_parameters, topic='SET_PARAMETERS')
        self._method_choice_made(method_name=self.method_names[0])

    def _set_stage_parameters(self, message=None):
        kwargs = message.data
        stage_name = kwargs['stage_name']
        if stage_name.lower() != self.stage_name.lower():
            print "not right panel. This panel is %s" % self.stage_name
            print "stage_name.lower is %s" % stage_name.lower()
            return # not the right stage_panel
        method_name = kwargs['method_name']
        parameters = {}
        for key, value in kwargs.items():
            if (key != 'stage_name' and 
                key != 'method_name'):
                parameters[key] = value
        print parameters
        self.methods[method_name]['control_panel'].set_parameters(**parameters)
        self._method_choice_made(method_name=method_name)

    def _running_completed(self, message=None):
        self.run_button.SetLabel(pt.RUN)
        self.run_button.Enable()

    
    def _method_choice_made(self, event=None, method_name=None):
        self.methods[self._method_name_chosen]['control_panel'].Show(False)

        if method_name is not None:
            self._method_name_chosen = method_name
            self.method_chooser.SetStringSelection(method_name)
        else:
            self._method_name_chosen = self.method_chooser.GetStringSelection()

        #self.method_description_text.SetText( 
        #        self.methods[self._method_name_chosen]['description'])

        self.methods[self._method_name_chosen]['control_panel'].Show(True)
        self.run_button.Show(True)
        self.Layout()
        pub.sendMessage(topic="UPDATE_STRATEGY_SUMMARY", 
                        data=(self.stage_num, self._method_name_chosen))
    

    def _run(self, event=None):
        control_panel = self.methods[self._method_name_chosen]['control_panel']
        settings = control_panel.get_parameters()
        self.run_button.SetLabel(pt.RUN_BUTTON_RUNNING_STATUS)
        self.run_button.Disable()
        wx.Yield() # about to let scipy hog cpu, so process all wx events.
        topic = self.stage_name.split()[-1].upper()
        print settings
        pub.sendMessage(topic=topic, data=(self.stage_name, 
                                              self._method_name_chosen,
                                              settings))

class DetectionPanel(wx.Panel):
    def __init__(self, parent, stage_num, stage_name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        title_panel = TitlePanel(self, stage_num, stage_name)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        ea_flag = wx.EXPAND|wx.ALL
        sizer.Add(title_panel, proportion=0, flag=ea_flag, border=5)

        self.SetSizer(sizer)
    

class TitlePanel(wx.Panel):
    def __init__(self, parent, stage_num, stage_name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        stage_num_text = wx.StaticText(self, label="Stage\n%d" % stage_num,
                                       style=wx.ALIGN_CENTER)
        stage_num_font = stage_num_text.GetFont()
        stage_num_font.SetWeight(wx.FONTWEIGHT_BOLD)
        stage_num_text.SetFont(stage_num_font)
        stage_name_text = wx.StaticText(self, label=stage_name)
        
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(stage_num_text, proportion=0, flag=wx.EXPAND|wx.ALL, 
                                                                    border=5)
        sizer.Add(stage_name_text, proportion=0, 
                  flag=wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(sizer)

class DescriptionPanel(wx.Panel):
    def __init__(self, parent, description="Choose a filter method.", **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.description = description
        description_text = wx.StaticText(self, 
                                    label="Description: %s" % self.description)
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(description_text, proportion=0)
        
        self.SetSizer(sizer)

class ControlsPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

def make_dict_hashable(unhashable_dict):
    for key in unhashable_dict.keys():
        if (isinstance(unhashable_dict[key], dict) and 
            not isinstance(unhashable_dict[key], HashableDict)):
            unhashable_dict[key] = HashableDict(unhashable_dict[key])
            make_dict_hashable(unhashable_dict[key])


