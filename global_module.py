#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############

import utils.config as u_conf
import utils.platforms as u_plat
import wrapper.functions as w

###############
## VARIABLES ##
###############
m64p_dir = None
parameters = {}

# This frontend is fully compliant with latest api.
parameters['api_version'] = 0x020102

frontend_conf = u_conf.FrontendConf()

parameters['m64plib'] = frontend_conf.get('m64plib')
parameters['pluginsdir'] = frontend_conf.get('PluginsDir')
parameters['configdir'] = frontend_conf.get('ConfigDir')
parameters['datadir'] = frontend_conf.get('DataDir')

parameters['gfx'] = frontend_conf.get('GfxPlugin')
parameters['audio'] = frontend_conf.get('AudioPlugin')
parameters['input'] = frontend_conf.get('InputPlugin')
parameters['rsp'] = frontend_conf.get('RSPPlugin')

u_plat.Platform()
m64p_wrapper = w.API(parameters)

running = False
lock = m64p_wrapper.lock # if m64+ library isn't found
CB_STATE = None
cache = None
