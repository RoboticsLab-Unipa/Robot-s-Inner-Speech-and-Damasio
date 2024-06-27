# coding=utf-8
"""
    Handle Log file and record in Model's simulation.

    (C) 2022 Sophia Corvaia, University of Palermo, Palermo, Italy
    Released under GNU Public License (GPL)
    Contacts: sophia.corvaia@unipa.it
"""
from os import listdir
from datetime import datetime
from os.path import isfile, isdir
from os import mkdir
from typing import Optional
from pathlib import Path

from termcolor import colored

from pandas import read_csv, DataFrame, concat


class Logger:
    """Class handling message logs"""

    def __init__(self, filename: str = None, signal=None) -> None:
        """Constructor method

        :param filename: Log filename
        :type filename: basestring
        :param signal: Signal emit graphic window
        :rtype: None
        """
        self.filename = filename
        self.path = 'log/'
        if not isdir(self.path):
            mkdir(self.path)
        if filename is None:
            self.filename = self.path + "Log_" + datetime.today().strftime('%Y-%m-%d') + ".log"
        elif type(filename) is not str:
            raise TypeError("Incorrect type parameter! Required str, received {} instead!".format(type(filename)))
        self.signal = signal

    def info(self, message: str = '', module: str = '') -> None:
        """ Show Info message log on terminal

        :param message: Log Message
        :type message: str
        :param module: Model's block
        :type module: str
        :return: None
        """
        time_record = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        print(("{} ".format(time_record) + colored(" | ", 'green') + colored("INFO", "blue") + colored(" | ", 'green')
               + colored(" {} {}", "blue").format(message, module)))
        self.write(message, module, 'INFO')
        if self.signal is not None:
            self.signal.emit("| INFO | {} {}".format(message, module))

    def critical(self, message: str = '', module: str = '') -> None:
        """ Show Critical message log on terminal

        :param message: Log Message
        :type message: str
        :param module: Model's block
        :type module: str
        :return: None
        """
        time_record = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        print(("{} ".format(time_record) + colored(" | ", 'green') + colored("CRITICAL", "red") + colored(" | ", 'green')
             + colored(" {} {}", "red").format(message, module)))
        self.write(message, module, 'CRITICAL')
        if self.signal is not None:
            self.signal.emit("| CRITICAL | {} {}".format(message, module))

    def error(self, message: str = '', module: str = '') -> None:
        """ Show Error message log on terminal

        :param message: Message to be shown
        :type message: str
        :param module: Model's block
        :type module: str
        :return: None
        """
        time_record = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        print(("{} ".format(time_record) + colored(" | ", 'green') + colored("ERROR", "grey", "on_red") +
               colored(" | ", 'green') + colored(" {} {}", "grey", "on_red").format(message, module)))
        self.write(message, module, 'ERROR')
        if self.signal is not None:
            self.signal.emit("| ERROR | {} {}".format(message, module))

    def warning(self, message: str = '', module: str = '') -> None:
        """ Show Warning message log on terminal

        :param message: Message to be shown
        :type message: str
        :param module: Model's block
        :type module: str
        :return: None
        """
        time_record = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        print(("{} ".format(time_record) + colored(" | ", 'green') + colored("WARNING", "yellow") +
               colored(" | ", 'green') + colored(" {} {}", "yellow").format(message, module)))
        self.write(message, module, 'WARNING')
        if self.signal is not None:
            self.signal.emit("| WARNING | {} {}".format(message, module))

    def write(self, message: str, module: str = '', code: str = '') -> str:
        """Write new log line in filename

        :param message: Log Message
        :type message: str
        :param module: Model's block
        :type module: str
        :param code: Message Log Code
        :type code: str
        :return: New registered record
        :rtype: str
        """
        if type(message) is not str:
            raise TypeError(
                "Type message parameter incorrect! Required str. Received {} instead!".format(type(message)))
        if type(code) is not str:
            raise TypeError("Type code parameter incorrect! Required str. Received {} instead!".format(type(code)))
        if type(module) is not str:
            raise TypeError("Type module parameter incorrect! Required str. Received {} instead!".format(type(module)))

        try:
            if not isfile(self.filename):
                with open(self.filename, 'w') as log_file:
                    log_file.write("datetime;message;module;code\n")

            with open(self.filename, 'a') as log_file:
                record = datetime.today().strftime('%Y-%m-%d %H:%M:%S') \
                         + ";" + message + ";" + module + ";" + code + "\n"
                log_file.write(record)
            return record
        except RuntimeError as e:
            print("LOG FILE: Cannot write %s %s. Error was here: %s" % (message, code, str(e)))
            return ''

    def find(self, search: dict, filename: str = None) -> Optional[DataFrame]:
        """
        Find records in log file based on search parameter. Return False if record is not found

        :param search: Elements to be search. Result will be search in form key-value couple
        :type search: dict
        :param filename: Log filename where execute search. If not specified, will be search in all files
        :type filename: str
        :return: Record to be search
        :rtype: DataFrame
        """
        if type(search) is not dict:
            raise TypeError('Incorrect type search parameter! Required dict. Received {} instead!'.format(type(search)))

        fields = list(search.keys())
        keys = ['datatime', 'module', 'code', 'message']
        for field in fields:
            if field not in keys:
                raise ValueError("Invalid Key search element {}! List of allowable keys: {}".format(field, keys))
        values = list(search.values())

        if not all(isinstance(value, str) for value in values):
            raise TypeError("Incorrect value type search element! Required only str. Check parameters")
        log_list = []

        if filename is not None:
            self.__check_file_exists(filename)
            log_list.append(filename)
        else:
            for log_file in listdir(self.path):
                file_extension = Path(log_file).suffix
                if file_extension == '.log':
                    log_list.append(self.path + log_file)

        query = ""
        for field, value in zip(fields, values):
            query = query + "{} == (".format(field)
            if type(value) is list:
                for val in value:
                    query = query + "'{}',".format(val)
                query = query[: -1] + ")"
            else:
                query = query + "'{}')".format(value)
            query = query + " or "
        query = query[: -4]

        results = DataFrame()
        for log_file in log_list:
            log_csv = read_csv(log_file).astype(str)
            df_query = log_csv.query(query)
            results = concat([results, df_query], axis=0)

        if results.empty:
            return None
        return results

    def __check_file_exists(self, filename: str = None) -> None:
        """Check existing file log

        :param filename: Log file to be checked
        :type filename: basestring
        :raise FileExistsError: if file doesn't exist
        """
        if filename is None:
            filename = self.filename
        if not isfile(filename):
            raise FileExistsError(filename + ": cannot open! File not found!")
        file_extension = Path(filename).suffix
        if file_extension != '.log':
            raise TypeError("Required .log file! Received {} instead!".format(file_extension))
