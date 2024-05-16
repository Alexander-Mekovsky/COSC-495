import wx
from style.theme import Theme

# Define constants for widget types to be used for theming.
TITLE = 'title'
HEADER = 'header'
GENERAL= 'general'
LIST = 'list'
LINK = 'link'
NOTE = 'note'

# Define wxFormat class which is a specialized theme class for wxPython applications.
class wxFormat(Theme):
    def __init__(self, path, name):
        # Load the theme configuration using inherited method from Theme.
        self._config = self.load_theme(name = name, path=path)
        
        self.current_theme = {}
        for key, value in self._config.items(name):
            self.current_theme[key] = value
            
        # Define adjustments for each widget type to modify themes dynamically.
        self.theme_adjustments = {
            TITLE: {'font_size_offset': 2, 'color_factor': 0.1},  # Lighter
            HEADER: {'font_size_offset': 1, 'color_factor': 0.05},  # Slightly lighter
            GENERAL: {'font_size_offset': 0, 'color_factor': 0.0},  # No change
            LIST: {'font_size_offset': -1, 'color_factor': -0.05},  # Slightly darker
            NOTE: {'font_size_offset': -2, 'color_factor': -0.1}  # Darker
        }
        
        # Defines default spacings for widgets added to the theme
        self.default_spacing = {
            'proportion':0, 
            'flag':wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM,
            'border':10
        }
        
        self.widgets_control = {}
        
    def adjust_color(self, color, factor):
        """
        Adjust the color brightness based on the factor.
        Lighten the color if factor is positive, darken if negative.
        """
        base_color = wx.Colour(color)
        r = min(255, max(0, base_color.Red() + base_color.Red() * factor))
        g = min(255, max(0, base_color.Green() + base_color.Green() * factor))
        b = min(255, max(0, base_color.Blue() + base_color.Blue() * factor))
        return wx.Colour(int(r), int(g), int(b))

    # Apply theme settings to a specific widget based on the theme configuration and adjustments.
    def apply_theme(self, widget, widget_type):
        """
        Apply themes to the given widget.
        Adjusts the base theme to fit each specific widget type.
        """
        if not widget or not self.current_theme:
            return

        # Fetch current adjustments for the widget type.
        current_adjustments = self.theme_adjustments.get(widget_type, {'font_size_offset': 0, 'color_factor': 0})

        # Apply background color from the theme.
        if 'background_color' in self.current_theme and hasattr(widget, 'SetBackgroundColour'):
            widget.SetBackgroundColour(self.current_theme['background_color'])

        # Adjust and apply the foreground color using color factor.
        base_foreground_color = self.current_theme.get('foreground_color', 'black')
        adjusted_foreground_color = self.adjust_color(color=base_foreground_color, factor=current_adjustments['color_factor'])
        if hasattr(widget, 'SetForegroundColour'):
            widget.SetForegroundColour(adjusted_foreground_color)

        # Adjust and apply font settings.
        if hasattr(widget, 'GetFont') and hasattr(widget, 'SetFont'):
            font = widget.GetFont()
            if 'font_size' in self.current_theme:
                adjusted_font_size = int(self.current_theme['font_size']) + current_adjustments['font_size_offset']
                font.SetPointSize(adjusted_font_size)
            if 'font_family' in self.current_theme:
                font.SetFamily(self._get_font_family(self.current_theme['font_family']))
            widget.SetFont(font)

        if hasattr(widget, 'Refresh'):
            widget.Refresh()

    def apply_theme_all(self):
        """
        Apply theme settings to all widgets controlled by this class.
        """
        for widget_pair in self.widgets_control.values():
            self.apply_theme(widget_pair[0], widget_pair[1])
        
    def add_widgets(self, parent, child, widget_type = GENERAL, flag=None, proportion=None, border=None):
        """
        Adds a child widget(not wx.Sizer) to the parent widget(wx.Sizer). Then adds the child to the theme.
        """
        if not isinstance(parent, wx.Sizer):
            raise ValueError("Parent must be a wx.Sizer instance")
        if isinstance(child, wx.Sizer):
            raise ValueError("Child is a wx.Sizer instance. Sizers do not need to be added to the theme")
        
        if not proportion:
            proportion = self.default_spacing['proportion']
        if not flag:
            flag = self.default_spacing['flag']
        if not border:
            border = self.default_spacing['border']
        
        parent.Add(child, proportion=proportion, flag=flag, border=border)
        self.Add(child, widget_type)
        
    def change_theme(self, name):
        try:
            self.load_theme(name,self._config)
            self.current_theme = self._config.items(name)
            self.apply_theme_all()
        except Exception as e:
            print(f"Error validating theme {name}: {e}")

    def Add(self, widget, widget_type):
        """
        Adds a widget to the theme with its associated type.
        """
        self.widgets_control[len(self.widgets_control)] = [widget, widget_type]
    
    @staticmethod
    def _get_font_family(font_name):
        """
        Convert font family name to wx.FontFamily
        """
        font_map = {
            'Arial': wx.FONTFAMILY_SWISS,
            'Helvetica': wx.FONTFAMILY_SWISS,
            'Times New Roman': wx.FONTFAMILY_ROMAN,
            'Courier New': wx.FONTFAMILY_TELETYPE,
            'Comic Sans MS': wx.FONTFAMILY_SCRIPT
        }
        return font_map.get(font_name, wx.FONTFAMILY_DEFAULT)