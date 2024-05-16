import wx
import wx.lib.agw.aui as aui
import wx.html

def test():
    pass
    
def text(parent, txt):
    text_element = wx.StaticText(parent, label=txt)
    return text_element

def box(parent='', static=False, label='', direction=wx.HORIZONTAL):
    orient = direction
    text = label if label else ''

    if static:
        # Create a static box and static box sizer if the static parameter is True
        static_box = wx.StaticBox(parent,size=-1, label=text)
        box_sizer = wx.StaticBoxSizer(static_box, orient)
    else:
        # Create a regular box sizer if the static parameter is False
        box_sizer = wx.BoxSizer(orient)

    return box_sizer

def list(parent, linked_items=None, regular_items=None):
    if not linked_items and not regular_items:
        raise ValueError("Linked list items AND regular list items cannot be None")
    
    vbox = box(direction=wx.VERTICAL)
    
    item_list = []
    number = 1
    for item_l in linked_items:
        hbox = box()
        left_label = text(parent, f"{number}.")
        item_list.append(left_label)
        hbox.Add(left_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.ALL, border=5)
        
        print(len(item_l[0])*14)
        html = wx.html.HtmlWindow(parent, size=(len(item_l[0])*8, 40),style=wx.html.HW_SCROLLBAR_NEVER)
        html.SetPage(f'<span style="color: #FF0000" ><a href="{item_l[0]}">{item_l[0]}</a></span>')
        html.Bind(wx.html.EVT_HTML_LINK_CLICKED, item_l[1])
        item_list.append(html)
        hbox.Add(html, proportion=1, flag=wx.EXPAND | wx.ALL)
        
        
        right_label = text(parent, f"{item_l[2]}")
        item_list.append(right_label)
        hbox.Add(right_label, proportion= 1, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border = 5)
        vbox.Add(hbox,proportion=0,flag=wx.EXPAND | wx.ALL)
        
        number += 1
    for item_r in regular_items:
        label = text(parent, f"{number}. {item_r}")
        item_list.append(label)
        vbox.Add(label, proportion= 0, flag= wx.EXPAND | wx.ALL, border=5)
        number += 1
    
    vbox.Layout()
    
    return vbox, item_list

if __name__ == '__main__':
    app = wx.App
    frame = wx.Frame(None, title='title', size = (1024,768))
    _mgr = aui.AuiManager(frame)
    panel = wx.Panel(frame)
    
    main_sizer = box()
    side_center = box()
    center_sizer = box(direction=wx.VERTICAL)
    
    linked_list = [
        ['Create a New Project',test, ': rquoipktdvohixqzvogkplqheturogclr gpzpvqujlyxrrcbolmyjfjruojkudsodfevgbxypnnoalvhyxsdirmbrnss.'],
        ['Open an Existing Project',test, ': Pick up the call where you left off.'],
        ['Explore TestValue Cases',test, ': rquoipktdvohixqzvogkplqheturogclr gpzpvqujlyxrrcbolmyjfjruojkudsodfevgbxypnnoalvhyxsdirmbrnss.'],
    ]
    regular_list = [
        'rquoipktdvohixqzvogkplqheturogclr gpzpvqujlyxrrcbolmyjfjruojkudsodfevgbxypnnoalvhyxsdirmbrnss.',
        'rquoipktdvohixqzvogkplqheturogclr gpzpvqujlyxrrcbolmyjfjruojkudsodfevgbxypnnoalvhyxsdirmbrnss.'
    ]

    list_size, list_items = list(panel, linked_list, regular_list)

    center_sizer.Add(list, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        
    side_center.Add(center_sizer, flag= wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM, border=100)
        
    main_sizer.Add(side_center,flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT, border=200)

    panel.SetSizer(main_sizer)
    panel.Layout()
    panel.Refresh()

    _mgr.AddPane(panel, aui.AuiPaneInfo().Name('panel').CenterPane())
    _mgr.Update()