import wx
import wx.html


def box(parent='', static=False, label='', direction=wx.HORIZONTAL):
    """
    Create and return a wx box sizer, either static or regular.
    
    Args:
        parent (wx.Window): The parent window for the box sizer.
        static (bool): True for a static box sizer with a label, False for a regular box sizer.
        label (str): Label of the box, used only if static is True.
        direction (str): 'horiz' for a horizontal box sizer, 'vert' for a vertical box sizer.
    
    Returns:
        wx.Sizer: The created box sizer.
    """

    orient = direction
    text = label if label else ''

    if static:
        # Create a static box and static box sizer if the static parameter is True
        static_box = wx.StaticBox(parent, label=text)
        box_sizer = wx.StaticBoxSizer(static_box, orient)
    else:
        # Create a regular box sizer if the static parameter is False
        static_box = None
        box_sizer = wx.BoxSizer(orient)

    return box_sizer, static_box

def text(parent, txt):
    """
    Creates a static text control for a title.
    """
    text_element = wx.StaticText(parent, label=txt)
    return text_element

def list(parent, linked_items=None, regular_items=None):
    """
    Creates and returns a vertical box sizer filled with static texts for each item in a list.
    
    Args:
        panel (wx.Panel): The wx.Panel on which the sizer will be used.
        items (list): A list of string items to include in the list.
        
    Returns:
        wx.Sizer: the box sizer containing all of the list values
        list: list containing all of the non-sizer objects created
    """
    if not linked_items and not regular_items:
        raise ValueError("Linked list items AND regular list items cannot be None")
    
    vbox, ebox = box(direction=wx.VERTICAL)
    
    item_list = []
    number = 1
    for item_l in linked_items:
        hbox, ebox = box()
        left_label = text(parent, f"{number}.")
        item_list.append(left_label)
        hbox.Add(left_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.ALL, border=5)
        
        html = wx.html.HtmlWindow(parent, size=(len(item_l[0])*8, 40),style=wx.html.HW_SCROLLBAR_NEVER)
        html.SetPage(f'<span style="color: #FF0000" ><a href="{item_l[0]}">{item_l[0]}</a></span>')
        html.Bind(wx.html.EVT_HTML_LINK_CLICKED, item_l[1])
        item_list.append(html)
        hbox.Add(html, proportion=1, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=5)
        
        hbox_right, ebox = box()
        right_label = text(parent, f"{item_l[2]}")
        item_list.append(right_label)
        hbox_right.Add(right_label, proportion=0, flag=wx.EXPAND)
        
        hbox.Add(hbox_right, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox, proportion=1, flag=wx.EXPAND | wx.ALL)
        
        number += 1
    for item_r in regular_items:
        label = text(parent, f"{number}. {item_r}")
        item_list.append(label)
        vbox.Add(label, proportion= 1, flag= wx.EXPAND | wx.ALL, border=5)
        number += 1
    
    vbox.Layout()
    
    return vbox, item_list
    
def inputbox(parent, txt):
    """
    Creates an input box with a label and a text control inside a horizontal box sizer.
    
    Args:
        parent (wx.Window): The parent window for the components.
        text (str): Text for the text to the left of the input field
    
    Returns:
        wx.Sizer: The created box sizer.
        wx.StaticText: The created text.
        wx.TextCtrl: The created input field.
    """
    
    main_sizer, ebox = box()
    label = text(parent, txt)
    main_sizer.Add(label, proportion = 0, flag = wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10)
    
    text_ctrl = wx.TextCtrl(parent)
    main_sizer.Add(text_ctrl, proportion = 1, flag=wx.EXPAND)
    
    return main_sizer, label, text_ctrl

def browsebox(parent, event_handler, txt):
    """
    Creates a combo with a label, text control, and browse button inside a horizontal box sizer.
    
    Args:
        parent (wx.Window): The parent window for the components.
        event_handler (callable): The function to handle the browse button click event.
        text (str): Text for the label next to the text control.
    
    Returns:
        tuple: Tuple containing the box sizer (wx.Sizer), the label (wx.StaticText), and the text control (wx.TextCtrl).
    """
    hbox, ebox = box()
    
    label = text(parent, txt)
    hbox.Add(label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)
    
    text_ctrl = wx.TextCtrl(parent)
    hbox.Add(text_ctrl, proportion = 1)
    
    browse_button = wx.Button(parent, label='Browse...')
    browse_button.Bind(wx.EVT_BUTTON, lambda evt: event_handler(evt, text_ctrl))
    hbox.Add(browse_button, flag=wx.LEFT, border=5)
    
    return hbox, label, text_ctrl, browse_button
    
def dropbox(parent, populate_method, path, event_handler, txt):
    """
    Creates a combo box with a label and an associated description text control.
    
    Args:
        parent (wx.Window): The parent window for the combo box.
        populate_method (function): The method to populate the ComboBox.
        path (str): The path to where the dropbox is populating from
        event_handler (function): The event handler for when the ComboBox selection changes.
        text (str): The label text for the ComboBox.
    
    Returns:
        wx.Sizer
        wx.StaticText
        wx.ComboBox
        wx.TextControl
    """
    
    hbox, ebox = box()
    
    label = text(parent, txt)
    hbox.Add(label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)
    
    dropbox = wx.ComboBox(parent, style=wx.CB_READONLY)
    populate_method(path,dropbox)
    dropbox.Bind(wx.EVT_COMBOBOX, event_handler)
    hbox.Add(dropbox, proportion = 1)
    
    description = text(parent, "")
    description.SetMinSize((-1, 40))
    description.Hide()
    
    return hbox, label, dropbox, description

import wx.lib.mixins.listctrl as listmix
class CheckListComboPopup(wx.ComboPopup, listmix.CheckListCtrlMixin):
    def __init__(self):
        super().__init__()
        self.lc = None
        self.items_checked = []

    def Init(self):
        self.value = -1

    def Create(self, parent):
        self.lc = wx.CheckListBox(parent, style=wx.LB_SINGLE | wx.LB_NEEDED_SB)
        self.lc.Bind(wx.EVT_LISTBOX, self.OnListBox)
        self.lc.Bind(wx.EVT_CHECKLISTBOX, self.OnCheckListBox)
        return True

    def GetControl(self):
        return self.lc

    def SetStringValue(self, value):
        idx = self.lc.FindString(value)
        if idx != wx.NOT_FOUND:
            self.lc.Check(idx, check=True)

    def GetStringValue(self):
        selections = [self.lc.GetString(i) for i in range(self.lc.GetCount()) if self.lc.IsChecked(i)]
        return ','.join(selections)

    def OnListBox(self, event):
        self.value = event.GetSelection()
        self.Dismiss()

    def OnCheckListBox(self, event):
        item_index = event.GetInt()  # Get the index of the item that was checked/unchecked
        item_label = self.lc.GetString(item_index)  # Get the label of the item

        if self.lc.IsChecked(item_index):
            # If the item is checked and not already in the list, add it
            if item_label not in self.items_checked:
                self.items_checked.append(item_label)
        else:
            # If the item is unchecked and currently in the list, remove it
            if item_label in self.items_checked:
                self.items_checked.remove(item_label)

    def AddItem(self, text):
        self.lc.Append(text)

    def Populate(self, items):
        for item in items:
            self.AddItem(item)