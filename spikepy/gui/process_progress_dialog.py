"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import Queue

import wx
from wx.lib.pubsub import Publisher as pub
import wx.grid as gridlib

from spikepy.common.config_manager import config_manager as config
from spikepy.common import program_text as pt

stages = ['detection_filter', 'detection', 'extraction_filter', 
          'extraciton', 'clustering']

class ProcessProgressDialog(wx.Dialog):
    def __init__(self, parent, trial_list, message_queue, abort_queue, 
                       **kwargs):
        if 'style' not in kwargs.keys():
            kwargs['style'] = wx.STAY_ON_TOP
        kwargs['style'] |= wx.RESIZE_BORDER
        kwargs['style'] |= wx.CAPTION
        kwargs['style'] |= wx.SYSTEM_MENU

        kwargs['title'] = pt.PROCESS_PROGRESS

        wx.Dialog.__init__(self, parent, **kwargs)

        self.message_queue = message_queue
        self.abort_queue = abort_queue
        self.update_period = 117 # in ms

        info_text = wx.StaticText(self, label=pt.STRATEGY_PROGRESS_INFO)

        self.gauge = wx.Gauge(self, wx.ID_ANY, 100, 
                              size=(350,20), style=wx.GA_HORIZONTAL)
        self.processing_text = wx.StaticText(self)
        self.abort_button = wx.Button(self, label=pt.ABORT)
        self.process_grid = ProcessGrid(self, trial_list)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(info_text, proportion=0, 
                  flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        sizer.Add(self.processing_text, proportion=0, 
                  flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        sizer.Add(self.gauge, proportion=0, flag=wx.ALL|wx.EXPAND, border=8)
        sizer.Add(self.abort_button, proportion=0, flag=wx.ALL|wx.ALIGN_RIGHT,
                  border=6)
        sizer.Add(self.process_grid, flag=wx.ALL|wx.EXPAND, border=20)
        # ADD A GRID UNDER "SHOW DETAILS"

        self.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_BUTTON, self._abort, self.abort_button)
        self.Bind(wx.EVT_IDLE, self._update_processing)
        self._reset_should_update()

    def _reset_should_update(self):
        self._should_update = True

    def _update_processing(self, event):
        if self._should_update:
            self._should_update = False
            wx.CallLater(self.update_period, self._reset_should_update)
            new_message = None
            try:
                new_message = self.message_queue.get(False)
            except Queue.Empty:
                pass
            if new_message is not None:
                statement, data = new_message
                if statement == 'JOB_CREATED':
                    new_job = data
                    self.process_grid.add_job(new_job)
                if statement == 'all processes ended':
                    pass
                if statement == 'finished':
                    pass
                if statement == 'JOB_STARTED':
                    started_job = data
                    self.process_grid.start_job(started_job)
            self.process_grid.update_run_times()

    def _abort(self, event):
        self.abort_queue.put(True)
        self.abort_button.Enable(False)

    def close(self):
        self.Show(False)
        self.Destroy()

class ProcessGrid(gridlib.Grid):
    def __init__(self, parent, trial_list, *args, **kwargs):
        gridlib.Grid.__init__(self, parent, *args, **kwargs)
        self.trial_list = trial_list

        self.trial_index = {}
        self.trial_name_index = {}
        for trial in trial_list:
            self.trial_index[trial.trial_id] = trial
            self.trial_name_index[trial.trial_id] = trial.display_name

        self.CreateGrid(0, len(stages))
        for i, stage in enumerate(stages):
            self.SetColLabelValue(i, stage)

        self.SetRowLabelSize(250)
        self.SetColLabelAlignment(wx.LEFT, wx.CENTER)
        self.SetColLabelTextOrientation(wx.VERTICAL)
        self.SetColLabelSize(150)
        self.SetDefaultColSize(85)

        self.SetDefaultCellBackgroundColour(wx.CYAN)
        self.update_row_index()
        self.update_col_index()
        self._jobs_index = {}
        self._running_jobs_index = {}

    def update_run_times(self):
        for job in self._running_jobs_index.values():
            cells = self.get_cells_for_job(job)
            run_time = job.get_run_time_as_string()
            for cell in cells:
                self.SetCellValue(cell[0], cell[1], run_time)

    def get_cells_for_job(self, job):
        col_name = job.job_name
        col = self._col_index[col_name]
        cells = []
        for trial_id in job.trial_ids:
            trial_name = self.trial_name_index[trial_id]
            row = self._row_index[trial_name]
            cells.append((row, col))
        return cells

    def start_job(self, job):
        self._running_jobs_index[job.job_id] = job
        cells = self.get_cells_for_job(job)
        for cell in cells:
            self.SetAttr(cell[0], cell[1], self.running_cell_attr)

    def add_job(self, job):
        self._jobs_index[job.job_id] = job

        # add new row(s)
        trial_ids = job.trial_ids
        for trial_id in trial_ids:
            trial = self.trial_index[trial_id]
            trial_name = trial.display_name
            if trial_name not in self._row_index.keys():
                new_row_pos = len(self._row_index.keys())
                self.InsertRows(pos=new_row_pos)
                self.SetRowLabelValue(new_row_pos, trial_name)
        self.update_row_index()

        # add new col
        new_col_name = job.job_name
        if new_col_name not in self._col_index.keys():
            new_col_pos = self._col_index[job.stage_name]+1
            self.InsertCols(pos=new_col_pos)
            self.SetColLabel(new_col_pos, new_col_name)
            self.update_col_index()

        # set new cells to pending attr.
        for trial_id in trial_ids:
            trial_name = trial.display_name
            row = self._row_index[trial_name]
            col = self._col_index[new_col_name]
            self.SetAttr(row, col, self.pending_cell_attr)

        self.relayout()

    def relayout(self):
        self.Layout()
        parent = self.GetParent()
        parent.Layout()
        parent.Fit()
        
    @property
    def pending_cell_attr(self):
        if not hasattr(self, '_pending_cell_attr'):
            attr = gridlib.GridCellAttr()
            attr.SetTextColour(wx.WHITE)
            attr.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
            attr.SetBackgroundColour(wx.BLUE)
            self._pending_cell_attr = attr
        return self._pending_cell_attr

    @property
    def running_cell_attr(self):
        if not hasattr(self, '_running_cell_attr'):
            attr = gridlib.GridCellAttr()
            attr.SetTextColour(wx.WHITE)
            attr.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
            attr.SetBackgroundColour(wx.RED)
            self._running_cell_attr = attr
        return self._running_cell_attr

    @property
    def default_cell_attr(self):
        if not hasattr(self, '_default_cell_attr'):
            attr = gridlib.GridCellAttr()
            attr.SetTextColour(wx.BLACK)
            attr.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
            attr.SetBackgroundColour(wx.CYAN)
            self._default_cell_attr = attr
        return self._default_cell_attr

    def update_row_index(self):
        self._row_index = {}
        for row in range(self.GetNumberRows()):
            row_label = self.GetRowLabelValue(row)
            self._row_index[row_label] = row

    def update_col_index(self):
        self._col_index = {}
        for col in range(self.GetNumberCols()):
            col_label = self.GetColLabelValue(col)
            self._col_index[col_label] = col
        

