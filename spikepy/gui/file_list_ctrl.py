import os

import wx
import wx.lib.mixins.listctrl as listmix

from spikepy.gui import utils

class FileListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    """
    This list control displays what files are opened and allows users to 
        open/close files by right-click popups.
    """
    def __init__(self, parent, **kwargs):
        wx.ListCtrl.__init__(self, parent, **kwargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        self.InsertColumn(0, 'Filename')
        self.InsertColumn(1, 'Path')

        self.Bind(wx.EVT_CONTEXT_MENU, self._context_menu)

    def add_file(self, filename, path):
        num_items = self.GetItemCount()
        self.InsertStringItem(num_items, filename)
        self.SetStringItem(num_items, 1, path)
        self.autosize_columns()

    def autosize_columns(self):
        for col in [0,1]:
            self.SetColumnWidth(col, wx.LIST_AUTOSIZE_USEHEADER)
            header_width = self.GetColumnWidth(col)
            self.SetColumnWidth(col, wx.LIST_AUTOSIZE)
            list_width = self.GetColumnWidth(col)
            self.SetColumnWidth(col, max(header_width, list_width))

    def _context_menu(self, event):
        if not hasattr(self, '_cmid_open_file'):
            self._cmid_open_file  = wx.NewId()
            self._cmid_close_file = wx.NewId()

            self.Bind(wx.EVT_MENU, self._open_file,  id=self._cmid_open_file)
            self.Bind(wx.EVT_MENU, self._close_file, id=self._cmid_close_file)

        cm = wx.Menu()
        # open file item
        item = wx.MenuItem(cm, self._cmid_open_file, 'Open Another File...')
        bmp = utils.get_bitmap_icon('folder')
        item.SetBitmap(bmp)
        cm.AppendItem(item)
        # close file item
        item = wx.MenuItem(cm, self._cmid_close_file, 'Close File')
        bmp = utils.get_bitmap_icon('action_stop')
        item.SetBitmap(bmp)
        cm.AppendItem(item)
        self.PopupMenu(cm)
        cm.Destroy()

    def _open_file(self, event):
        paths = []
        dlg = wx.FileDialog(self, message="Choose file(s) to open.",
                            defaultDir=os.getcwd(),
                            style=wx.OPEN|wx.MULTIPLE) 
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
        dlg.Destroy()
        for path in paths:
            p, fn = os.path.split(path)
            # XXX just publish open file request
            self.add_file(fn,p)

    def _close_file(self, event):
        item = self.GetFocusedItem()
        # XXX just publish close file request
        self.DeleteItem(item)
        self.autosize_columns()


