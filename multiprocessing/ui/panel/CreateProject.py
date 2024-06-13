import wx

import os
import configparser
import shutil

import util.ui as ui
import style.wx as twx
import util.file as fut

class CreateProjectPanel(wx.Panel):
    def __init__(self,parent):
        super(CreateProjectPanel, self).__init__(parent)
        self.parent = parent
        
        theme = parent.theme
        
        main_sizer, box= ui.box(direction=wx.VERTICAL)
        main_sizer.Add((-1, 10))
        
        center_sizer, box= ui.box(direction=wx.VERTICAL)
        
        title_box, box = ui.box(direction=wx.VERTICAL)
        title = ui.text(self, "Create New Project")
        theme.add_widgets(title_box,title, twx.TITLE, 
                          0, wx.ALIGN_LEFT | wx.ALL, 10)
        
        description = "Configure and initiate a new project designed for API interaction. In this context, a 'project' is a uniuie configuration comprising specific API connections, logging preferences, and other adjustable settings that are uniuiely identified by a project name. This framework allows for efficient management of various API configurations and reuiests, each organized into distinct projects. Such organization facilitates streamlined API testing, effective data retrieval, and seamless integration with other applications, enhancing overall workflow and productivity."
        desc = ui.text(self, description)
        theme.add_widgets(title_box, desc, twx.GENERAL, 
                          1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        center_sizer.Add(title_box, proportion=2, flag=wx.ALIGN_LEFT | wx.ALL, border=10)
        
        proj_info_sizer, proj_info_box = ui.box(self, True, "Project Information", wx.VERTICAL)
        theme.Add(proj_info_box, twx.HEADER)
        
        proj_name_sizer, proj_name_label, self.proj_name = ui.inputbox(self, "Project Name")
        theme.Add(proj_name_label, twx.LIST)
        theme.Add(self.proj_name, twx.LIST)
        proj_info_sizer.Add(proj_name_sizer, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        
        
        proj_loc_sizer, proj_loc_label, self.proj_loc, browse_btn = ui.browsebox(self, self.on_browse, "Location:")
        theme.Add(proj_loc_label, twx.GENERAL)
        theme.Add(self.proj_loc, twx.GENERAL)
        theme.Add(browse_btn, twx.GENERAL)
        proj_info_sizer.Add(proj_loc_sizer, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        
        center_sizer.Add(proj_info_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        
        proj_api_sizer, proj_api_box = ui.box(self, True, "API Information", wx.VERTICAL)
        theme.Add(proj_api_box, twx.HEADER)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.on_radio_button_toggle)
        e_api_sizer, box = ui.box(direction=wx.VERTICAL)
        self.e_api_rb = wx.RadioButton(self, label='Use an existing API:', style=wx.RB_GROUP)
        theme.add_widgets(e_api_sizer,self.e_api_rb, twx.GENERAL,
                          0, wx.EXPAND | wx.ALL, 10)
        
        path = r"C:\Users\Joshua\Documents\School\Classes\COSC-495\multiprocessing\api\allowedAPI.csv"
        e_prim_api_sizer, self.e_prim_api_label, self.e_prim_api, self.e_prim_api_desc = ui.dropbox(self, fut.load_from_csv, path,  self.on_api_selection_changed, "Select Primary API:")
        theme.Add(self.e_prim_api_label, twx.GENERAL)
        theme.Add(self.e_prim_api, twx.GENERAL)
        e_api_sizer.Add(e_prim_api_sizer, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        theme.add_widgets(e_api_sizer, self.e_prim_api_desc, twx.LIST, 
                          0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        
        e_api_key_sizer, self.e_api_key_label, self.e_api_key = ui.inputbox(self, "API Key:")
        theme.Add(self.e_api_key_label, twx.LIST)
        theme.Add(self.e_api_key, twx.LIST)
        e_api_sizer.Add(e_api_key_sizer, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        
        proj_api_sizer.Add(e_api_sizer, flag=wx.EXPAND | wx.ALL, border=5)
        
        n_api_sizer, box = ui.box(direction=wx.VERTICAL)
        self.n_api_rb = wx.RadioButton(self, label='Load a new API:')
        theme.add_widgets(n_api_sizer,self.n_api_rb, twx.GENERAL,
                          0, wx.EXPAND | wx.ALL, 10)
        
        n_prim_api_sizer, self.n_prim_api_label, self.n_prim_api = ui.inputbox(self, "API Name:")
        theme.Add(self.n_prim_api_label, twx.LIST)
        theme.Add(self.n_prim_api, twx.LIST)
        n_api_sizer.Add(n_prim_api_sizer, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        
        n_api_desc_sizer, self.n_api_desc_label, self.n_api_desc = ui.inputbox(self, "Description:")
        theme.Add(self.n_api_desc_label, twx.LIST)
        theme.Add(self.n_api_desc, twx.LIST)
        n_api_sizer.Add(n_api_desc_sizer, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        
        n_api_key_sizer, self.n_api_key_label, self.n_api_key = ui.inputbox(self, "API Key:")
        theme.Add(self.n_api_key_label, twx.LIST)
        theme.Add(self.n_api_key, twx.LIST)
        n_api_sizer.Add(n_api_key_sizer, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border = 10)
        
        proj_api_sizer.Add(n_api_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)
        
        note = ui.text(self, "Note: You will be able to change API and select secondary APIs at a later time.")
        theme.add_widgets(proj_api_sizer, note, twx.NOTE,
                          wx.TE_READONLY | wx.TOP, 10)
        
        center_sizer.Add(proj_api_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border = 10)
        
        self.e_api_rb.SetValue(True)
        self.e_prim_api_desc.Hide()
        self.e_api_key_label.Hide()
        self.e_api_key.Hide()
        
        # Initial new api ui setup 
        self.n_api_rb.SetValue(False)
        self.n_prim_api.Disable()
        self.n_api_key_label.Hide()
        self.n_api_key.Hide()
        self.n_api_desc_label.Hide()
        self.n_api_desc.Hide()
        
        logging_sizer, log_box = ui.box(self, True, "Logging Information",wx.VERTICAL)
        theme.Add(log_box, twx.HEADER)
        
        tog_log_sizer, box = ui.box()
        tog_log_label = ui.text(self, "Enable Logging?")
        theme.add_widgets(tog_log_sizer, tog_log_label, twx.GENERAL,
                          0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        self.tog_log_on_rb = wx.RadioButton(self, label='Yes', style=wx.RB_GROUP)
        tog_log_off_rb = wx.RadioButton(self, label='No')
        theme.add_widgets(tog_log_sizer, self.tog_log_on_rb, twx.LIST,
                           0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        theme.add_widgets(tog_log_sizer, tog_log_off_rb, twx.LIST,
                           0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        
        logging_sizer.Add(tog_log_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=0)
        center_sizer.Add(logging_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        
        self.tog_log_on_rb.SetValue(True)
        tog_log_off_rb.SetValue(False)
        
        action_btns_sizer, box = ui.box()
        cancel_btn = wx.Button(self, label="Cancel")
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        theme.add_widgets(action_btns_sizer, cancel_btn, twx.GENERAL,
                          0, wx.RIGHT, 8)
        create_btn = wx.Button(self, label="Create")
        create_btn.Bind(wx.EVT_BUTTON, self.on_create)
        theme.add_widgets(action_btns_sizer, create_btn, twx.GENERAL,
                          0, wx.RIGHT, 8)
        
        center_sizer.Add(action_btns_sizer, flag=wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.RIGHT, border=10)
        
        main_sizer.Add(center_sizer, proportion = 1, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border=100)
        
        theme.Add(self, twx.GENERAL)
        
        theme.apply_theme_all()
        self.enabled = proj_name_label.GetForegroundColour()
        self.n_prim_api_label.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
        
        self.SetSizer(main_sizer)
        self.Layout()
        wrap_width = center_sizer.GetSize()[0] - 20  # Adjust the subtraction for actual margins
        
        desc.Wrap(wrap_width)
        self.Layout()
        self.Refresh()
        
        self.parent._mgr.Update()
        
        
    def on_browse(self, event, location):
        """Opens a file explorer dialog to choose a directory"""
        with wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_OK:
                location.SetValue(dirDialog.GetPath())
                
    def on_radio_button_toggle(self, event):
        """Changes the visible fields depending on which button is selected"""
        if self.n_api_rb.GetValue():
            self.e_prim_api_label.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
            self.e_prim_api.Disable()
            self.e_prim_api_desc.Hide()
            self.e_api_key_label.Hide()
            self.e_api_key.Hide()
            
            self.n_prim_api_label.SetForegroundColour(self.enabled)
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

            self.e_prim_api_label.SetForegroundColour(self.enabled)
            self.e_prim_api.Enable()
            if self.e_prim_api.GetValue() != "":
                self.e_prim_api_desc.Show()
                self.e_api_key_label.Show()
                self.e_api_key.Show()
        self.parent._mgr.Update()
        
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
            self.parent._mgr.Update()
    
    def on_cancel(self, event):
        if self.parent._mgr.GetPane("create_project").IsOk():
            self.parent._mgr.ClosePane(self.parent._mgr.GetPane("create_project"))
            self.parent._mgr.DetachPane(self.parent._mgr.GetPane("create_project").window)
        self.parent.show_all_panes()
        self.parent._mgr.Update()
        
    def on_create(self, event):
        import re
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
            project_dir_exists = True
        except PermissionError:
            wx.MessageBox(f'Failed creating project folder. Check file permissions', 'Error', wx.OK | wx.ICON_HAND)
            return
        
        project_dirs = ['tmp','config','data']
        if self.tog_log_on_rb.GetValue():
            project_dirs.append('logs')
        if not use_existing:
            project_dirs.append('user_apis')
        
        dir_created, log_file_path = fut.setup_project_directories(project_path, project_dirs)
        if not dir_created:
            dialog = wx.MessageDialog(None, f"Setup failed. Would you like to keep the log file at:\n{log_file_path}?",
                              "Setup Failed", wx.YES_NO | wx.ICON_QUESTION)
            result = dialog.ShowModal()
            if result == wx.ID_NO:
                try:
                    os.remove(log_file_path)
                    if project_dir_exists:
                        shutil.rmtree(project_path)
                    print("Log file has been deleted.")
                except Exception as e:
                    print(f"Failed to delete log file: {e}")
            elif result == wx.ID_YES:
                print("Log file has been kept.")
            
            dialog.Destroy()
            return
        os.remove(log_file_path)
        

        config_path = os.path.join(project_path, 'config', 'config.ini')
        config = configparser.ConfigParser()
        config['Project'] = {
            'apiname': api_name,
            'apikey': api_key,
            'path_output': os.path.join(project_path, 'data')
        }
        if not use_existing:
            config['Project']['user_api'] = 'true'
        with open(config_path, 'w') as configfile:
            config.write(configfile)

        wx.MessageBox(f"Project '{project_name}' created successfully at '{project_location}'", "Project Created", wx.OK | wx.ICON_INFORMATION)
        self.on_cancel(None)
        
        self.parent.project_panel(project_path)
        
        self.parent._mgr.Update()