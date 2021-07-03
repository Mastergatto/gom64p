#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############

import logging as log

###############
## VARIABLES ##
###############

#logging.debug('This is a debug message')
#logging.info('This is an info message')
#logging.warning('This is a warning message')
#logging.error('This is an error message')
#logging.critical('This is a critical message')

class CustomFormatter(log.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    # For codes see: https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_(Select_Graphic_Rendition)_parameters
    cyan = "\x1b[36;22m"
    white = "\x1b[37;22m"
    yellow = "\x1b[33;22m"
    red = "\x1b[31;22m"
    bold_red = "\x1b[31;4m"
    reset = "\x1b[0m"
    logformat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    date_format = '%Y-%m-%d, %H:%M:%S'
    #format = '[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s'

    FORMATS = {
        log.DEBUG: cyan + logformat + reset,
        log.INFO: white + logformat + reset,
        log.WARNING: yellow + logformat + reset,
        log.ERROR: red + logformat + reset,
        log.CRITICAL: bold_red + logformat + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = log.Formatter(log_fmt)
        return formatter.format(record)

class Logger:
    def __init__(self):
        # create logger
        self.logger = log.getLogger()
        self.logger.setLevel(log.INFO)

        # create console handler with a higher log level
        self.ch = log.StreamHandler()
        self.ch.setLevel(log.INFO)

        self.ch.setFormatter(CustomFormatter())

        self.logger.addHandler(self.ch)

    def set_level(self, level):
        self.logger.setLevel(level)
        self.ch.setLevel(level)

