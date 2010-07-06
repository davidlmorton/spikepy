import wx

from spikepy.gui.utils import NamedChoiceCtrl, NamedTextCtrl, recursive_layout
from spikepy.gui.look_and_feel_settings import lfs


class ControlPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        window_names = ['boxcar', 'triang', 'Blackman', 'Hamming', 'Hanning',
                        'Bartlett', 'Parzen', 'Bohman', 'Blackman-Harris', 
                        'Nuttall', 'Barthann']
        window_chooser = NamedChoiceCtrl(self, name="Windowing function:",
                                           choices=window_names)
        passband_chooser = NamedChoiceCtrl(self, name="Passband Type:", 
                                           choices=["High Pass", "Low Pass", 
                                                    "Band Pass"])
        low_cutoff_textctrl = NamedTextCtrl(self, name="Low cutoff frequency:")
        high_cutoff_textctrl = NamedTextCtrl(self, 
                                             name="High cutoff frequency:")
        cutoff_textctrl = NamedTextCtrl(self, name="Cutoff frequency:")
        taps_textctrl = NamedTextCtrl(self, name="Taps:")

        sizer = wx.BoxSizer(orient=wx.VERTICAL)

        flag = wx.ALIGN_LEFT|wx.ALL|wx.EXPAND
        border = lfs.CONTROL_PANEL_BORDER
        sizer.Add(window_chooser,   proportion=0, 
                  flag=flag, border=border)
        sizer.Add(passband_chooser, proportion=0, 
                  flag=flag, border=border)
        sizer.Add(taps_textctrl,    proportion=0, 
                  flag=flag, border=border)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_CHOICE, self._passband_choice_made, 
                  passband_chooser.choice)
        self.low_cutoff_textctrl = low_cutoff_textctrl
        self.high_cutoff_textctrl = high_cutoff_textctrl
        self.cutoff_textctrl = cutoff_textctrl
        self.window_chooser = window_chooser
        self.passband_chooser = passband_chooser
        self.taps_textctrl = taps_textctrl
        self._passband_choice_made()

    def get_parameters(self):
        window_chosen = self.window_chooser.GetStringSelection()
        if window_chosen == 'Blackman-Harris':
            window_chosen = 'blackmanharris' # how scipy needs it.
        passband_chosen = self.passband_chooser.GetStringSelection()
        if passband_chosen == "Band Pass":
            low_cutoff_freq = float(self.low_cutoff_textctrl.GetValue())
            high_cutoff_freq = float(self.high_cutoff_textctrl.GetValue())
            critical_freq = (low_cutoff_freq, high_cutoff_freq)
        else:
            critical_freq = float(self.cutoff_textctrl.text_ctrl.GetValue())
        taps = int(self.taps_textctrl.GetValue())

        kind = passband_chosen.lower().split()[0] 
        settings = {'window_name':str(window_chosen).lower(), # scipy can't
                                                              # deal w/ unicode
                    'critical_freq':critical_freq, 
                    'taps':taps, 
                    'kind':kind}
        return settings

    def _passband_choice_made(self, event=None):
        self.low_cutoff_textctrl.Show(False)
        self.high_cutoff_textctrl.Show(False)
        self.cutoff_textctrl.Show(False)
        sizer = self.GetSizer()
        sizer.Detach(self.low_cutoff_textctrl)
        sizer.Detach(self.high_cutoff_textctrl)
        sizer.Detach(self.cutoff_textctrl)
        if (event==None or event.GetString() == "High Pass" or
            event.GetString() == "Low Pass"):
            sizer.Insert(2, self.cutoff_textctrl, proportion=0, 
                         flag=wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, border=2)
            self.cutoff_textctrl.Show(True)
        else:
            sizer.Insert(2, self.high_cutoff_textctrl, proportion=0, 
                         flag=wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, border=2)
            sizer.Insert(2, self.low_cutoff_textctrl, proportion=0, 
                         flag=wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, border=2)
            self.high_cutoff_textctrl.Show(True)
            self.low_cutoff_textctrl.Show(True)
        recursive_layout(self)
