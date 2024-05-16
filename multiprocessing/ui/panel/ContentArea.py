import wx
import wx.lib.agw.aui as aui

import util.ui as ui
import style.wx as twx

class ContentAreaPanel(wx.Panel):
    def __init__(self,parent):
        super(ContentAreaPanel, self).__init__(parent)
        self.parent = parent
        
        config_path = r"C:\Users\Joshua\Documents\School\Classes\COSC-495\multiprocessing\ui\theme_config.ini"
        theme = twx.wxFormat(config_path,'high_contrast')
        
        self.parent.notebook = aui.AuiNotebook(self)
        self.main_sizer, box = ui.box(direction=wx.VERTICAL)
        self.main_sizer.Add(self.parent.notebook,
                          1, wx.EXPAND, 0)
        self.parent.notebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_note_book)
        
        theme.Add(self, twx.GENERAL)
        theme.apply_theme_all()
        self.SetSizer(self.main_sizer)
        self.main_sizer.Layout()
        self.Layout()
        self.Refresh()

        self.parent._mgr.Update()
        
    def on_note_book(self, event):
        self.main_sizer.Layout()
        self.Layout()
        self.Refresh()