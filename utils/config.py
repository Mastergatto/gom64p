#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############

import configparser, os.path
import logging as log

###############
## VARIABLES ##
###############

#############
## CLASSES ##
#############

class Configuration():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = None
        self.section = None

    def default(self):
        self.config = {}
        self.write()

    def write(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
        del configfile

    def load(self):
        self.config.read(self.config_file)

    def set(self, option, value):
        self.config[self.section][option] = value

    def get(self, option):
        return self.config[self.section][option]

    def get_bool(self, option):
        return self.config[self.section].getboolean(option)

    def check(self):
        if os.path.isfile(self.config_file) == True:
            try:
                self.load()
            except:
                log.warning("Cannot load", self.config_file)
        else:
            self.default()
            log.warning(f"{self.config_file} NOT found! Creating new config file.")

    def open_section(self, section):
        self.section = section



class FrontendConf(Configuration):
    def __init__(self, path):
        self.config = configparser.ConfigParser()
        self.config_file = f'{str(path)}{os.sep}gom64p.conf'
        self.section = 'Frontend'
        self.check()

    def default(self):
        self.config['Frontend'] = {'FirstTime': 'True',
                            'Version': '0.1',
                            'M64pLib': '',
                            'PluginsDir': '',
                            'ConfigDir': '',
                            'DataDir': '',
                            'LastPosition': '',
                            'ToolbarConfig': 'True',
                            'FilterConfig': 'True',
                            'StatusConfig': 'True',
                            'Language': '0',
                            'GfxPlugin': 'mupen64plus-video-glide64mk2',
                            'AudioPlugin': 'mupen64plus-audio-sdl',
                            'InputPlugin': 'mupen64plus-input-sdl',
                            'RSPPlugin': 'mupen64plus-rsp-hle',
                            'VidExt': 'True',
                            'LogLevel': '20',
                            'TrueFullscreen': 'False'
                            }
        self.config['GameDirs'] = {'path1': '',
                            'path2': '',
                            'path3': '',
                            'path4': '',
                            'path5': '',
                            'path6': '',
                            'path7': '',
                            'path8': '',
                            'path9': '',
                            'path10': '',
                            'path64dd': ''
                            }

        self.write()


class M64pConf(Configuration):
    #TODO: Erase
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = 'config/mupen64plus.cfg'
        #self.Sections = ['Core', 'CoreEvents']
        self.check()

    def set(self, section, option, value):
        self.config[section][option] = value

    def get(self, section, option):
        return self.config[section][option]

    def get_bool(self, section, option):
        return self.config[section].getboolean(option)

    def default(self):
        #mupen64plus.cfg
        self.config['Core'] = {'Version': '1,010000', #float, don't touch
                        'OnScreenDisplay': 'False',
                        'R4300Emulator': '2', #int
                        'NoCompiledJump': 'False',
                        'DisableExtraMem': 'False',
                        'AutoStateSlotIncrement': 'False',
                        'EnableDebugger': 'False',
                        'CurrentStateSlot': '0', #int
                        'ScreenshotPath': "",
                        'SaveStatePath': "",
                        'SaveSRAMPath': "",
                        'SharedDataPath': "",
                        'CountPerOp': '0', #int
                        'DelaySI': 'False',
                        'DisableSpecRecomp': 'True'
                        }

        self.config['CoreEvents'] = {'Version': '1', #don't touch
                                'Kbd Mapping Stop': '27',
                                'Kbd Mapping Fullscreen': '0',
                                'Kbd Mapping Save State': '286',
                                'Kbd Mapping Load State': '288',
                                'Kbd Mapping Increment Slot': '0',
                                'Kbd Mapping Reset': '290',
                                'Kbd Mapping Speed Down': '291',
                                'Kbd Mapping Speed Up': '292',
                                'Kbd Mapping Screenshot': '293',
                                'Kbd Mapping Pause': '112',
                                'Kbd Mapping Mute': '109',
                                'Kbd Mapping Increase Volume': '93',
                                'Kbd Mapping Decrease Volume': '91',
                                'Kbd Mapping Fast Forward': '102',
                                'Kbd Mapping Frame Advance': '47',
                                'Kbd Mapping Gameshark': '103',
                                'Joy Mapping Stop': "",
                                'Joy Mapping Fullscreen': "",
                                'Joy Mapping Save State': "",
                                'Joy Mapping Load State': "",
                                'Joy Mapping Increment Slot': "",
                                'Joy Mapping Screenshot': "",
                                'Joy Mapping Pause': "",
                                'Joy Mapping Mute': "",
                                'Joy Mapping Increase Volume': "",
                                'Joy Mapping Decrease Volume': "",
                                'Joy Mapping Fast Forward': "",
                                'Joy Mapping Gameshark': ""
                                }
        self.write()
