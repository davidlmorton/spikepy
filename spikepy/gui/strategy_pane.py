import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.buttons import GenButton

from .utils import NamedChoiceCtrl, recursive_layout
from ..stages import filtering, detection
from .look_and_feel_settings import lfs

class StrategyPane(ScrolledPanel):
    def __init__(self, parent, **kwargs):
        ScrolledPanel.__init__(self, parent, **kwargs)
        
        self.strategy_summary = StrategySummary(self)
        line = wx.StaticLine(self)
        stage_choicebook = wx.Choicebook(self, wx.ID_ANY)

        detection_filter_panel = StagePanel(stage_choicebook, 
                                             1, "Detection Filter", filtering)
        detection_panel = StagePanel(stage_choicebook, 
                                         2, "Spike Detection", detection)
        extraction_filter_panel = StagePanel(stage_choicebook, 
                                              3, "Extraction Filter", filtering)
        extraction_panel = wx.Panel(stage_choicebook)
        clustering_panel = wx.Panel(stage_choicebook)

        stage_choicebook.AddPage(detection_filter_panel, 
                                 "Detection Filter Strategy")
        stage_choicebook.AddPage(detection_panel, "Detection Strategy")
        stage_choicebook.AddPage(extraction_filter_panel, 
                                 "Extraction Filter Strategy")
        stage_choicebook.AddPage(extraction_panel, "Extraction Strategy")
        stage_choicebook.AddPage(clustering_panel, "Clustering Strategy")
        
        # setup the sizer
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.EXPAND|wx.ALL
        border = lfs.STRATEGY_PANE_BORDER
        sizer.Add(self.strategy_summary,  proportion=0, 
                                          flag=flag|wx.ALIGN_CENTER_HORIZONTAL, 
                                          border=border)
        sizer.Add(line,  proportion=0, 
                                          flag=flag|wx.ALIGN_CENTER_HORIZONTAL, 
                                          border=border)
        sizer.Add(stage_choicebook,  proportion=1, flag=flag, border=border)
        self.strategy_summary.select_stage(1)
        self.SetSizer(sizer)
        self.do_layout()

        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self._page_changed)

    def _page_changed(self, event=None):
        if event is not None:
            new_page_num = event.GetSelection()
            self.strategy_summary.select_stage(new_page_num+1)

    def do_layout(self):
        self.SetupScrolling()
        self.Layout()

class StrategySummary(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        
        s = []
        stages = ['Detection Filter', 'Detection', 'Extraction Filter', 
                  'Extraction', 'Clustering']
        size = (140, -1)
        for stage in stages:
            s.append(wx.StaticText(self, label=stage+':', size=size,
                               style=wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE))

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        lsizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.ALL
        border = lfs.STRATEGY_SUMMARY_BORDER
        for index, stage_text in enumerate(s):
            lsizer.Add(stage_text, proportion=0, flag=flag, 
                                  border=border)
        sizer.Add(lsizer, proportion=1)
        self.SetSizer(sizer)
        self.stage_text_list = s
        self._selected_stage = 1

    def select_stage(self, stage_num):
        old_stage_text = self.stage_text_list[self._selected_stage-1]
        stage_font = old_stage_text.GetFont()
        stage_font.SetWeight(wx.FONTWEIGHT_NORMAL)
        old_stage_text.SetFont(stage_font)

        new_stage_text = self.stage_text_list[stage_num-1]
        stage_font = new_stage_text.GetFont()
        stage_font.SetWeight(wx.FONTWEIGHT_BOLD)
        new_stage_text.SetFont(stage_font)
        self._selected_stage = stage_num
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
        self.method_chooser = NamedChoiceCtrl(self, name="Method:",
                                 choices=self.method_names)
#        self.method_description_text = StaticBoxText(self, label='Description') 
        self.run_button = wx.Button(self, label="Run")
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
        sizer.Add(self.run_button,           proportion=0, 
                      flag=wx.ALL,                         border=1)
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_CHOICE, self._method_choice_made,
                  self.method_chooser.choice)
        self.Bind(wx.EVT_BUTTON, self._run, self.run_button)
#        self._method_choice_made(method_name=self._method_name_chosen)
        
        pub.subscribe(self._running_completed, topic='RUNNING_COMPLETED')
        self._method_choice_made(method_name=self.method_names[0])

    def _running_completed(self, message=None):
        self.run_button.SetLabel('Run')
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
    

    def _run(self, event=None):
        control_panel = self.methods[self._method_name_chosen]['control_panel']
        settings = control_panel.get_parameters()
        self.run_button.SetLabel('Running...')
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
