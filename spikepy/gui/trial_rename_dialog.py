import string

import wx
from .validators import FilenameValidator
from . import program_text as pt
from .named_controls import NamedTextCtrl 

valid_filename_characters = ('-_.,)(%s%s' % 
                             (string.ascii_letters, string.digits))

class TrialRenameDialog(wx.TextEntryDialog):
    def __init__(self, parent, trial_name, fullpath, 
                       other_trial_names, *args, **kwargs):
        message =  'Fullpath: %s' % fullpath
        self._valid_characters = valid_filename_characters
        wx.TextEntryDialog.__init__(self, parent, message, 
                caption='Enter New Trial Name',
                defaultValue=trial_name, **kwargs)

        # if you add validator too early, it won't accept the defaultValue
        wx.CallLater(300, self._add_validator)

    def _add_validator(self):
        # add a validator to the textctrl
        for child in self.GetChildren():
            if isinstance(child, wx.TextCtrl):
                # for some reason after dlg closes dlg.GetValue() will always
                # be the original value, but dlg._text_ctrl.GetValue() will
                # get the correct value.
                self._text_ctrl = child
                child.SetValidator(FilenameValidator(valid_filename_characters))
