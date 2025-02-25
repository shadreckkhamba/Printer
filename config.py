import os
import configparser

# Default configuration settings
DEFAULT_CONFIG = {
    'delete_files': True,           
    'file_directory': "Downloads",  
    'printer1': "Printer1",         
    'printer2': "Printer2"          
}

class PrinterConfiguration:
    def __init__(self, filename='config.ini'):
        self.filename = filename
        self.config = configparser.ConfigParser()

    def read(self):
        # If config file doesn't exist, create one with default values.
        if not os.path.exists(self.filename):
            self.create_default_config()
        # Read the configuration file
        self.config.read(self.filename)
        return self.config

    def create_default_config(self):
        # Use the DEFAULT_CONFIG dictionary to write default settings under the 'DEFAULT' section.
        self.config['DEFAULT'] = DEFAULT_CONFIG
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)

    def update(self, section, key, value):
        # Update a specific configuration value.
        self.config.read(self.filename)
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)