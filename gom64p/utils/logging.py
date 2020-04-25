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

class Logger:
    def __init__(self):
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        format = '[%(asctime)s] %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s'
        date_format = '%Y-%m-%d, %H:%M:%S'
        log.basicConfig(format=format, datefmt=date_format, level=log.INFO)
        self.logger = log.getLogger()

    def set_level(self, level):
        self.logger.setLevel(level)
