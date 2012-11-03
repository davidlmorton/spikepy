

import wx
from wx.lib.pubsub import Publisher as pub

from spikepy.common.path_utils import get_image_path

class StageCtrl(wx.Panel):
    '''
        These are the elements in a StrategySummary that the user can
    select to choose a stage.  They also have a wxChoice control to allow
    the user to select the method for this stage (optional).
    '''
    def __init__(self, parent, stage_name, stage_display_name, 
                 method_names, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self._create_images()

        self.stage_name = stage_name
        self.method_names = method_names 

        stage_text = wx.StaticText(self, label='%s' % stage_display_name)
        method_chooser = wx.Choice(self, choices=method_names)
        method_chooser.Show(bool(len(method_names)))

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        border = 3
        if wx.Platform == '__WXMSW__':
            border = 8
        flag = wx.ALIGN_CENTER_VERTICAL
        sizer.Add((15,1))
        sizer.Add(stage_text, flag=flag|wx.RIGHT|wx.BOTTOM|
                wx.LEFT|wx.ALIGN_CENTER_HORIZONTAL, 
                border=3)
        sizer.Add(method_chooser, flag=flag|wx.BOTTOM|wx.ALIGN_LEFT, 
                border=3, proportion=1)
        sizer.Add((25,1))
        self.SetSizer(sizer)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        stage_text.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        method_chooser.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_CHOICE, self.on_method_choice, method_chooser)

        self.method_chooser = method_chooser

        self.set_image_positions()

    def _create_images(self):
        right_arrow = wx.Image(get_image_path('results_icon.png'), 
                wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        ra_image = wx.StaticBitmap(self, wx.ID_ANY, right_arrow, 
                size=(right_arrow.GetWidth(), right_arrow.GetHeight()))
        self.ra_image = ra_image
        self.ra_image.Bind(wx.EVT_LEFT_DOWN, self.on_click)

        underline = wx.Image(get_image_path('underline.png'), 
                wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        un_image = wx.StaticBitmap(self, wx.ID_ANY, underline, 
                size=(underline.GetWidth(), underline.GetHeight()))
        self.un_image = un_image
        self.un_image.Bind(wx.EVT_LEFT_DOWN, self.on_click)

        left_bar = wx.Image(get_image_path('left_bar.png'), 
                wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        lb_image = wx.StaticBitmap(self, wx.ID_ANY, left_bar, 
                size=(left_bar.GetWidth(), left_bar.GetHeight()))
        self.lb_image = lb_image
        self.lb_image.Bind(wx.EVT_LEFT_DOWN, self.on_click)

    def set_image_positions(self):
        ss = self.GetSize()
        if hasattr(self, 'ss') and ss == self.ss:
            return
        else:
            self.ss = self.GetSize()

        ras = self.ra_image.GetSize()
        self.ra_image.SetPosition((ss[0]-ras[0], int((ss[1]-ras[1])/2.0)))

        uns = self.un_image.GetSize()
        self.un_image.SetPosition((0, ss[1]-uns[1]))

        lbs = self.lb_image.GetSize()
        left_bar = wx.Image(get_image_path('left_bar.png'), 
                wx.BITMAP_TYPE_PNG).Scale(lbs[0], 
                ss[1]).ConvertToBitmap()
        self.lb_image.SetBitmap(left_bar)
        self.lb_image.SetPosition((0, 0))
        self.lb_image.SetSize((left_bar.GetWidth(), left_bar.GetHeight()))

    def on_size(self, event):
        event.Skip()
        self.set_image_positions()

    def get_current_method(self):
        return self.method_chooser.GetStringSelection()

    def set_current_method(self, method_name):
        if method_name in self.method_names:
            self.method_chooser.SetStringSelection(method_name)
        else:
            raise RuntimeError("Method %s is not a valid choice for stage %s" % (method_name, self.stage_name))
        
    def on_method_choice(self, event):
        event.Skip()
        method_name = self.get_current_method()
        pub.sendMessage(topic='METHOD_CHOSEN', 
                        data=(self.stage_name, method_name))
    
    def on_click(self, event):
        event.Skip()
        pub.sendMessage(topic='STAGE_CHOSEN', 
                        data=self.stage_name)

    def show_results_icon(self, state):
        self.ra_image.Show(state)

    def show_left_bar(self, state):
        self.lb_image.Show(state)

    def show_stage_icon(self, state):
        self.un_image.Show(state)

class AuxiliaryCtrl(StageCtrl):
    def __init__(self, parent, stage_name, stage_display_name, **kwargs):
        StageCtrl.__init__(self, parent, stage_name, stage_display_name, [], 
                **kwargs)
        self.GetSizer().Add((1, 28))

    def _create_images(self):
        underline = wx.Image(get_image_path('underline.png'), 
                wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        un_image = wx.StaticBitmap(self, wx.ID_ANY, underline, 
                size=(underline.GetWidth(), underline.GetHeight()))
        self.un_image = un_image
        self.un_image.Bind(wx.EVT_LEFT_DOWN, self.on_click)

        left_bar = wx.Image(get_image_path('left_bar.png'), 
                wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        lb_image = wx.StaticBitmap(self, wx.ID_ANY, left_bar, 
                size=(left_bar.GetWidth(), left_bar.GetHeight()))
        self.lb_image = lb_image
        self.lb_image.Bind(wx.EVT_LEFT_DOWN, self.on_click)

    def set_image_positions(self):
        ss = self.GetSize()
        if hasattr(self, 'ss') and ss == self.ss:
            return
        else:
            self.ss = self.GetSize()

        uns = self.un_image.GetSize()
        self.un_image.SetPosition((0, ss[1]-uns[1]))

        lbs = self.lb_image.GetSize()
        left_bar = wx.Image(get_image_path('left_bar.png'), 
                wx.BITMAP_TYPE_PNG).Scale(lbs[0], 
                ss[1]).ConvertToBitmap()
        self.lb_image.SetBitmap(left_bar)
        self.lb_image.SetPosition((0, 0))
        self.lb_image.SetSize((left_bar.GetWidth(), left_bar.GetHeight()))

    def show_results_icon(self, state):
        pass

