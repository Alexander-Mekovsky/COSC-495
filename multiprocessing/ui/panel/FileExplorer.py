import wx
import os

import util.ui as ui 
import style.wx as twx

class FileExplorerPanel(wx.Panel):
    def __init__(self, parent, project_path):
        super(FileExplorerPanel, self).__init__(parent)
        self.parent = parent
        self.project_path = project_path
        self.file_paths = {}
        
        self.theme = parent.theme
        
        main_sizer, box = ui.box(direction=wx.VERTICAL)
        
        refresh_btn = wx.Button(self, label = "Refresh")
        refresh_btn.Bind(wx.EVT_BUTTON, lambda evt: self.refresh_files(evt,self.project_path))
        self.theme.add_widgets(main_sizer, refresh_btn, flag=wx.EXPAND | wx.ALL, border=5)
        
        self.tree_ctrl = wx.TreeCtrl(self)
        root = self.tree_ctrl.AddRoot(os.path.basename(self.project_path))
        self.build_file_tree(root, self.project_path)
        self.tree_ctrl.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_open_file)
        self.theme.add_widgets(main_sizer, self.tree_ctrl, twx.GENERAL,
                          0, wx.EXPAND | wx.ALL, 5)
        
        self.theme.Add(self, twx.GENERAL)
        self.theme.apply_theme_all()
        self.SetSizer(main_sizer)
        main_sizer.Layout()
        self.Layout()
        self.Refresh()
        
        self.parent._mgr.Update()
        
    def refresh_files(self, event ,path):
        # Refresh the tree structure
        self.tree_ctrl.DeleteAllItems()
        root = self.tree_ctrl.AddRoot(os.path.basename(path))
        self.build_file_tree(root, path)
        self.tree_ctrl.Expand(root)

        # Refresh open files in the content area
        self.refresh_open_files()

        self.parent._mgr.Update()
        
    def refresh_open_files(self):
        for page_index in range(self.parent.notebook.GetPageCount()):
            page = self.parent.notebook.GetPage(page_index)
            file_path = self.file_paths.get(page_index)
            if file_path and os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    page.SetValue(file.read())
            else:
                page.SetValue("File not found or removed.")
                self.parent.notebook.SetPageText(page_index, "Missing: " + os.path.basename(file_path))
        
    def build_file_tree(self, tree_item, path):
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                child_item = self.tree_ctrl.AppendItem(tree_item, entry)
                self.build_file_tree(child_item, full_path)
            else:
                self.tree_ctrl.AppendItem(tree_item, entry)
                
    def on_open_file(self, event):
        item = event.GetItem()
        if not item.IsOk():
            return  # No item selected

        relative_path = self.tree_ctrl.GetItemText(item)
        file_path = os.path.join(self.project_path, self.get_full_item_path(item))
        
        if os.path.isfile(file_path):
            self.open_file_in_tab(file_path)
    
    def get_full_item_path(self, item):
        """ Recursively construct the full path to an item in the tree control, including specific subdirectories as needed. """
        path = []
        while item and not item == self.tree_ctrl.GetRootItem():
            path.append(self.tree_ctrl.GetItemText(item))
            item = self.tree_ctrl.GetItemParent(item)
        # Correct the path if a known directory structure is expected
        full_path = os.path.join(*reversed(path))
        
        return full_path
    
    def open_file_in_tab(self, file_path):
        new_page = wx.TextCtrl(self.parent.notebook, style=wx.TE_MULTILINE)
        self.theme.Add(new_page, twx.GENERAL)
        with open(file_path, 'r') as file_content:
            new_page.SetValue(file_content.read())
        self.theme.Add(new_page, twx.GENERAL)
        self.parent.notebook.AddPage(new_page, os.path.basename(file_path))
        page_index = self.parent.notebook.GetPageIndex(new_page)
        self.file_paths[page_index] = file_path
        self.theme.apply_theme_all()
        new_page.SetSize(self.parent.notebook.GetClientSize())  # Set the size of the TextCtrl to the size of the notebook client area
        self.parent.notebook.GetAuiManager().Update()
        