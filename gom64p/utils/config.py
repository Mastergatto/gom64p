#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############

import configparser
import os.path
import logging as log
import json

import wrapper.datatypes as wrp_dt

###############
## VARIABLES ##
###############

#############
## CLASSES ##
#############

class FrontendConf():
    def __init__(self, path):
        self.config = configparser.ConfigParser()
        self.config_file = f'{str(path)}{os.sep}gom64p.conf'
        self.section = 'Frontend'
        self.check()

    def default(self):
        self.config['Frontend'] = {'FirstTime': 'True',
                            'Version': '0.1',
                            'M64pLib': '',
                            'PifLoad': 'False',
                            'PifNtscPath': '',
                            'PifPalPath': '',
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
                            'TrueFullscreen': 'False',
                            'Recursive': 'False'
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

    def write(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
        del configfile

    def load(self):
        self.config.read(self.config_file)

    def set(self, section, option, value):
        self.config[section][option] = value

    def get(self, section, option):
        return self.config[section][option]

    def get_bool(self, section, option):
        return self.config[section].getboolean(option)

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


class CheatsCfg():
    def __init__(self, parent):
        self.frontend = parent
        self.list = None
        self.list_default = {}
        self.directory = None
        self.file = None

    def add(self, cheatname, codes):
        codes_type = wrp_dt.m64p_cheat_code * len(codes)
        codelist = codes_type()
        for i, cheat in enumerate(codes):
            address, value, choices, selected = cheat["address"], cheat["value"], cheat["choices"], cheat["selected"]

            if choices:
                pass

            codelist[i].address = int(address, 16)
            codelist[i].value = int(value, 16)

        self.frontend.m64p_wrapper.CoreAddCheat(cheatname, codelist)

    def dispatch(self):
        if self.check() == True:
            self.read()
            for cheat in self.list["cheats"]:
                if cheat["activate"] == True:
                    self.add(cheat["name"], cheat["codes"])

    def check(self):
        return True if os.path.isfile(self.file) == True else False

    def clean(self):
        self.list = None

    def toggle(self, cheatname, boolean):
        self.frontend.m64p_wrapper.CoreCheatEnabled(cheatname, boolean)

    def translate(self, country):
        # TODO: UJ?
        if country == "J":
            return "4A"
        elif country == "U":
            return "45"
        elif country == "E":
            return "50"
        elif country == "A":
            return "55"
        elif country == "F":
            return "46"
        elif country == "D":
            return "44"
        elif country == "I":
            return "49"
        elif country == "S":
            return "53"
        else:
            log.warning("Cheats: Unknown country")


    def read(self):
        try:
            with open(self.file, 'r') as file:
                self.list = json.load(file)

        except IOError as e:
            log.error(f"Couldn't open cheat file:\n >{self.file}: {e}")

    def set_game(self, crc1, crc2, country):
        self.directory = f'{self.frontend.environment.frontend_config_dir}{os.sep}games{os.sep}{country.lower()}-{crc1}-{crc2}{os.sep}'
        if os.path.isdir(self.directory) == False:
            os.makedirs(self.directory, mode=0o755, exist_ok=True)

        self.file = f'{self.directory}cheats.cfg'

    def write(self):
        try:
            with open(self.file, 'w') as file:
                json.dump(self.list, file, indent=4)

        except IOError as e:
            log.error(f"Couldn't open cheat file:\n >{self.file}:{e}")

    def write_default(self, crc1, crc2, country):
        cheat_default = f"{self.frontend.m64p_wrapper.ConfigGetSharedDataFilepath('mupencheat.txt')}"

        header = f'{crc1}-{crc2}-C:{self.translate(country)}'.upper()

        try:
            with open(cheat_default, 'r') as file:
                # {game, {cheat name, description, {1st pair code, 2nd pair code, (1st part, 2nd part, choices if available), ...}}, next cheat, ...}
                cheat, codes, parts = [], [], []
                game, name, description = None, None, None
                found, new = False, False

                for line in file:
                    if line.startswith('crc '):
                        found = True if line[4:].rstrip("\n") == header else False
                    else:
                        if found == True:
                            if line.startswith('gn '):
                                # gn = game name
                                self.list_default["game"] = line[3:].rstrip("\n")
                            elif line.startswith(' cn '):
                                # cn = cheat name
                                if new == True:
                                    cheat.append({"name": name, "description": description, "codes": codes, "activate": False})
                                    # clear for next cheat
                                    codes = []
                                    description = None
                                new, name = True, line[3:].rstrip("\n")

                            elif line.startswith('  cd '):
                                # cd = cheat description
                                description = line[4:].rstrip("\n")
                            else:
                                #make sure to exclude every other lines that don't contain codes
                                if line.startswith('  '):
                                    parts = line[2:].split(" ", 2)
                                    if '?' in parts[1]:
                                        parts[2] = [item.split(':') for item in parts[2].split(',')] #TODO: .rstrip("\n") ?
                                    else:
                                        parts.append(None)

                                    codes += [{'address': parts[0].rstrip("\n"), 'value': parts[1].rstrip("\n"), 'choices': parts[2], 'selected': None}]

                self.list_default["cheats"] = cheat
                self.list = self.list_default
                if "game" in self.list:
                    self.write()

                self.list_default = {}

        except IOError as e:
            log.error(f"Couldn't open cheat database: {os.linesep} >{e}")

        # self.config['CoreEvents'] = 'Version': '1', #don't touch
        #                         'Kbd Mapping Stop': '27',
        #                         'Kbd Mapping Fullscreen': '0',
        #                         'Kbd Mapping Save State': '286',
        #                         'Kbd Mapping Load State': '288',
        #                         'Kbd Mapping Increment Slot': '0',
        #                         'Kbd Mapping Reset': '290',
        #                         'Kbd Mapping Speed Down': '291',
        #                         'Kbd Mapping Speed Up': '292',
        #                         'Kbd Mapping Screenshot': '293',
        #                         'Kbd Mapping Pause': '112',
        #                         'Kbd Mapping Mute': '109',
        #                         'Kbd Mapping Increase Volume': '93',
        #                         'Kbd Mapping Decrease Volume': '91',
        #                         'Kbd Mapping Fast Forward': '102',
        #                         'Kbd Mapping Frame Advance': '47',
        #                         'Kbd Mapping Gameshark': '103',
        #                         'Joy Mapping Stop': "",
        #                         'Joy Mapping Fullscreen': "",
        #                         'Joy Mapping Save State': "",
        #                         'Joy Mapping Load State': "",
        #                         'Joy Mapping Increment Slot': "",
        #                         'Joy Mapping Screenshot': "",
        #                         'Joy Mapping Pause': "",
        #                         'Joy Mapping Mute': "",
        #                         'Joy Mapping Increase Volume': "",
        #                         'Joy Mapping Decrease Volume': "",
        #                         'Joy Mapping Fast Forward': "",
        #                         'Joy Mapping Gameshark': ""
        #                         
