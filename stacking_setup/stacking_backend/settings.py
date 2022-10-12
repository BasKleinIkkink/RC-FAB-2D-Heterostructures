

class Settings():
    """
    This file contains the settings class.
    
    The settings class is responsible for loading and validating all the settings.
    Most of the type enforcing will be done in this class, this makes other
    classes less clutered and debugging easier.
    """

    def __init__(self, config_file):
        self._config_file = config_file

    def load_config(self):
        """
        Load the config file.
        """
        config = configparser.ConfigParser()
        config.read(self._config_file)
        return config
