import wx

from .look_and_feel_settings import lfs

class NamedChoiceCtrl(wx.Panel):
    def __init__(self, parent, name="", choices=[], bar_width=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.name = wx.StaticText(self, label=name)
        if bar_width == None and len(choices) > 0:
            bar_width_in_characters = max(map(len, choices))
            bar_width = bar_width_in_characters*8
            self.choice = wx.Choice(self, choices=choices) 
        elif bar_width == None and len(choices) == 0:
            self.choice = wx.Choice(self, choices=choices)
        else:
            self.choice = wx.Choice(self, choices=choices)
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        border = lfs.CHOICE_BORDER
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        sizer.Add(self.name, proportion=0, flag=flag, border=border)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.choice, proportion=1, flag=flag, border=border)
        
        self.SetSizer(sizer)

    def GetStringSelection(self):
        return self.choice.GetStringSelection()

    def SetStringSelection(self, string):
        return self.choice.SetStringSelection(string)

class NamedTextCtrl(wx.Panel):
    def __init__(self, parent, name="", **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.name = wx.StaticText(self, label=name)
        self.text_ctrl = wx.TextCtrl(self, size=(50,-1))
        
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        border=lfs.TEXT_CTRL_BORDER
        sizer.Add(self.name, proportion=0, 
                  flag=flag|wx.ALIGN_RIGHT, border=border)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.text_ctrl, proportion=1, 
                  flag=flag|wx.ALIGN_LEFT, border=border)

        self.SetSizer(sizer)

    def GetValue(self):
        return self.text_ctrl.GetValue()

class OptionalNamedTextCtrl(NamedTextCtrl):
    def __init__(self, parent, name, enabled=False, **kwargs):
        NamedTextCtrl.__init__(self, parent, name='', **kwargs)
        
        self.checkbox = wx.CheckBox(self, label=name)
        self.GetSizer().Insert(0, self.checkbox, proportion=0, flag=wx.ALL,
                                                 border=3)
        self.Bind(wx.EVT_CHECKBOX, self._enable, self.checkbox)
        self._enabled = enabled
        self._enable(state=enabled)

    def _enable(self, event=None, state=None):
        if state is None:
            state = event.IsChecked()
        self._enabled = state
        self.name.Enable(state)
        self.text_ctrl.Enable(state)
