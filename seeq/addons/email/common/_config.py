import configparser
from pathlib import Path
from typing import Optional

DEFAULT_PATH = Path.home().joinpath('.seeq', 'email_function_config.ini')


class EmailConfiguration:
    def __init__(self, configfile=None, validate=True):
        self.configfile = configfile
        self.configuration_parser: Optional[configparser.ConfigParser] = None
        if validate:
            self.validate_configuration_file()

    def check_config_file_exists(self, create_if_not_exists=False):
        if self.configfile is None:
            self.configfile = DEFAULT_PATH
        if not Path(self.configfile).exists():
            if create_if_not_exists:
                with open(self.configfile, 'w'):
                    pass
                print(self.configfile)
            else:
                raise FileNotFoundError(f"File {self.configfile} could not be found.")

    def validate_configuration_file(self, create_if_not_exists=False):
        """
        Reads a configuration file and sets the global variable configuration_parser
        """
        self.check_config_file_exists(create_if_not_exists)
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(self.configfile)
        self.configuration_parser = config

    def get(self, section: str, variable: str, fallback=None):
        """
        Retrieves the value of named option from the configuration_parser. If the
        configuration_parser is not set, a fallback value can be returned.

        Parameters
        ----------
        section: str
            Name of the section in the configuration file to retrieve the value from.
        variable: str
            Name of the option whose value will be retrieved.
        fallback: object
            Object to be retrieved if configuration_parser is not set.

        Returns
        -------
        value: str
            A string value for the named option.

        """
        if not self.configuration_parser:
            return fallback
        return self.configuration_parser.get(section, variable, fallback=fallback)

    def set(self, section: str, variable: str, value: str):
        """
        Sets the value of named option from the configuration_parser. If the
        configuration_parser is not set, a fallback value can be returned.

        Parameters
        ----------
        section: str
            Name of the section in the configuration file.
        variable: str
            Name of the option whose value will be set.
        value: str
            Value of the variable that will be set.

        Returns
        -------
        value: None

        """
        self.validate_configuration_file(create_if_not_exists=True)
        if not self.configuration_parser:
            return
        if section not in self.configuration_parser.sections():
            self.configuration_parser.add_section(section)
        self.configuration_parser.set(section, variable, value)
        with open(self.configfile, 'w') as configfile:
            self.configuration_parser.write(configfile)
