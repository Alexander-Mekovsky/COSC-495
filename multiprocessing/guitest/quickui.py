import wx

def box(parent='', static=False, label='', direction='horiz'):
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

    orient = wx.HORIZONTAL if direction == 'horiz' else wx.VERTICAL
    text = label if label else ''

    if static:
        # Create a static box and static box sizer if the static parameter is True
        static_box = wx.StaticBox(parent, label=text)
        box_sizer = wx.StaticBoxSizer(static_box, orient)
    else:
        # Create a regular box sizer if the static parameter is False
        box_sizer = wx.BoxSizer(orient)

    return box_sizer

def editcombo(parent, text):
    """
    Creates a combo editor with a label and a text control inside a horizontal box sizer.
    
    Args:
        parent (wx.Window): The parent window for the components.
        text (str): Text for the text to the left of the input field
    
    Returns:
        wx.Sizer: The created box sizer.
        wx.StaticText: The created text.
        wx.TextCtrl: The created input field.
    """
    # Create a horizontal box sizer using the box function
    main_sizer = box()
    
    # Create the label for the input
    label = wx.StaticText(parent, label=text)
    main_sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)
    
    # Create the text control for the input

    text_ctrl = wx.TextCtrl(parent)
    # Add the input sizer to the main sizer
    main_sizer.Add(text_ctrl, proportion=1)
    
    return main_sizer, label, text_ctrl

import wx

def browsecombo(parent, event_handler, text):
    """
    Creates a combo with a label, text control, and browse button inside a horizontal box sizer.
    
    Args:
        parent (wx.Window): The parent window for the components.
        event_handler (callable): The function to handle the browse button click event.
        text (str): Text for the label next to the text control.
    
    Returns:
        tuple: Tuple containing the box sizer (wx.Sizer), the label (wx.StaticText), and the text control (wx.TextCtrl).
    """
    # Create a horizontal box sizer
    location_hbox = box()
    
    # Create the label for the location input
    location_label = wx.StaticText(parent, label=text)
    location_hbox.Add(location_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)
    
    # Create the text control for the location input
    location_text_ctrl = wx.TextCtrl(parent)
    location_hbox.Add(location_text_ctrl, proportion=1)
    
    # Create the browse button
    browse_button = wx.Button(parent, label='Browse...')
    browse_button.Bind(wx.EVT_BUTTON, lambda evt: event_handler(location_text_ctrl))
    location_hbox.Add(browse_button, flag=wx.LEFT, border=5)
    
    return location_hbox, location_label, location_text_ctrl


def dropcombo(parent, populate_method, event_handler, text):
    """
    Creates a combo box with a label and an associated description text control.
    
    Args:
        parent (wx.Window): The parent window for the combo box.
        populate_method (function): The method to populate the ComboBox.
        event_handler (function): The event handler for when the ComboBox selection changes.
        text (str): The label text for the ComboBox.
    
    Returns:
        wx.Sizer
        wx.StaticText
        wx.ComboBox
        wx.TextControl
    """
    # Create the main horizontal box sizer
    hbox = box()
    
    # Create and add the label for the ComboBox
    label = wx.StaticText(parent, label=text)
    hbox.Add(label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=8)
    
    # Create the ComboBox and set up event handling and population
    combo_box = wx.ComboBox(parent, style=wx.CB_READONLY)
    populate_method(combo_box)  # Populate the ComboBox using the provided method
    combo_box.Bind(wx.EVT_COMBOBOX, event_handler)
    hbox.Add(combo_box, proportion=1)
    
    # Create the description TextCtrl
    description = wx.StaticText(parent, label='')
    description.SetMinSize((-1, 40))
    description.Hide()  # Initially hide the description
    
    # Return the sizer, label, ComboBox, and description TextCtrl
    return hbox, label, combo_box, description

import wx

def note(parent, text):
    """
    Creates a static text control with a specified note, applying a smaller font and grey color.
    
    Args:
        parent (wx.Window): The parent window for the static text.
        text (str): The text to be displayed in the note.
    
    Returns:
        wx.StaticText: The static text control with the applied settings.
    """
    # Create the static text control with the provided text
    user_note = wx.StaticText(parent, label=text)
    
    # Get the current font from the control and modify it
    current_font = user_note.GetFont()
    smaller_font = wx.Font(current_font.GetPointSize() - 2,  # Reduce the font size by 2 points
                           current_font.GetFamily(),
                           current_font.GetStyle(),
                           current_font.GetWeight(),
                           current_font.GetUnderlined(),
                           current_font.GetFaceName())
    
    # Set the modified font and the foreground color
    user_note.SetFont(smaller_font)
    user_note.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
    
    return user_note

