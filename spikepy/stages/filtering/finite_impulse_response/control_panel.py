import wx

from spikepy.gui.named_controls import NamedChoiceCtrl, NamedSpinCtrl
from spikepy.gui.utils import recursive_layout
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
        low_cutoff_spinctrl = NamedSpinCtrl(self, name="Low cutoff frequency:",
                                            min=10, max=100000)
        high_cutoff_spinctrl = NamedSpinCtrl(self, 
                                             name="High cutoff frequency:",
                                             min=10, max=100000)
        cutoff_spinctrl = NamedSpinCtrl(self, name="Cutoff frequency:",
                                              min=10, max=100000)
        taps_spinctrl = NamedSpinCtrl(self, name="Taps:",
                                            min=40, max=5000)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)

        flag = wx.ALIGN_LEFT|wx.ALL|wx.EXPAND
        border = lfs.CONTROL_PANEL_BORDER
        sizer.Add(window_chooser,   proportion=0, 
                  flag=flag, border=border)
        sizer.Add(passband_chooser, proportion=0, 
                  flag=flag, border=border)
        sizer.Add(low_cutoff_spinctrl, proportion=0, 
                  flag=flag, border=border)
        sizer.Add(high_cutoff_spinctrl, proportion=0, 
                  flag=flag, border=border)
        sizer.Add(cutoff_spinctrl, proportion=0, 
                  flag=flag, border=border)
        sizer.Add(taps_spinctrl,    proportion=0, 
                  flag=flag, border=border)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_CHOICE, self._passband_choice_made, 
                  passband_chooser.choice)
        self.low_cutoff_spinctrl = low_cutoff_spinctrl
        self.high_cutoff_spinctrl = high_cutoff_spinctrl
        self.cutoff_spinctrl = cutoff_spinctrl
        self.window_chooser = window_chooser
        self.passband_chooser = passband_chooser
        self.taps_spinctrl = taps_spinctrl

        # --- SET DEFAULTS ---
        self.window_chooser.SetStringSelection('Hamming')
        self.passband_chooser.SetStringSelection('High Pass')
        self._passband_choice_made(band_type='High Pass')
        low_cutoff_spinctrl.SetValue(300)
        high_cutoff_spinctrl.SetValue(3000) 
        cutoff_spinctrl.SetValue(300)
        taps_spinctrl.SetValue(101)

    def get_parameters(self):
        window_chosen = self.window_chooser.GetStringSelection()
        if window_chosen == 'Blackman-Harris':
            window_chosen = 'blackmanharris' # how scipy needs it.
        passband_chosen = self.passband_chooser.GetStringSelection()
        if passband_chosen == "Band Pass":
            low_cutoff_freq = float(self.low_cutoff_spinctrl.GetValue())
            high_cutoff_freq = float(self.high_cutoff_spinctrl.GetValue())
            critical_freq = (low_cutoff_freq, high_cutoff_freq)
        else:
            critical_freq = float(self.cutoff_spinctrl.GetValue())
        taps = int(self.taps_spinctrl.GetValue())

        kind = passband_chosen.lower().split()[0] 
        settings = {'window_name':str(window_chosen).lower(), # scipy can't
                                                              # deal w/ unicode
                    'critical_freq':critical_freq, 
                    'taps':taps, 
                    'kind':kind}
        return settings

    def _passband_choice_made(self, event=None, band_type=None):
        if event is not None:
            band_type = event.GetString()
        self.low_cutoff_spinctrl.Show(False)
        self.high_cutoff_spinctrl.Show(False)
        self.cutoff_spinctrl.Show(False)
        if (band_type == "High Pass" or
            band_type == "Low Pass"):
            self.cutoff_spinctrl.Show(True)
        else:
            self.high_cutoff_spinctrl.Show(True)
            self.low_cutoff_spinctrl.Show(True)
        recursive_layout(self)
