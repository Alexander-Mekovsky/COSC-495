import wx
import wx.lib.agw.aui as aui

import util.ui as ui
import style.wx as twx

class ContentAreaPanel(wx.Panel):
    def __init__(self,parent):
        super(ContentAreaPanel, self).__init__(parent)
        self.parent = parent
        theme = parent.theme
        
        self.parent.notebook = aui.AuiNotebook(self)
        theme.Add(self, twx.GENERAL)
        self.main_sizer, box = ui.box(direction=wx.VERTICAL)
        self.main_sizer.Add(self.parent.notebook,
                          1, wx.EXPAND, 0)
        self.parent.notebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_note_book)
        
        theme.Add(self.parent.notebook, twx.GENERAL)
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