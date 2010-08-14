import os

import wx.grid as gridlib
from wx.lib.pubsub import Publisher as pub
from spikepy.gui import utils
from .look_and_feel_settings import lfs
import wx

from . import program_text as pt

class FileGridCtrl(gridlib.Grid):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        gridlib.Grid.__init__(self, parent, **kwargs)

        self._num_empty_rows = 8
        self.CreateGrid(self._num_empty_rows, 2)
        # ---- col settings -----
        attr0 = gridlib.GridCellAttr()
        #                    horizontal       vertical
        attr0.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER) 
        font = self.GetDefaultCellFont()
        font.SetPointSize(14)
        attr0.SetFont(font)
        attr1 = gridlib.GridCellAttr()
        attr1.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTER) 
        # set all cols to use this set of attributes
        self.SetColAttr(0, attr0)
        self.SetColAttr(1, attr1)
        # set the col labels
        self.SetColLabelValue(0, '%s/%s' % (lfs.FILE_LIST_UNMARKED_STATUS,
                                            lfs.FILE_LIST_MARKED_STATUS))
        self.SetColLabelValue(1, pt.TRIAL_NAME)
        # set the col widths
        self.SetColSize(0, 5)
        self._autosize_cols()

        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self._on_right_click)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self._on_left_click)
        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self._on_range_select)
        self.Bind(wx.EVT_SIZE, self._ensure_fills_space)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self._on_left_dclick)

        # set it up so that selections select the whole row
        self.SetSelectionMode(self.wxGridSelectRows)

        self.SetRowLabelSize(0)
        # this will hold what should be in the grid
        
        pub.subscribe(self._file_opened, topic='FILE_OPENED')
        pub.subscribe(self._file_opened, topic='FILE_ALREADY_OPENED')
        pub.subscribe(self._file_closed, topic='FILE_CLOSED')
        pub.subscribe(self._opening_data_file, topic='OPENING_DATA_FILE')
        pub.subscribe(self._trial_renamed, topic='TRIAL_RENAMED')
        self.EnableGridLines(False)
        self.DisableDragRowSize()
        self._last_fullpath_selected = None
        self.SetGridCursor(0, 4)
        self._opened_files = set()
        self._files = []


    def _autosize_cols(self):
        self.AutoSizeColumns()
        self._min_column_sizes=(self.GetColSize(0), self.GetColSize(1))
        self._ensure_fills_space()

    def _ensure_fills_space(self, event=None):
        if event is not None:
            event.Skip()
        marked_col_size = self.GetColSize(0)
        trial_name_col_size = self.GetColSize(1)
        used_size = marked_col_size + trial_name_col_size
        panel_width, panel_height = self.GetSize()
        fill_size = trial_name_col_size + panel_width - used_size
        self.SetColSize(1, max(fill_size, self._min_column_sizes[1]))

    def MakeCellVisible(self):
        pass # don't scroll to where the cursor is

    def _on_range_select(self, event):
        return # do not do event.Skip() thus not allowing range selection

    def _file_closed(self, message):
        fullpath = message.data
        num_rows = self.GetNumberRows()
        row = self._get_row_from_fullpath(fullpath)
        if row == self._left_clicked_row:
            pub.sendMessage(topic='SHOW PLOT', data='DEFAULT')
        self.DeleteRows(pos=row)
        self.AppendRows()
        self._num_empty_rows += 1
        self._opened_files.remove(fullpath)
        self._files.remove(fullpath)

    def _file_opened(self, message):
        fullpath, display_name = message.data
        self._opened_files.add(fullpath)
        num_rows = self.GetNumberRows()
        row = self._get_row_from_fullpath(fullpath)
        self.SetCellValue(row, 1, display_name) 
        self._autosize_cols()
        self._set_row_backround_color(row, 'white')
        # if there are no other files opening.
        if self._files == list(self._opened_files): 
            self._select_row(row)

    def _get_row_from_fullpath(self, fullpath):
        for row in xrange(self._num_nonempty_rows):
            fullpath_from_row =  self._get_fullpath(row)
            if fullpath == fullpath_from_row:
                return row

    def _on_right_click(self, event):
        row = event.GetRow()
        self._row_right_clicked = row
        if not hasattr(self, '_cmid_open_file'):
            self._cmid_open_file  = wx.NewId()
            self._cmid_rename_trial = wx.NewId()
            self._cmid_close_selected_files = wx.NewId()
            self._cmid_close_this_file = wx.NewId()

            self.Bind(wx.EVT_MENU, self._rename_trial, 
                                   id=self._cmid_rename_trial)
            self.Bind(wx.EVT_MENU, self._open_file,  id=self._cmid_open_file)
            self.Bind(wx.EVT_MENU, self._close_selected_files, 
                                   id=self._cmid_close_selected_files)
            self.Bind(wx.EVT_MENU, self._close_this_file, 
                                   id=self._cmid_close_this_file)

        cm = wx.Menu()
        if self._num_nonempty_rows:
            row = event.GetRow()

        if row < self._num_nonempty_rows:
            trial_name = self._get_trial_name(row)
            fullpath = self._get_fullpath(row)

        # rename_trial item
        if row >= self._num_nonempty_rows:
            item = wx.MenuItem(cm, self._cmid_rename_trial, pt.RENAME_TRIAL)
        else:
            item = wx.MenuItem(cm, self._cmid_rename_trial, pt.RENAME_TRIAL+
                               ' (%s)' % trial_name)
        bmp = utils.get_bitmap_icon('text_signature')
        item.SetBitmap(bmp)
        cm.AppendItem(item)
        if row >= self._num_nonempty_rows:
            cm.Enable(self._cmid_rename_trial, False)

        # open file item
        if self._num_nonempty_rows:
            item = wx.MenuItem(cm, self._cmid_open_file, pt.OPEN_ANOTHER_FILE)
        else:
            item = wx.MenuItem(cm, self._cmid_open_file, pt.OPEN_FILE)
        bmp = utils.get_bitmap_icon('folder')
        item.SetBitmap(bmp)
        cm.AppendItem(item)

        # close this file item
        if row < self._num_nonempty_rows and fullpath in self._opened_files:
            item = wx.MenuItem(cm, self._cmid_close_this_file, 
                               pt.CLOSE_THIS_FILE+' (%s)' % trial_name)
        else:
            item = wx.MenuItem(cm, self._cmid_close_this_file, 
                               pt.CLOSE_THIS_FILE)
        bmp = utils.get_bitmap_icon('action_stop')
        item.SetBitmap(bmp)
        cm.AppendItem(item)
        if (row >= self._num_nonempty_rows or
            (row < self._num_nonempty_rows and  # file is being opened still
             fullpath not in self._opened_files)):
            cm.Enable(self._cmid_close_this_file, False)

        # close selected files item
        item = wx.MenuItem(cm, self._cmid_close_selected_files, 
                               pt.CLOSE_SELECTED_FILES)
        bmp = utils.get_bitmap_icon('action_stop')
        item.SetBitmap(bmp)
        cm.AppendItem(item)
        if not self.marked_fullpaths:
            cm.Enable(self._cmid_close_selected_files, False)

        self.PopupMenu(cm)
        cm.Destroy()

    def _rename_trial(self, event=None):
        if event is not None: # came in through menu
            row = self._row_right_clicked
        else:
            row = self._row_left_dclicked
        fullpath = self._get_fullpath(row)
        pub.sendMessage(topic='OPEN_RENAME_TRIAL_DIALOG', data=fullpath)

    def _trial_renamed(self, message):
        trial = message.data
        fullpath = trial.fullpath
        name = trial.display_name
        row = self._get_row_from_fullpath(fullpath)
        self._set_trial_name(row, name)

    def _open_file(self, event):
        pub.sendMessage(topic='OPEN_FILE', data=self)

    def _close_selected_files(self, event=None):
        for fullpath in self.marked_fullpaths:
            pub.sendMessage(topic='CLOSE_DATA_FILE', 
                            data=fullpath)

    def _close_this_file(self, event=None):
        row = self._row_right_clicked
        fullpath = self._get_fullpath(row)
        pub.sendMessage(topic='CLOSE_DATA_FILE',
                        data=fullpath)

    def _opening_data_file(self, message):
        fullpath = message.data
        filename = os.path.split(fullpath)[1]
        self._files.append(fullpath)
        if self._get_row_from_fullpath(fullpath) is not None:
            return
        new_row = self._num_nonempty_rows
        self._set_trial_name(new_row, 
                             filename)
        self._set_row_backround_color(new_row, 'pink')
        self._set_marked_status(new_row, False)
        self._autosize_cols()
        if self._num_empty_rows > 1:
            self._num_empty_rows -= 1
        else:
            self.AppendRows()

    def _set_row_backround_color(self, row, color):
        for col in xrange(self.GetNumberCols()):
            self.SetCellBackgroundColour(row, col, color)

    @property
    def _num_nonempty_rows(self):
        return self.GetNumberRows() - self._num_empty_rows
        

    def _get_fullpath(self, row):
        return self._files[row]

    def _get_trial_name(self, row):
        return self.GetCellValue(row, 1)

    def _set_trial_name(self, row, name):
        self.SetCellValue(row, 1, name)

    def _get_marked_status(self, row):
        cell_value = self.GetCellValue(row, 0)
        if cell_value == lfs.FILE_LIST_UNMARKED_STATUS:
            return False
        else:
            return True

    def _set_marked_status(self, row, status):
        if status:
            self.SetCellValue(row, 0, lfs.FILE_LIST_MARKED_STATUS)
        else:
            self.SetCellValue(row, 0, lfs.FILE_LIST_UNMARKED_STATUS)

            
    @property
    def marked_fullpaths(self):
        result = [self._get_fullpath(row) 
                  for row in xrange(self._num_nonempty_rows)
                  if self._get_marked_status(row)]
        return result

    def _on_left_click(self, event):
        row = event.GetRow()
        col = event.GetCol()
        self._left_clicked_row = row
        if (row < self._num_nonempty_rows and 
                self._get_fullpath(row) in self._opened_files):
            fullpath = self._get_fullpath(row)
            if col == 0:
                marked = self._get_marked_status(row)
                self._set_marked_status(row, not marked)
            else: 
                self._select_row(row)

    def _on_left_dclick(self, event=None):
        row = event.GetRow()
        col = event.GetCol()
        self._row_left_dclicked = row
        if (row < self._num_nonempty_rows and 
                self._get_fullpath(row) in self._opened_files):
            fullpath = self._get_fullpath(row)
            if col != 0:
                self._rename_trial()

    def _select_row(self, row):
        fullpath = self._get_fullpath(row)
        self.SelectRow(row)
        wx.Yield()
        if fullpath != self._last_fullpath_selected:
            pub.sendMessage(topic="FILE_SELECTION_CHANGED",
                            data=fullpath)
            self._last_fullpath_selected = fullpath

