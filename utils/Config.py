# coding=utf-8
"""
    Class utilities from manage common models in the entire project

     (C) 2022 Sophia Corvaia, University of Palermo, Palermo, Italy
    Released under GNU Public License (GPL)
    Contacts: sophia.corvaia@unipa.it
"""
from os.path import dirname, join
from configparser import ConfigParser
from pathlib import Path
from typing import Optional


class ConfigHandle:
    """Class for handle project's config file."""

    def __init__(self, file_ini: str = None) -> None:
        """Constructor method.

        :param file_ini: Config file ini name. File MUST be in project's directory 'config'
        :type file_ini: str
        """
        self.config = ConfigParser()

        try:
            if file_ini is None:
                self.file_ini = 'config.ini'
            else:
                self.file_ini = file_ini
                file_extension = Path(file_ini).suffix
                if file_extension != '.ini':
                    raise TypeError("Required .ini file! Received {} instead!".format(file_extension))
            script_dir = dirname(__file__)  # Absolute dir the script is in
            rel_path = "../config/" + self.file_ini
            abs_file_path = join(script_dir, rel_path)
            self.config.read(abs_file_path)
        except Exception as ex:
            raise Exception("Exception: {}".format(ex), self.__class__.__name__)

    def get_option(self, section: str, option: str) -> Optional[str]:
        """Get option from a section in ini file

        :param section: section part of the ini file
        :type section: str
        :param option: option parameter of the ini file to be retrieved
        :type option: str
        :return: Parameter value (if present), None instead
        :rtype: Union[str, None]
        """
        if self.config.has_option(section, option):
            return self.config.get(section, option)
        return None

    def get_default_knowledge(self) -> Optional[str]:
        """Get default knowledge value from ini file if present

        :return: Parameter value (if present), None instead
        :rtype: Union[str, None]
        """
        if self.config.has_option('setting', 'default_knowledge'):
            return self.config.get('setting', 'default_knowledge')
        return None

    def get_default_individual(self) -> Optional[str]:
        """Get default individual value from ini file if present

        :return: Parameter value (if present), None instead
        :rtype: Union[str, None]
        """
        if self.config.has_option('setting', 'default_individual'):
            return self.config.get('setting', 'default_individual')
        return None
