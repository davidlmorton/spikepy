import string

import wx

from . import program_text as pt

class FloatValidator(wx.PyValidator):
    valid_characters = ".-%s%s" % (string.digits, chr(8))
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.Bind(wx.EVT_CHAR, self._on_char)

    def Clone(self):
        return FloatValidator()

    def Validate(self, data=None):
        win = self.GetWindow()
        val = win.GetValue()

        try:
            float(val)
            win.SetBackgroundColour('white')
            return True
        except ValueError:
            win.SetBackgroundColour('pink')
            return False

    def _on_char(self, event):
        key = event.GetKeyCode()
        if key < 256:
            chr_key = chr(key)
            if chr(key) not in FloatValidator.valid_characters:
                return
            if chr(key) in string.ascii_letters:
                return
        event.Skip()
        wx.CallLater(10, self.Validate)

class CharacterSubsetValidator(wx.PyValidator):
    def __init__(self, valid_characters, **kwargs):
        # add backspace and enter keys to valid characters
        valid_characters += chr(8) + chr(13)
        self._valid_characters = valid_characters

        wx.PyValidator.__init__(self, **kwargs)
        self.Bind(wx.EVT_CHAR, self._on_char)

    def Clone(self):
        return CharacterSubsetValidator(self._valid_characters)

    def Validate(self, dlg=None):
        return True

    def _on_char(self, event):
        key = event.GetKeyCode()
        if key < 256 and chr(key) not in self._valid_characters:
            return # eat the event.
        event.Skip()

class FilenameValidator(CharacterSubsetValidator):
    def __init__(self, valid_characters, **kwargs):
        CharacterSubsetValidator.__init__(self, valid_characters, **kwargs)

    def Clone(self):
        return FilenameValidator(self._valid_characters)

    def Validate(self, dlg=None, can_exit=True):
        win = self.GetWindow()
        new_name = win.GetValue()
        # ensure current name is not one of the other names.
        has_error = False
        all_other_trial_names = [otrial.display_name 
                                 for otrial in dlg.all_other_trials]
        if new_name in all_other_trial_names:
            dlg.warning_text.SetLabel(pt.NAME_ALREADY_EXISTS % new_name)
            has_error = True
        if new_name.startswith('.'):
            dlg.warning_text.SetLabel(pt.NAME_CANNOT_BEGIN_WITH)
            has_error = True
        if has_error:
            win.SetBackgroundColour('pink')
            return False
        else:
            if can_exit:
                dlg.EndModal(wx.ID_OK)
                return True
            else:
                dlg.warning_text.SetLabel('')
                win.SetBackgroundColour('white')
                return True

    def _reset_background_color(self):
        win = self.GetWindow()
        win.SetBackgroundColour('white')
        

