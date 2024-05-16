import wx
import wx.lib.agw.aui as aui
import configparser

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame(None, title="Welcome", size=(1024, 768))
        self.frame.Show()
        return True

class MainFrame(wx.Frame):
    def __init__(self, parent, title, size):
        super(MainFrame, self).__init__(parent, title=title, size=size)
        self.init_ui()
        
    def init_ui(self):
        # Load theme
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8')
        self.current_theme = self.load_theme(self.config.get('User', 'theme', fallback='Dark'))
        self.apply_theme(self.current_theme)

        # Initialize the AuiManager
        self._mgr = aui.AuiManager(self)
        
        # Menu bar
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_ANY, "Create New Project", "Create a new project")
        file_menu.Append(wx.ID_ANY, "Open Existing Project", "Open an existing project")
        file_menu.Append(wx.ID_ANY, "Preferences", "Adjust preferences")
        file_menu.Append(wx.ID_EXIT, "Exit", "Exit application")
        menubar.Append(file_menu, '&File')
        self.SetMenuBar(menubar)

        # Status bar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("Ready...")

        # Adding a dockable pane
        text_panel = wx.TextCtrl(self, style=wx.NO_BORDER | wx.TE_MULTILINE)
        self._mgr.AddPane(text_panel, aui.AuiPaneInfo().
                          Caption("Editable Text").
                          Floatable(True).Dockable(True).
                          CloseButton(True).MaximizeButton(True).
                          BestSize(wx.Size(300, 200)).
                          Left().Layer(1).Position(1))

        # Update the manager
        self._mgr.Update()

    def load_theme(self, theme_name):
        theme = {
            'bg': self.config[theme_name]['background'],
            'fg': self.config[theme_name]['foreground'],
            'button_bg': self.config[theme_name]['button_background'],
            'button_fg': self.config[theme_name]['button_foreground']
        }
        return theme

    def apply_theme(self, theme):
        self.SetBackgroundColour(theme['bg'])

    def open_new_window(self):
        new_frame = wx.Frame(None, title="Additional Window", size=(400, 300))
        new_frame.Show()

    def exit_app(self, event):
        self._mgr.UnInit()  # Uninitialize the AuiManager
        self.Close(True)

if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
