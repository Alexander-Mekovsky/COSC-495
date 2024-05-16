import wx
import frame.Main as mf

class MyApp(wx.App):
    def OnInit(self):
        self.frame = mf.MainFrame(None, title="API Caller")
        self.frame.Show()
        return True
    
if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()