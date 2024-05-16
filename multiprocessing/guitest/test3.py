import wx
import wx.lib.agw.aui as aui
import wx.adv
import configparser
import csv
import os

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame(None, title="Project Setup")
        self.frame.Show()
        return True

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title, size=(1024, 768))
        self._mgr = aui.AuiManager(self)
        self.file_paths = {}
        
        # Initialize panels
        self.init_welcome_panel()
        self._mgr.Update()

    def init_welcome_panel(self):
        # This will hold the Welcome screen
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        hyperlink1 = wx.adv.HyperlinkCtrl(panel, id=wx.ID_ANY, label="Create New Project", url="",
                                           pos=(20, 60))
        hyperlink1.Bind(wx.adv.EVT_HYPERLINK, self.on_hyperlink_create_project)
        sizer.Add(hyperlink1, 0, wx.ALL, 5)
        
        hyperlink2 = wx.adv.HyperlinkCtrl(panel, id=wx.ID_ANY, label="Open Existing Project", url="",
                                           pos=(20, 100))
        # hyperlink2.Bind(wx.adv.EVT_HYPERLINK, self.on_open_project)
        sizer.Add(hyperlink2, 0, wx.ALL, 5)
        
        panel.SetSizer(sizer)
        
        self._mgr.AddPane(panel, aui.AuiPaneInfo().Name("welcome").CenterPane())
    
    def on_hyperlink_create_project(self, event):
        # This method should only handle switching to the create project panel
        self._mgr.ClosePane(self._mgr.GetPane("welcome"))
        self.init_create_project_panel()
        self._mgr.Update()


    def init_create_project_panel(self):
        import quickui as qu
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(main_sizer)
        # Top padding
        main_sizer.Add((-1, 10))  # Add some space at the top
    
        # Centered content sizer
        center_sizer = qu.box(direction='vert')
        title_box = qu.box(direction='vert')
        
        title_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title = wx.StaticText(panel, label='Create New Project')
        title.SetFont(title_font)
        title_box.Add(title, flag=wx.ALIGN_LEFT | wx.ALL, border=10)

        # Set up the description
        desc_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_LIGHT)
        description = "Configure and initiate a new project designed for API interaction. In this context, a 'project' is a unique configuration comprising specific API connections, logging preferences, and other adjustable settings that are uniquely identified by a project name. This framework allows for efficient management of various API configurations and requests, each organized into distinct projects. Such organization facilitates streamlined API testing, effective data retrieval, and seamless integration with other applications, enhancing overall workflow and productivity."
        self.desc = wx.StaticText(panel, label=description)
        title_box.Add(self.desc, proportion=1,flag=wx.ALIGN_LEFT | wx.ALL, border=10)
        center_sizer.Add(title_box, proportion=2, flag=wx.ALIGN_LEFT | wx.ALL, border=10)
        
        # Project Information Group
        proj_info_sizer = qu.box(panel, True,"Project Information",'vert')
        
        # Project Name
        proj_name_sizer, proj_name_label, self.proj_name = qu.editcombo(panel,"Project Name:")
        proj_info_sizer.Add(proj_name_sizer, flag=wx.EXPAND | wx.ALL, border=10)
    
        # Location with file dialog
        proj_loc_sizer, proj_loc_label, self.proj_loc = qu.browsecombo(panel,self.on_browse_location,"Location:")
        proj_info_sizer.Add(proj_loc_sizer, flag=wx.EXPAND | wx.ALL, border=10)
    
        center_sizer.Add(proj_info_sizer,proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
    
        # API Selection
        proj_api_sizer = qu.box(panel,True,"API Information",'vert')

        self.Bind(wx.EVT_RADIOBUTTON, self.on_radio_button_toggle)
        
        # Existing API Radio Button
        e_api_sizer = qu.box(direction='vert')
        
        self.e_api_rb = wx.RadioButton(panel, label='Use an existing API:', style=wx.RB_GROUP)
        e_api_sizer.Add(self.e_api_rb, proportion=1,flag=wx.EXPAND | wx.ALL, border=10)

        # Primary API Selection ComboBox
        e_prim_api_sizer, self.e_prim_api_label, self.e_prim_api, self.e_prim_api_desc = qu.dropcombo(panel,self.load_apis,self.on_api_selection_changed, "Select Primary API:") 
        e_api_sizer.Add(e_prim_api_sizer, proportion=1,flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=10)
        e_api_sizer.Add(self.e_prim_api_desc, proportion=1,flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        
        e_api_key_sizer, self.e_api_key_label, self.e_api_key = qu.editcombo(panel,"API Key:")
        e_api_sizer.Add(e_api_key_sizer, proportion=1,flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=20)
        
        proj_api_sizer.Add(e_api_sizer,flag=wx.EXPAND | wx.ALL, border=5)

        # New API Radio Button
        n_api_sizer = qu.box(direction='vert')
        self.n_api_rb = wx.RadioButton(panel, label='Load a new API:')
        n_api_sizer.Add(self.n_api_rb, flag=wx.EXPAND | wx.ALL, border=10)
        
        n_prim_api_sizer, self.n_prim_api_label, self.n_prim_api = qu.editcombo(panel,"API Name:")
        n_api_sizer.Add(n_prim_api_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        
        n_api_desc_sizer, self.n_api_desc_label, self.n_api_desc = qu.editcombo(panel, "Description:")
        n_api_sizer.Add(n_api_desc_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border=10)
        
        n_api_key_sizer, self.n_api_key_label, self.n_api_key = qu.editcombo(panel, "API Key:")
        n_api_sizer.Add(n_api_key_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        
        proj_api_sizer.Add(n_api_sizer,flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=0)
        
        api_note = qu.note(panel,"Note: You will be able to change API and select secondary APIs at a later time.")
        proj_api_sizer.Add(api_note, flag=wx.TE_READONLY | wx.TOP,border = 10)
        center_sizer.Add(proj_api_sizer,proportion=4, flag=wx.EXPAND | wx.ALL, border=10)
        
        # Initial existing api ui setup
        self.e_api_rb.SetValue(True)
        self.e_prim_api_desc.Hide()
        self.e_api_key_label.Hide()
        self.e_api_key.Hide()
        
        # Initial new api ui setup 
        self.n_api_rb.SetValue(False)
        self.n_prim_api_label.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
        self.n_prim_api.Disable()
        self.n_api_key_label.Hide()
        self.n_api_key.Hide()
        self.n_api_desc_label.Hide()
        self.n_api_desc.Hide()
        
        # Logging Option
        logging_sizer = qu.box(panel,True,"Logging Information",direction='vert')
        tog_log_sizer = qu.box()
        tog_log_label = wx.StaticText(panel, label='Enable Logging?')
        tog_log_sizer.Add(tog_log_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)
        
        self.tog_log_on_rb = wx.RadioButton(panel, label='Yes', style=wx.RB_GROUP)
        tog_log_off_rb = wx.RadioButton(panel, label='No')
        tog_log_sizer.Add(self.tog_log_on_rb, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=10)
        tog_log_sizer.Add(tog_log_off_rb, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=10)
        
        logging_sizer.Add(tog_log_sizer,flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=0)
        center_sizer.Add(logging_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        
        # Initial logging ui setup
        self.tog_log_on_rb.SetValue(True)
        tog_log_off_rb.SetValue(False)

        # Action Buttons
        action_buttons_hbox = wx.BoxSizer(wx.HORIZONTAL)
        cancel_button = wx.Button(panel, label='Cancel')
        cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
        action_buttons_hbox.Add(cancel_button, flag=wx.RIGHT, border=8)
        create_button = wx.Button(panel, label='Create')
        create_button.Bind(wx.EVT_BUTTON, self.on_create_project)
        action_buttons_hbox.Add(create_button, flag=wx.RIGHT, border=8)
        center_sizer.Add(action_buttons_hbox, flag=wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.RIGHT, border=10)
        
        main_sizer.Add(center_sizer, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=100)  # Adjust border size for horizontal padding
    
        panel.SetSizer(main_sizer)
        panel.Layout()
        wrap_width = center_sizer.GetSize()[0] - 20  # Adjust the subtraction for actual margins
        
        self.desc.Wrap(wrap_width)
        panel.Layout()
        
        self._mgr.AddPane(panel, aui.AuiPaneInfo().Name("create_project").CenterPane().Caption("Create New Project"))
        self._mgr.Update()

    def on_radio_button_toggle(self, event):
        # Enable or disable fields based on the selected radio button
        if self.n_api_rb.GetValue():
            self.e_prim_api_label.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
            self.e_prim_api.Disable()
            self.e_prim_api_desc.Hide()
            self.e_api_key_label.Hide()
            self.e_api_key.Hide()
            
            self.n_prim_api_label.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
            self.n_prim_api.Enable()
            self.n_api_key_label.Show()
            self.n_api_key.Show()
            self.n_api_desc_label.Show()
            self.n_api_desc.Show()
            
        elif self.e_api_rb.GetValue():
            self.n_prim_api_label.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
            self.n_prim_api.Disable()
            self.n_api_key_label.Hide()
            self.n_api_key.Hide()
            self.n_api_desc_label.Hide()
            self.n_api_desc.Hide()

            self.e_prim_api_label.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
            self.e_prim_api.Enable()
            if self.e_prim_api.GetValue() != "":
                self.e_prim_api_desc.Show()
                self.e_api_key_label.Show()
                self.e_api_key.Show()
        self._mgr.Update()

    def load_apis(self,loadstruct):
        # Load API data from CSV
        with open('../api/allowedAPI.csv', mode='r') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                loadstruct.Append(row['API'], row)  # Append the API name and store the entire row as client data

    def on_api_selection_changed(self, event):
        selection = self.e_prim_api.GetSelection()
        if selection != wx.NOT_FOUND:
            api_data = self.e_prim_api.GetClientData(selection)
            description = api_data.get('Description', '').strip()
            if description:
                self.e_prim_api_desc.SetLabel(f"Description: {description}")
                self.e_prim_api_desc.Show()  # Show the control
                self.e_api_key_label.Show()
                self.e_api_key.Show()
            else:
                self.e_prim_api_desc.Hide()  # Hide if no description
            self._mgr.Update()

    def on_browse_location(self, event):
        # Open a directory dialog
        with wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_OK:
                self.proj_loc.SetValue(dirDialog.GetPath())

    def on_cancel(self, event):
        if self._mgr.GetPane("create_project").IsOk():
            self._mgr.ClosePane(self._mgr.GetPane("create_project"))
        self._mgr.Update()

    def on_create_project(self, event):
        import re
        import file as ps
        project_name = self.proj_name.GetValue().strip()
        project_location = self.proj_loc.GetValue().strip()

        if not project_name or re.search(r'[<>:"/\\|?*]', project_name) or project_name.upper() in ["CON", "PRN", "AUX", "NUL"] + [f"COM{i}" for i in range(1, 10)] + [f"LPT{i}" for i in range(1, 10)]:
            wx.MessageBox('Failed creating project folder. Invalid project name.', 'Error', wx.OK | wx.ICON_ERROR)
            return

        if not project_location or not os.path.isdir(project_location):
            wx.MessageBox('Failed creating project folder. Invalid project location.', 'Error', wx.OK | wx.ICON_ERROR)
            return

        use_existing = self.e_api_rb.GetValue()
        api_name = self.e_prim_api.GetValue() if use_existing else self.n_prim_api.GetValue()
        api_key = self.e_api_key.GetValue() if use_existing else self.n_api_key.GetValue()
        if not api_name:
            wx.MessageBox('Failed creating project folder. Empty API name.', 'Error', wx.OK | wx.ICON_ERROR)
            return
        if not api_name:
            wx.MessageBox('Failed creating project folder. Empty API Key name.', 'Error', wx.OK | wx.ICON_ERROR)
            return
        project_path = os.path.join(project_location, project_name)
        try:
            os.makedirs(project_path, exist_ok=False)
        except FileExistsError:
            pass
        except PermissionError:
            wx.MessageBox(f'Failed creating project folder. Check file permissions', 'Error', wx.OK | wx.ICON_HAND)
            return
        
        project_dirs = ['tmp','config','data']
        if self.tog_log_on_rb.GetValue():
            project_dirs.append('logs')
        if not use_existing:
            project_dirs.append('user_apis')
        
        dir_created, log_file_path = ps.setup_project_directories(project_path, project_dirs)
        if not dir_created:
            dialog = wx.MessageDialog(None, f"Setup failed. Would you like to keep the log file at:\n{log_file_path}?",
                              "Setup Failed", wx.YES_NO | wx.ICON_QUESTION)
            result = dialog.ShowModal()
            if result == wx.ID_NO:
                try:
                    os.remove(log_file_path)
                    print("Log file has been deleted.")
                except Exception as e:
                    print(f"Failed to delete log file: {e}")
            elif result == wx.ID_YES:
                print("Log file has been kept.")
            dialog.Destroy()
            return

        config_path = os.path.join(project_path, 'config', 'config.ini')
        config = configparser.ConfigParser()
        config['Project'] = {
            'api': api_name,
            'apiKey': api_key 
        }
        with open(config_path, 'w') as configfile:
            config.write(configfile)

        wx.MessageBox(f"Project '{project_name}' created successfully at '{project_location}'", "Project Created", wx.OK | wx.ICON_INFORMATION)
        self.on_cancel(None)
        self.init_project_panes(project_path)
            
    def init_project_panes(self, project_path):
        self.init_file_explorer(project_path)
        self.init_content_area()
        self.init_requests_pane(project_path)
        self._mgr.Update()

    
    def init_file_explorer(self, project_path):
        self.project_path = project_path
        explorer_panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        refresh_button = wx.Button(explorer_panel, label="Refresh")
        refresh_button.Bind(wx.EVT_BUTTON, lambda evt: self.refresh_files(project_path))
        
        # Creating a tree control with just the project name
        self.tree_ctrl = wx.TreeCtrl(explorer_panel)
        root = self.tree_ctrl.AddRoot(os.path.basename(project_path))
        self.build_file_tree(root, project_path)
        self.tree_ctrl.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_open_file)

        vbox.Add(refresh_button, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.tree_ctrl, 1, wx.EXPAND)
        explorer_panel.SetSizer(vbox)

        # Add this panel to the left side of the window
        self._mgr.AddPane(explorer_panel, aui.AuiPaneInfo().Left().Caption("Project Files"))
        self._mgr.Update()
        
    def refresh_files(self, project_path):
        # Refresh the tree structure
        self.tree_ctrl.DeleteAllItems()
        root = self.tree_ctrl.AddRoot(os.path.basename(project_path))
        self.build_file_tree(root, project_path)
        self.tree_ctrl.Expand(root)

        # Refresh open files in the content area
        self.refresh_open_files()

        self._mgr.Update()

    def refresh_open_files(self):
        for page_index in range(self.notebook.GetPageCount()):
            page = self.notebook.GetPage(page_index)
            file_path = self.file_paths.get(page_index)
            if file_path and os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    page.SetValue(file.read())
            else:
                page.SetValue("File not found or removed.")
                self.notebook.SetPageText(page_index, "Missing: " + os.path.basename(file_path))
    
    def on_notebook_page_close(self, event):
        page_index = event.GetSelection()
        if page_index in self.file_paths:
            del self.file_paths[page_index]  # Remove the entry from the dictionary
        event.Skip()


    def build_file_tree(self, tree_item, path):
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                child_item = self.tree_ctrl.AppendItem(tree_item, entry)
                self.build_file_tree(child_item, full_path)
            else:
                self.tree_ctrl.AppendItem(tree_item, entry)
                
    def init_content_area(self):
        content_panel = wx.Panel(self)
        self.notebook = aui.AuiNotebook(content_panel)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.notebook, 1, wx.EXPAND)
        content_panel.SetSizer(vbox)

        self._mgr.AddPane(content_panel, aui.AuiPaneInfo().CenterPane().Caption("Open Files"))
        self._mgr.Update()

    def on_open_file(self, event):
        item = event.GetItem()
        if not item.IsOk():
            return  # No item selected

        relative_path = self.tree_ctrl.GetItemText(item)
        print(self.tree_ctrl.GetItemText(item))
        print(self.tree_ctrl.GetItemText(self.tree_ctrl.GetItemParent(item)))
        print(self.tree_ctrl.GetItemParent(item) == self.tree_ctrl.GetRootItem())
        file_path = os.path.join(self.project_path, self.get_full_item_path(item))
        print(file_path)
        if os.path.isfile(file_path):
            self.open_file_in_tab(file_path)

    def get_full_item_path(self, item):
        """ Recursively construct the full path to an item in the tree control, including specific subdirectories as needed. """
        path = []
        while item and not item == self.tree_ctrl.GetRootItem():
            path.append(self.tree_ctrl.GetItemText(item))
            print(path)
            item = self.tree_ctrl.GetItemParent(item)
        # Correct the path if a known directory structure is expected
        full_path = os.path.join(*reversed(path))
        
        return full_path


    def open_file_in_tab(self, file_path):
        new_page = wx.TextCtrl(self.notebook, style=wx.TE_MULTILINE)
        with open(file_path, 'r') as file_content:
            new_page.SetValue(file_content.read())
        self.notebook.AddPage(new_page, os.path.basename(file_path))
        page_index = self.notebook.GetPageIndex(new_page)
        self.file_paths[page_index] = file_path
        
    def init_requests_pane(self, project_path):
        api_panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Create a notebook within the panel
        notebook = aui.AuiNotebook(api_panel)

        # Tabs
        self.add_api_request_tab(notebook, project_path)
        self.add_network_tab(notebook)
        self.add_api_config_tab(notebook, project_path)

        vbox.Add(notebook, 1, wx.EXPAND)
        api_panel.SetSizer(vbox)

        # Add to the main frame or AUI manager
        self._mgr.AddPane(api_panel, aui.AuiPaneInfo().Bottom().Caption("Tools"))
        self._mgr.Update()

    def add_api_request_tab(self, notebook, project_path):
        panel = wx.Panel(notebook)
        vbox = wx.BoxSizer(wx.VERTICAL)
        st = wx.StaticText(panel, label="Enter API endpoint and parameters:")
        # Placeholder for API request inputs
        vbox.Add(st, flag=wx.ALL, border=5)
        notebook.AddPage(panel, "Requests")

    def add_network_tab(self, notebook):
        panel = wx.Panel(notebook)
        vbox = wx.BoxSizer(wx.VERTICAL)
        st = wx.StaticText(panel, label="Network settings and status:")
        # Placeholder for network settings
        vbox.Add(st, flag=wx.ALL, border=5)
        notebook.AddPage(panel, "Network")

    def add_api_config_tab(self, notebook, project_path):
        panel = wx.Panel(notebook)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Simple form to enter API key
        st = wx.StaticText(panel, label="API Key:")
        api_key_text_ctrl = wx.TextCtrl(panel)
        save_button = wx.Button(panel, label="Save API Key")
        save_button.Bind(wx.EVT_BUTTON, lambda evt: self.save_api_key(evt, api_key_text_ctrl.GetValue(), project_path))

        vbox.Add(st, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.Add(api_key_text_ctrl, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.Add(save_button, flag=wx.EXPAND|wx.ALL, border=5)

        notebook.AddPage(panel, "Config")


    def save_api_key(self, event, api_key, project_path):
        config_path = os.path.join(project_path, 'config', 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        config['Project']['api_key'] = api_key
        with open(config_path, 'w') as configfile:
            config.write(configfile)
        wx.MessageBox("API Key saved successfully!", "Success", wx.OK | wx.ICON_INFORMATION)



if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
