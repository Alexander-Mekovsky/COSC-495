import wx
import wx.html

import util.ui as ui
import style.wx as twx

class WelcomePanel(wx.Panel):
    def __init__(self, parent):
        super(WelcomePanel, self).__init__(parent)
        self.parent = parent

        config_path = r"C:\Users\Joshua\Documents\School\Classes\COSC-495\multiprocessing\ui\theme_config.ini"
        theme = twx.wxFormat(config_path,'high_contrast')
        
        self.themes = [theme]
        
        main_sizer, box = ui.box()
        side_center, box = ui.box()
        center_sizer, box = ui.box(direction=wx.VERTICAL)
        
        title = ui.text(self, "Welcome to API Caller!")
        theme.add_widgets(center_sizer, title, twx.TITLE, 
                          0, wx.ALIGN_LEFT | wx.ALL, 10)
        
        desc_text = "Welcome to API Caller, the ultimate tool for managing and testing your APIs effortlessly. Whether you're a developer, a tester, or simply an API enthusiast, our tool is designed to streamline your workflow, making API interaction simple and efficient."
        desc = ui.text(self, desc_text)
        theme.add_widgets(center_sizer, desc, twx.GENERAL, 
                          1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        
        header1 = ui.text(self, "Getting Started:")
        theme.add_widgets(center_sizer,header1, twx.HEADER, 
                          0, wx.ALIGN_LEFT | wx.ALL, 10)
        
        linked_list = [
                ['Create a New Project',self.parent.create_project_panel, 'Organize your APIs by creating a project where you can add and manage multiple API endpoints.'],
                ['Open an Existing Project',self.parent.open_project_dialog, 'Pick up the call where you left off.'],
                ['Explore Pre-loaded APIs',self.parent.documentation_panel, 'Learn from generated documentation of pre-loaded APIs and start sending requests in minutes.'],
            ]
        regular_list = [
                'Customize Your Requests: Easily modify headers, request body, and parameters to test different scenarios.',
                'Save Your Sessions: Keep track of your test cases and responses for future reference or regression tests.'
            ]
        
        list, list_items = ui.list(self, linked_list, regular_list)

        for item in list_items:
            if isinstance(item, wx.html.HtmlWindow):
                theme.Add(item, twx.LINK)
            else:
                theme.Add(item, twx.LIST)

        center_sizer.Add(list, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        
        side_center.Add(center_sizer, flag= wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM, border=100)
        
        main_sizer.Add(side_center,flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, border=200)
        
        theme.Add(self, twx.GENERAL)
        self.SetSizer(main_sizer)
        self.Layout()
        
        theme.apply_theme_all()
        
        self.Layout()
        self.Refresh()
        self.parent._mgr.Update()