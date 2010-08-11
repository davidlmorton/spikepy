import os

import wx.grid as gridlib
from wx.lib.pubsub import Publisher as pub
from spikepy.gui import utils
import wx

from . import program_text as pt

class FileGridCtrl(gridlib.Grid):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        gridlib.Grid.__init__(self, parent, **kwargs)

        self._num_empty_rows = 8
        self.CreateGrid(self._num_empty_rows, 3)
        # ---- column settings -----
        attr1 = gridlib.GridCellAttr()
        attr1.SetReadOnly(True)
        attr1.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER) 
        # set all columns to use this set of attributes
        self.SetColAttr(0, attr1)
        self.SetColAttr(1, attr1)
        self.SetColAttr(2, attr1)
        # set the column labels
        self.SetColLabelValue(0, "")
        self.SetColLabelValue(1, pt.TRIAL_NAME)
        self.SetColLabelValue(2, pt.FULLPATH)
        # set the column widths
        self.SetColSize(0, 10)
        self.SetColSize(1, 80)
        self.SetColSize(2, 150)

        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self._on_right_click)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self._on_left_click)

        # set it up so that selections select the whole row
        self.SetSelectionMode(self.wxGridSelectRows)

        self.SetRowLabelSize(0)
        # this will hold what should be in the grid
        
        pub.subscribe(self._file_opened, topic='FILE_OPENED')
        pub.subscribe(self._file_opened, topic='FILE_ALREADY_OPENED')
        pub.subscribe(self._file_closed, topic='FILE_CLOSED')
        pub.subscribe(self._opening_data_file, topic='OPENING_DATA_FILE')
        self.EnableGridLines(False)

    def _file_closed(self, message):
        fullpath = message.data
        num_rows = self.GetNumberRows()
        selected_row = self.GetSelectedRows()[0]
        for row in xrange(self._number_nonempty_rows):
            if fullpath == self.GetCellValue(row, 2):
                if row == selected_row:
                    pub.sendMessage(topic='SHOW PLOT', data='DEFAULT')
                self.DeleteRows(pos=row)
                break
        
    def _on_right_click(self, event):
        row = event.GetRow()
        if not hasattr(self, '_cmid_open_file'):
            self._cmid_open_file  = wx.NewId()
            self._cmid_close_selected_files = wx.NewId()
            self._cmid_close_this_file = wx.NewId()

            self.Bind(wx.EVT_MENU, self._open_file,  id=self._cmid_open_file)
            self.Bind(wx.EVT_MENU, self._close_selected_files, 
                                   id=self._cmid_close_selected_files)
            self.Bind(wx.EVT_MENU, self._close_this_file, 
                                   id=self._cmid_close_this_file)

        cm = wx.Menu()
        if self._number_nonempty_rows:
            row = event.GetRow()
            fullpath = self.GetCellValue(row, 2)
        # open file item
        if self._number_nonempty_rows:
            item = wx.MenuItem(cm, self._cmid_open_file, pt.OPEN_ANOTHER_FILE)
        else:
            item = wx.MenuItem(cm, self._cmid_open_file, pt.OPEN_FILE)
        bmp = utils.get_bitmap_icon('folder')
        item.SetBitmap(bmp)
        cm.AppendItem(item)
        # close this file item
        item = wx.MenuItem(cm, self._cmid_close_this_file, pt.CLOSE_THIS_FILE)
        if row >= self._number_nonempty_rows:
            cm.Enable(self._cmid_close_this_file, False)
        bmp = utils.get_bitmap_icon('action_stop')
        item.SetBitmap(bmp)
        cm.AppendItem(item)
        # close selected files item
        item = wx.MenuItem(cm, self._cmid_close_selected_files, 
                               pt.CLOSE_SELECTED_FILES)
        if self.GetSelectedRows():
            cm.Enable(self._cmid_close_selected_files, False)
        bmp = utils.get_bitmap_icon('action_stop')
        item.SetBitmap(bmp)
        cm.AppendItem(item)
        self.PopupMenu(cm)
        cm.Destroy()

    def _open_file(self, event):
        pub.sendMessage(topic='OPEN_FILE', data=self)

    def _close_selected_files(self, event=None):
        for row in self.GetSelectedRows():
            fullpath = self.GetCellValue(row, 2)
            pub.sendMessage(topic='CLOSE_DATA_FILE', data=fullpath)

    def _close_this_file(self, event=None):
        row = self._row_right_clicked
        fullpath = self.GetCellValue(row, 2)
        pub.sendMessage(topic='CLOSE_DATA_FILE', data=fullpath)

    @property
    def _number_nonempty_rows(self):
        return self.GetNumberRows() - self._num_empty_rows
        
    def _opening_data_file(self, message):
        fullpath = message.data
        filename = os.path.split(fullpath)[1]
        for row in xrange(self._number_nonempty_rows):
            if fullpath == self.GetCellValue(row, 2):
                return
        self.SetCellValue(self._number_nonempty_rows, 1, 
                          "%s(%s)" % (pt.FILE_OPENING_STATUS, filename))
        self.SetCellValue(self._number_nonempty_rows, 2, fullpath)
        if self._num_empty_rows:
            self._num_empty_rows -= 1
        else:
            self.AppendRows()
            
    def _file_opened(self, message):
        fullpath, display_name = message.data
        num_rows = self.GetNumberRows()
        for row in xrange(self._number_nonempty_rows):
            fullpath_from_row =  self.GetCellValue(row, 2)
            if fullpath == fullpath_from_row:
                self.SetCellValue(row, 1, display_name) 

    def _on_left_click(self, event):
        row = event.GetRow()
        column = event.GetColumn()
        fullpath = self.GetCellValue(row, 2)
        if fullpath != '':
            pub.sendMessage(topic="FILE_SELECTION_CHANGED", data=fullpath)
        print row,column
        event.Skip()

