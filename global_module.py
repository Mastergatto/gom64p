#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############

#import utils.config as u_conf
#import utils.platforms as u_plat
#import wrapper.functions as w

###############
## VARIABLES ##
###############
m64p_dir = None

m64p_wrapper = None
lock = None # if m64+ library isn't found
parameters = None

running = False
cache = None
