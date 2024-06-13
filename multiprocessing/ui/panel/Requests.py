import wx
import wx.lib.agw.aui as aui

import os
import configparser

import util.ui as ui
import style.wx as twx
import testcallwithui.make_call as mc

class RequestsPanel(wx.Panel):
    def __init__(self,parent, project_path):
        super(RequestsPanel, self).__init__(parent)
        self.parent = parent
        
        self.theme = parent.theme
        
        main_sizer, box = ui.box(direction=wx.VERTICAL)

        notebook = aui.AuiNotebook(self)
        self.theme.Add(notebook, twx.GENERAL)
        # Tabs
        self.add_api_request_tab(notebook, project_path)
        self.add_network_tab(notebook)
        self.add_api_config_tab(notebook, project_path)

        main_sizer.Add(notebook, 
                         1, wx.EXPAND, 0)

        # theme.Add(self, twx.GENERAL)
        self.theme.apply_theme_all()
        self.SetSizer(main_sizer)

        self.parent._mgr.Update()
        
    def add_api_request_tab(self, notebook, project_path):
        panel = wx.Panel(notebook)
        sizer, box = ui.box(direction=wx.VERTICAL)
        
        self.ready = False
        # check if the api endpoint exists in the config
        config_path = os.path.join(project_path, 'config', 'config.ini')
        config = configparser.ConfigParser()
        config.read(config_path)
        userAPI = config.get('Project', 'user_api', fallback=None)
        
        req_fields = ['apiname', 'apikey','path_output']
        if userAPI and userAPI == 'true':
            req_fields.append('apiendpoint')
        
        self.verify_fields(panel, sizer, config, req_fields, project_path)
        self.theme.Add(panel, twx.GENERAL)
        self.theme.apply_theme_all()
        panel.SetSizer(sizer)
        panel.Layout()
        
        notebook.AddPage(panel, "Requests")
    def on_browse(self, event, location):
        # Open a directory dialog
        with wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_OK:
                location.SetValue(dirDialog.GetPath())
        
    def verify_fields(self, panel, vbox, config, req_fields, path):
        field_vals = {}
        field_controls = {}
        
        for field in req_fields:
            value = config.get('Project', field, fallback = None)
            field_vals[field] = value
            if value is None:
                if field[:4] == 'path':
                    field_sizer, field_label, field_val, browse_btn = ui.browsebox(panel, self.on_browse, f'Select a/n {field[5:]} location:' )
                    field_controls[field] = [field_sizer, field_label, field_val, browse_btn]
                else:
                    field_sizer, field_label, field_val = ui.inputbox(panel, f'Enter a value for the field ({field}):')
                    field_controls[field] = [field_sizer, field_label, field_val]
                self.theme.Add(field_label, twx.GENERAL)
                self.theme.Add(field_val, twx.GENERAL)
                if browse_btn:
                    self.theme.Add(browse_btn, twx.GENERAL)
                self.theme.apply_theme_all()
                vbox.Add(field_sizer, flag=wx.TOP | wx.RIGHT | wx.LEFT , border=10)
                
        # check the field value, if it is not null, write to the config file and delete the 
        if field_controls:
            submit_btn = wx.Button(panel, label='Submit')
            submit_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_submit(event, field_controls, vbox, config, submit_btn, panel,path))
            self.theme.Add(submit_btn, twx.GENERAL)
            self.theme.apply_theme_all()
            vbox.Add(submit_btn, flag=wx.ALIGN_LEFT | wx.ALL, border=10)
        else:
            self.make_requests(panel,vbox, path, config)
        
    def on_submit(self, event, field_controls, vbox, config, submit_btn,panel, path):
        for field in list(field_controls.keys()):  # Use list to make a copy of keys for safe deletion
            control = field_controls[field]
            value = control[2].GetValue()
            if value:
                config['Project'][field] = value
                # Detach the label from the vbox
                vbox.Detach(control[0])
                # Destroy the label, static text, and text control
                
                for widget in field_controls[field]:
                    widget.Destroy()
                # Remove the field from the dictionary
                del field_controls[field]
                
        if not field_controls:
            vbox.Detach(submit_btn)
            submit_btn.Destroy()
            self.make_requests(panel, vbox, path, config)
        panel.Layout()
        self.parent.Layout()
        self.parent._mgr.Update()
        
        with open(os.path.join(path, 'config', 'config.ini'), 'w') as configfile:
            config.write(configfile)
        wx.MessageBox('Configuration Saved!', 'Info', wx.OK | wx.ICON_INFORMATION)
    
    
    def make_requests(self, panel, vbox, path, config):
        import pandas as pd
        # BASIC: Makes request on the user defined api framework
        if config.get('Project', 'user_api', fallback=None) and config['Project']['user_api'] == 'true':
            query_sizer, query_label, query = ui.editcombo(panel, 'Enter a query for the API: ')
            vbox.Add(query_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=10)
            use_api = config.get('Project', 'apiname',fallback=None)
            cur_api_sizer = ui.text(panel, f"Using the api: {use_api}")
            vbox.Add(cur_api_sizer, proportion=1, flag= wx.ALIGN_LEFT | wx.LEFT, border = 10)
        else: # Makes request on a preloaded api framework
            combo_sizer = wx.ComboCtrl(panel, style=wx.CB_READONLY)
            popup_sizer = ui.CheckListComboPopup()
            combo_sizer.SetPopupControl(popup_sizer)
            listdf = mc.read_api_config(config['Project']['apiname'])
            list = listdf['Field'].tolist()
            popup_sizer.Populate(list)
            hbox, box = ui.box()
            text = wx.StaticText(panel, label= "Select fields you would like in the output:")
            hbox.Add(text, 0, wx.ALL | wx.EXPAND, 5)
            hbox.Add(combo_sizer, 1, wx.ALL | wx.EXPAND, 5)
            vbox.Add(hbox, 0, flag=wx.ALL | wx.EXPAND, border=10)
            
            combo_sizerq = wx.ComboCtrl(panel, style=wx.CB_READONLY)
            popup_sizerq = ui.CheckListComboPopup()
            combo_sizerq.SetPopupControl(popup_sizerq)
            listdfq = mc.read_api_config_two(config['Project']['apiname'])
            listq = listdfq['Parameter'].tolist()
            popup_sizerq.Populate(listq)
            hboxq, box = ui.box()
            textq = wx.StaticText(panel, label= "Select parameters you would like to use for the query:")
            hboxq.Add(textq, 0, wx.ALL | wx.EXPAND, 5)
            hboxq.Add(combo_sizerq, 1, wx.ALL | wx.EXPAND, 5)
            vbox.Add(hboxq, 0, flag=wx.ALL | wx.EXPAND, border=10)
            use_api = config.get('Project', 'apiname',fallback=None)
            cur_api_sizer = ui.text(panel, f"Using the api: {use_api}")
            vbox.Add(cur_api_sizer, proportion=1, flag= wx.ALIGN_LEFT | wx.LEFT, border = 10)
        # submit_btn = wx.Button(panel, label='Send request')
        # submit_btn.Bind(wx.EVT_BUTTON, lambda event: self.on_submit(event, field_controls, vbox, config, submit_btn, panel,path))
        
    
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