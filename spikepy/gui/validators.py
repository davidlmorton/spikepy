import string

import wx

class FloatValidator(wx.PyValidator):
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
            if chr(key) not in valid_characters:
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

    def Validate(self, dlg=None):
        win = self.GetWindow()
        val = win.GetValue()
        if val.startswith('.'):
            win.SetBackgroundColour('pink')
            wx.CallLater(300, self._reset_background_color)
            return False
        win.SetBackgroundColour('white')
        dlg.EndModal(wx.ID_OK)
        return True

    def _reset_background_color(self):
        win = self.GetWindow()
        win.SetBackgroundColour('white')
        

