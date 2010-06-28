import os

import wx
from wx.lib.pubsub import Publisher as pub
import wx.lib.mixins.listctrl as listmix

from spikepy.gui import utils

class FileListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, **kwargs):
        """
        This list control displays what files are opened and allows users to 
            open/close files by right-click popups.
        Inputs:
            parent          : the parent panel/frame 
        Subscribes to:
            'FILE_OPENED'           : data=fullpath  will remove 'Opening' 
                                      status from Num column.
            'FILE_ALREADY_OPENED'   : data=fullpath  will remove 'Opening' 
                                      status from Num column.
            'FILE_CLOSED'           : data=fullpath  will remove file from
                                      the list.
            'OPENING_DATA_FILE'     : data=fullpath  will add file to the
                                      list with Num column set to 'Opening'.
        Publishes:
            'OPEN_FILE'             : data=self        
            'CLOSE_DATA_FILE'       : data=fullpath      
        """
        wx.ListCtrl.__init__(self, parent, **kwargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        self.InsertColumn(0, 'Num')
        self.InsertColumn(1, 'Filename')

        self.opened_files = []
        self.opening_files = []

        self.Bind(wx.EVT_CONTEXT_MENU, self._context_menu)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._item_selected)
        pub.subscribe(self._file_opened, topic='FILE_OPENED')
        pub.subscribe(self._file_opened, topic='FILE_ALREADY_OPENED')
        pub.subscribe(self._file_closed, topic='FILE_CLOSED')
        pub.subscribe(self._opening_data_file, topic='OPENING_DATA_FILE')

    def _item_selected(self, event):
        item_num = self.GetFocusedItem()
        if self.GetItemText(item_num) == 'Opening':
            self.SetItemState(item_num, 0, wx.LIST_STATE_SELECTED)
            return
        fullpath = self.opened_files[item_num]
        pub.sendMessage(topic="FILE_SELECTION_CHANGED", data=fullpath)

    def _update(self):
        self.DeleteAllItems()
        for index, file in enumerate(self.opened_files):
            path, filename = os.path.split(file)
            if file in self.opening_files:
                file_id = 'Opening'
            else:
                file_id = index
            self.InsertStringItem(index, str(file_id))
            self.SetStringItem(index, 1, filename)
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
            self._cmid_file_info  = wx.NewId()

            self.Bind(wx.EVT_MENU, self._open_file,  id=self._cmid_open_file)
            self.Bind(wx.EVT_MENU, self._close_file, id=self._cmid_close_file)

        cm = wx.Menu()
        if self.GetItemCount():
            index = self.GetFocusedItem()
            fullpath = self.opened_files[index]
            # file info item
            item = wx.MenuItem(cm, self._cmid_file_info, fullpath)
            bmp = utils.get_bitmap_icon('comment')
            item.SetBitmap(bmp)
            cm.AppendItem(item)
            cm.Enable(self._cmid_file_info, False)
        # open file item
        if self.GetItemCount():  
            item = wx.MenuItem(cm, self._cmid_open_file, 'Open Another File...')
        else:
            item = wx.MenuItem(cm, self._cmid_open_file, 'Open File')
        bmp = utils.get_bitmap_icon('folder')
        item.SetBitmap(bmp)
        cm.AppendItem(item)
        # close file item
        if self.GetSelectedItemCount() > 1:
            item = wx.MenuItem(cm, self._cmid_close_file, 'Close Files')
        else: 
            item = wx.MenuItem(cm, self._cmid_close_file, 'Close File')
        bmp = utils.get_bitmap_icon('action_stop')
        item.SetBitmap(bmp)
        cm.AppendItem(item)
        self.PopupMenu(cm)
        cm.Destroy()

    def _opening_data_file(self, message):
        fullpath = message.data
        if fullpath not in self.opened_files:
            self.opened_files.append(fullpath)
        if fullpath not in self.opening_files:
            self.opening_files.append(fullpath)
        self._update()

    def _file_opened(self, message):
        fullpath = message.data
        self.opening_files.remove(fullpath)
        self._update()

    def _file_closed(self, message):
        fullpath = message.data
        self.opened_files.remove(fullpath)
        pub.sendMessage(topic='SHOW PLOT', data='DEFAULT')
        self._update()

    def _open_file(self, event):
        pub.sendMessage(topic='OPEN_FILE', data=self)

    def _close_file(self, event):
        #if self.GetItemCount():
        #    item_num = self.GetFocusedItem()
        #    fullpath = self.opened_files[item_num]
        #    pub.sendMessage(topic='CLOSE_DATA_FILE', data=fullpath)
        files_to_close = []
        selected_item_count = self.GetSelectedItemCount()
        if selected_item_count > 0:
            item_num = self.GetFirstSelected()
            fullpath = self.opened_files[item_num]
            files_to_close.append(fullpath)
            item = 2
            while item < selected_item_count + 1:
                item_num = self.GetNextSelected(item_num)
                fullpath = self.opened_files[item_num]
                files_to_close.append(fullpath)
                item += 1

            for file in files_to_close:          
                pub.sendMessage(topic='CLOSE_DATA_FILE', data=file)

