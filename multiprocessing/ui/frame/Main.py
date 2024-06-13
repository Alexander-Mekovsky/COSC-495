import wx
import wx.lib.agw.aui as aui
import os

import style.wx as twx

# Add imports for specific panels here
import panel.Welcome as wlc
import panel.CreateProject as cpp
import panel.Documentation as dcp
import panel.FileExplorer as fep
import panel.Requests as rqp
import panel.ContentArea as cap

WELCOME = 'welcome'
CREATE_PROJ = 'create_project'
DOCUMENTATION = 'documentation'
SETTINGS = 'settings'
FILE_EXPLORER = 'file_explorer'
CONTENT_AREA = 'content_area'
REQUESTS = 'requests'

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title, size=(1024, 768))
        
        config_path = r"C:\Users\Joshua\Documents\School\Classes\COSC-495\multiprocessing\ui\theme_config.ini"
        self.theme = twx.wxFormat(config_path,'high_contrast')
        
        self._mgr = aui.AuiManager(self)
        self.hidden_panes = {}
        self.project_path = os.getcwd()
        
        self.menu_bar()
        
        self.defaultDirs = ['config', 'tmp', 'data']
        self.defaultFiles = ['config\\config.ini']
        
        self.welcome_panel()
        
        self.status_bar()
        self._mgr.Bind(aui.EVT_AUI_PANE_CLOSE, self.on_pane_close)
        self._mgr.Update()
        
    def menu_bar(self):
        menu_bar = wx.MenuBar()
        
        file_menu = wx.Menu()
        
        # Append 'Open Project' item
        open_project_item = file_menu.Append(wx.NewIdRef(), 'Open Project', 'Open an existing project')
        self.Bind(wx.EVT_MENU, self.open_project_dialog, open_project_item)

        # Append 'Create New Project' item
        create_project_item = file_menu.Append(wx.NewIdRef(), 'Create New Project', 'Create a new project')
        self.Bind(wx.EVT_MENU, self.create_project_panel, create_project_item)

        # Append 'API Documentation' item
        api_doc_item = file_menu.Append(wx.NewIdRef(), 'API Documentation', 'View API documentation')
        self.Bind(wx.EVT_MENU, self.documentation_panel, api_doc_item)

        # Append 'Settings' item
        settings_item = file_menu.Append(wx.NewIdRef(), 'Settings', 'Adjust application settings')
        self.Bind(wx.EVT_MENU, self.settings_panel, settings_item)

        exit_item = file_menu.Append(wx.ID_EXIT, 'Exit', 'Exit application')
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)

        menu_bar.Append(file_menu, '&File')
        
        view_menu = wx.Menu()
    
        # Adding "File Explorer" menu item (checkable)
        self.file_explorer_item = view_menu.AppendCheckItem(wx.NewIdRef(), 'File Explorer', 'Toggle file explorer view')
        self.Bind(wx.EVT_MENU, self.on_toggle_file_explorer, self.file_explorer_item)

        # Adding "Open" menu item (checkable)
        self.open_item = view_menu.AppendCheckItem(wx.NewIdRef(), 'Open Files', 'Toggle open file view')
        self.Bind(wx.EVT_MENU, self.on_toggle_open_file, self.open_item)

        # Adding "Requests Toolbar" menu item (checkable)
        self.requests_toolbar_item = view_menu.AppendCheckItem(wx.NewIdRef(), 'Requests Toolbar', 'Toggle requests toolbar view')
        self.Bind(wx.EVT_MENU, self.on_toggle_requests_toolbar, self.requests_toolbar_item)
        self.view_items = {
            FILE_EXPLORER:self.file_explorer_item,
            CONTENT_AREA:self.open_item,
            REQUESTS:self.requests_toolbar_item
        }
        menu_bar.Append(view_menu, '&View')

        self.SetMenuBar(menu_bar)
        
    def status_bar(self):
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Ready")
    
    def frame_pane_exists(self, name):
        return self._mgr.GetPane(name).IsOk()
    
    def hide_all_panes(self):
        """Hides all panes."""
        all_panes = self._mgr.GetAllPanes()
        for pane in all_panes:
            pane.Hide()
        self._mgr.Update()
        
    def show_all_panes(self):
        """Shows all panes."""
        all_panes = self._mgr.GetAllPanes()
        for pane in all_panes:
            pane.Show()
        self._mgr.Update()
    
    def close_all_panes(self):
        """Close all panes."""
        all_panes = self._mgr.GetAllPanes()
        for pane in all_panes:
            self._mgr.ClosePane(pane)
            self._mgr.DetachPane(pane.window)
        self._mgr.Update()
    
    def on_exit(self, event):
        """Close the frame, terminating the application."""
        self.close_all_panes()
        self.Close(True)
        
    def on_toggle_file_explorer(self, event):
        if not self.frame_pane_exists("file_explorer"):
            self.add_file_explorer_panel(self.project_path)
        else:
            pane = self._mgr.GetPane("file_explorer")
            pane.Show(event.IsChecked())
        self._mgr.Update()

    def on_toggle_open_file(self, event):
        if not self.frame_pane_exists("content_area"):
            self.add_content_area_panel()
        else:
            pane = self._mgr.GetPane("content_area")
            pane.Show(event.IsChecked())
        self._mgr.Update()

    def on_toggle_requests_toolbar(self, event):
        if not self.frame_pane_exists("requests"):
            self.add_requests_panel(self.project_path)
        else:
            pane = self._mgr.GetPane("requests")
            pane.Show(event.IsChecked())
        self._mgr.Update()
        
    def add_file_explorer_panel(self, project_path):
        if not self.frame_pane_exists(FILE_EXPLORER):
            self.file_explorer_panel = fep.FileExplorerPanel(self, project_path)
            self._mgr.AddPane(self.file_explorer_panel, aui.AuiPaneInfo().Name(FILE_EXPLORER).Left().Caption("Project Files"))
            self.file_explorer_item.Check(True)
            self._mgr.Update()

    def add_content_area_panel(self):
        if not self.frame_pane_exists(CONTENT_AREA):
            self.content_area_panel = cap.ContentAreaPanel(self)
            self._mgr.AddPane(self.content_area_panel, aui.AuiPaneInfo().Name(CONTENT_AREA).Center().Caption("Open Files"))
            self.open_item.Check(True)
            self._mgr.Update()

    def add_requests_panel(self, project_path):
        if not self.frame_pane_exists(REQUESTS):
            third_height = (self.GetSize().GetHeight() // 5) * 2
            min_height = self.status_bar.GetSize().GetHeight()
            self.requests_panel = rqp.RequestsPanel(self, project_path)
            self._mgr.AddPane(self.requests_panel, aui.AuiPaneInfo().Name(REQUESTS).Bottom().BestSize(-1, third_height).MinSize(-1, min_height).Caption("Tools"))
            self.requests_toolbar_item.Check(True)
            self._mgr.Update()
    
    def welcome_panel(self):
        self.welcome_panel = wlc.WelcomePanel(self)
        self._mgr.AddPane(self.welcome_panel, aui.AuiPaneInfo().Name(WELCOME).CenterPane())
    
    def create_project_panel(self, event):
        self.hide_all_panes()
        self._create_project_panel = cpp.CreateProjectPanel(self)
        if not self.frame_pane_exists(CREATE_PROJ):
            self._mgr.AddPane(self._create_project_panel, aui.AuiPaneInfo().Name(CREATE_PROJ).CenterPane().Caption("Create New Project"))
        self._mgr.Update()
    
    def check_defaults(self, path):
        import os
        # Check if default directories exist
        dirs_exist = all(os.path.isdir(os.path.join(path, d)) for d in self.defaultDirs)
        # Check if default files exist
        files_exist = all(os.path.isfile(os.path.join(path, f)) for f in self.defaultFiles)
        return dirs_exist and files_exist
    
    def open_project_dialog(self, event):
        with wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_OK:
                selected_path = dirDialog.GetPath()
                if self.check_defaults(selected_path):
                    # Continue with further processing
                    wx.MessageBox('All required directories and files are present.', 'Check Complete', wx.OK | wx.ICON_INFORMATION)
                    self.project_panel(selected_path)
                else:
                    # Show warning dialog to override
                    if wx.MessageBox('Some directories or files are missing. Do you want to continue anyway?', 
                                     'Warning', wx.YES_NO | wx.ICON_WARNING) == wx.YES:
                        # User chose to override the warning
                        # Continue with further processing
                        wx.MessageBox('Continuing despite missing elements.', 'Continued', wx.OK | wx.ICON_INFORMATION)

                        if self.frame_pane_exists(WELCOME):
                            self._mgr.ClosePane(self._mgr.GetPane(WELCOME))

                        self.project_panel(selected_path)

    def documentation_panel(self, event):
        self.hide_all_panes()
    
        self._documentation_panel = dcp.DocumentationPanel(self)
        if not self.frame_pane_exists(DOCUMENTATION):
            self._mgr.AddPane(self._documentation_panel, aui.AuiPaneInfo().Name(DOCUMENTATION).CenterPane())
        self._mgr.Update()
    
    def settings_panel(self, event):
        pass
    
    def project_panel(self, path):
        self.close_all_panes()
        self.project_path = path
        self.add_file_explorer_panel(path)
        self.add_content_area_panel()
        self.add_requests_panel(path)
    
    def on_pane_close(self, event):
        pane = event.GetPane()
        for name, item in self.view_items.items():
            if pane.name == name:
                item.Check(False)
                event.Skip()
                return
        event.Skip()
        self.show_all_panes()