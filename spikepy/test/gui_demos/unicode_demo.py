"""
copyright (c) 2011  david morton

this program is free software: you can redistribute it and/or modify
it under the terms of the gnu general public license as published by
the free software foundation, either version 3 of the license, or
(at your option) any later version.

this program is distributed in the hope that it will be useful,
but without any warranty; without even the implied warranty of
merchantability or fitness for a particular purpose.  see the
gnu general public license for more details.

you should have received a copy of the gnu general public license
along with this program.  if not, see <http://www.gnu.org/licenses/>.
"""
import wx

app = wx.PySimpleApp()
main_frame = wx.Frame(None, title='Choice Demo',
                                 size=(400, 300))

sizer = wx.BoxSizer(orient=wx.VERTICAL)

text_out = wx.StaticText(main_frame)
text_in = wx.TextCtrl(main_frame, size=(250, -1))
update_button = wx.Button(main_frame, label='Update')
def update_text(event):
    event.Skip()
    text_out.SetLabel(eval(text_in.GetValue()))
    sizer.Layout()
main_frame.Bind(wx.EVT_BUTTON, update_text)

font_picker = wx.FontPickerCtrl(main_frame)
def update_font(event):
    event.Skip()
    font = font_picker.GetSelectedFont()
    text_out.SetFont(font)
    sizer.Layout()
main_frame.Bind(wx.EVT_FONTPICKER_CHANGED, update_font)

sizer.Add(text_out)
sizer.Add(text_in)
sizer.Add(update_button)
sizer.Add(font_picker)

# set sizer and run app
main_frame.SetSizer(sizer)
main_frame.Show()
app.MainLoop()
