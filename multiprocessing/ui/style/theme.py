from abc import ABC, abstractmethod
import util.file as util
class Theme(ABC):
    @staticmethod
    def load_theme(name, config=None, path=None):
        """
        Verifies the config file to load a theme for a UI from a configuration file. If config is None, create a new ConfigParser.
        
        Args:
            name (str): The theme name to load options for.
            config (configparser.ConfigParser, optional): A pre-existing config parser object.
            path (str, optional): The file path to load the configuration from if config is None.
        
        Returns:
            bool: A dictionary containing all options for the specified theme.
        """
        if config is None:
            if path is None:
                raise ValueError("Path cannot be None if no config is provided")
            config = util.load_config(path)
        
        if name not in config.sections():
            raise ValueError(f"No theme named '{name}' found in the configuration.")

        # Returning all options in the theme as a dictionary
        return config
    
    @abstractmethod
    def apply_theme(self, widget, size_offset):
        """
        Apply the theme to a specific widget. This method must be implemented by subclasses
        to define how the theme settings are applied to the widgets.

        Args:
            widget (Any): The widget to apply the theme settings to.
            size_offset (int): Changes the font size of the widget size_offset pts from the value in the config
        """
        pass
    @abstractmethod
    def apply_theme_all(self, size_offset):
        """
        Apply the theme to a all widgets controlled by class. This method must be implemented by subclasses
        to define how the theme settings are applied to the widgets.

        Args:
            widget (Any): The widget to apply the theme settings to.
        """
        pass