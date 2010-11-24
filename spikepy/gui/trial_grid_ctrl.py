import os

import wx.grid as gridlib
from wx.lib.pubsub import Publisher as pub
from spikepy.gui import utils
from .look_and_feel_settings import lfs
import wx

from . import program_text as pt

class TrialGridCtrl(gridlib.Grid):
    def __init__(self, parent, **kwargs):
        self.parent = parent
        gridlib.Grid.__init__(self, parent, **kwargs)

        self._num_empty_rows = 8
        self.CreateGrid(self._num_empty_rows, 2)
        # ---- col settings -----
        attr0 = gridlib.GridCellAttr()
        #                    horizontal       vertical
        attr0.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER) 
        if wx.Platform == '__WXMAC__':
            font_point_size = 20
        else:
            font_point_size = 15
        font = wx.Font(font_point_size, wx.FONTFAMILY_SWISS, 
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

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
        # set it up so that selections select the whole row
        self.SetSelectionMode(self.wxGridSelectRows)
        self.EnableGridLines(False)
        self.DisableDragRowSize()
        self.DisableDragColSize()
        self._last_trial_id_selected = None
        self.SetGridCursor(0, 4)
        self.SetRowLabelSize(0)
        self._autosize_cols()
        
        pub.subscribe(self._trial_added, topic='TRIAL_ADDED')
        pub.subscribe(self._trial_closed, topic='TRIAL_CLOSED')
        pub.subscribe(self._trial_renamed, topic='TRIAL_RENAMED')

        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self._on_left_click)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self._on_left_dclick)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self._on_right_click)
        self.Bind(wx.EVT_SIZE, self._ensure_fills_space)

        self._trial_ids = []

    # --- UTILITIES ---
    def _autosize_cols(self):
        self.AutoSizeColumns()
        self._min_column_sizes=(self.GetColSize(0), self.GetColSize(1))
        self._ensure_fills_space()

    def _set_row_backround_color(self, row, color):
        for col in xrange(self.GetNumberCols()):
            self.SetCellBackgroundColour(row, col, color)

    def _select_row(self, row):
        trial_id = self._get_trial_id_from_row(row)
        self.SelectRow(row)
        wx.Yield()
        if trial_id != self._last_trial_id_selected:
            pub.sendMessage(topic="TRIAL_SELECTION_CHANGED",
                            data=trial_id)
            self._last_trial_id_selected = trial_id

    def MakeCellVisible(self):
        pass # don't scroll to where the cursor is
            
    # --- GET/SETTERS
    def _get_row_from_trial_id(self, trial_id):
        for row in xrange(self._num_nonempty_rows):
            trial_id_from_row = self._get_trial_id_from_row(row)
            if trial_id == trial_id_from_row:
                return row

    def _get_trial_id_from_row(self, row):
        return self._trial_ids[row]

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
        pub.sendMessage(topic='TRIAL_MARKS_CHANGED', data=None)

    @property
    def _num_nonempty_rows(self):
        return self.GetNumberRows() - self._num_empty_rows
        
    @property
    def marked_trial_ids(self):
        result = [self._get_trial_id_from_row(row) 
                  for row in xrange(self._num_nonempty_rows)
                  if self._get_marked_status(row)]
        return result

    # --- EVENT HANDLERS ---
    def _ensure_fills_space(self, event=None):
        if event is not None:
            event.Skip()
        marked_col_size = self.GetColSize(0)
        trial_name_col_size = self.GetColSize(1)
        used_size = marked_col_size + trial_name_col_size
        panel_width, panel_height = self.GetSize()
        fill_size = trial_name_col_size + panel_width - used_size - 30
        self.SetColSize(1, max(fill_size, self._min_column_sizes[1]))

    def _open_file(self, event):
        pub.sendMessage(topic='OPEN_OPEN_FILE_DIALOG', data=self)

    def _close_marked_trials(self, event=None):
        for trial_id in self.marked_trial_ids:
            pub.sendMessage(topic='CLOSE_TRIAL', 
                            data=trial_id)

    def _close_this_trial(self, event=None):
        row = self._row_right_clicked
        trial_id = self._get_trial_id_from_row(row)
        pub.sendMessage(topic='CLOSE_TRIAL',
                        data=trial_id)

    def _on_left_click(self, event):
        row = event.GetRow()
        col = event.GetCol()
        if (row < self._num_nonempty_rows and 
                self._get_trial_id_from_row(row) in self._trial_ids):
            trial_id = self._get_trial_id_from_row(row)
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
                self._get_trial_id_from_row(row) in self._trial_ids):
            trial_id = self._get_trial_id_from_row(row)
            if col != 0:
                self._rename_trial()

    def _on_right_click(self, event):
        row = event.GetRow()
        self._row_right_clicked = row
        if not hasattr(self, '_cmid_open_file'):
            self._cmid_open_file  = wx.NewId()
            self._cmid_rename_trial = wx.NewId()
            self._cmid_close_marked_trials = wx.NewId()
            self._cmid_close_this_trial = wx.NewId()

            self.Bind(wx.EVT_MENU, self._rename_trial, 
                                   id=self._cmid_rename_trial)
            self.Bind(wx.EVT_MENU, self._open_file,  id=self._cmid_open_file)
            self.Bind(wx.EVT_MENU, self._close_marked_trials, 
                                   id=self._cmid_close_marked_trials)
            self.Bind(wx.EVT_MENU, self._close_this_trial, 
                                   id=self._cmid_close_this_trial)

        cm = wx.Menu()
        if self._num_nonempty_rows:
            row = event.GetRow()

        if row < self._num_nonempty_rows:
            trial_name = self._get_trial_name(row)
            trial_id = self._get_trial_id_from_row(row)

        # open file item
        if self._num_nonempty_rows:
            item = wx.MenuItem(cm, self._cmid_open_file, pt.OPEN_ANOTHER_FILE)
        else:
            item = wx.MenuItem(cm, self._cmid_open_file, pt.OPEN)
        cm.AppendItem(item)

        # rename_trial item
        if row >= self._num_nonempty_rows:
            item = wx.MenuItem(cm, self._cmid_rename_trial, pt.RENAME_TRIAL)
        else:
            item = wx.MenuItem(cm, self._cmid_rename_trial, pt.RENAME_TRIAL+
                               ' (%s)' % trial_name)
        cm.AppendItem(item)
        if row >= self._num_nonempty_rows:
            cm.Enable(self._cmid_rename_trial, False)

        # close this trial item
        if row < self._num_nonempty_rows and trial_id in self._trial_ids:
            item = wx.MenuItem(cm, self._cmid_close_this_trial, 
                               pt.CLOSE_THIS_TRIAL+' (%s)' % trial_name)
        else:
            item = wx.MenuItem(cm, self._cmid_close_this_trial, 
                               pt.CLOSE_THIS_TRIAL)
        cm.AppendItem(item)
        if row >= self._num_nonempty_rows:
            cm.Enable(self._cmid_close_this_trial, False)

        # close marked trials item
        item = wx.MenuItem(cm, self._cmid_close_marked_trials, 
                               pt.CLOSE_MARKED_TRIALS)
        cm.AppendItem(item)
        if not self.marked_trial_ids:
            cm.Enable(self._cmid_close_marked_trials, False)

        self.PopupMenu(cm)
        cm.Destroy()

    def _rename_trial(self, event=None):
        if event is not None: # came in through menu
            row = self._row_right_clicked
        else:
            row = self._row_left_dclicked
        trial_id = self._get_trial_id_from_row(row)
        pub.sendMessage(topic='OPEN_RENAME_TRIAL_DIALOG', data=trial_id)

    # --- MESSAGE HANDLERS ---
    def _trial_closed(self, message):
        trial_id = message.data
        row = self._get_row_from_trial_id(trial_id)
        self.DeleteRows(pos=row)
        self.AppendRows()
        self._num_empty_rows += 1
        self._trial_ids.remove(trial_id)

    def _trial_added(self, message):
        trial = message.data
        trial_name = trial.display_name
            
        new_row = self._num_nonempty_rows
        self._trial_ids.append(trial.trial_id)
        self._set_trial_name(new_row, trial_name)
        self._set_marked_status(new_row, False)

        self._autosize_cols()
        if self._num_empty_rows > 1:
            self._num_empty_rows -= 1
        else:
            self.AppendRows()
        assert len(self._trial_ids) == self._num_nonempty_rows

    def _trial_renamed(self, message):
        trial = message.data
        trial_id = trial.trial_id
        new_name = trial.display_name
        row = self._get_row_from_trial_id(trial_id)
        self._set_trial_name(row, new_name)

