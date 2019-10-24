#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk

#############
## CLASSES ##
#############


class Cheats:
    def __init__(self, parent):
        self.parent = parent
        self.cheat_list = {}

    def page(self):
        grid = Gtk.Grid()
        lb_cheats = Gtk.ListBox()
        tv_codes = Gtk.TreeView()

        return grid


    def parse(self):
        cheat_fn = f"{self.parent.m64p_wrapper.ConfigGetSharedDataFilepath('mupencheat.txt')}"
        crc1 = '635a2bff' #TODO: crc1, crc2 and country are hardcoded for Super Mario 64 (USA), change them later
        crc2 = '8b022326'
        country = 45 #4A = Jap, 45= U, 50 = E, 55 = A, 46 = F, 44 = D, 49 = I, 53 = S || & 0xff is needed?

        header = f'{crc1}-{crc2}-C:{country}'.upper()

        try:
            with open(cheat_fn, 'r') as file:
                # [game, [cheat name, description, {1st pair code, 2nd pair code, (1st part, 2nd part, choices if available), ...}], next cheat, ...]
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
                                self.cheat_list["game"] = line[3:].rstrip("\n")
                            elif line.startswith(' cn '):
                                # cn = cheat name
                                if new == True:
                                    cheat.append([name, description, codes])
                                    # clear for next cheat
                                    codes = None
                                new, name = True, line[3:].rstrip("\n")

                            elif line.startswith('  cd '):
                                # cd = cheat description
                                description = line[4:].rstrip("\n")
                            else:
                                #excludes every line that doesn't contain codes
                                if line.startswith('  '):
                                    parts = line[2:].rstrip("\n").split(" ", 2)
                                    if '?' in parts[1]:
                                        parts[2] = [item.split(':') for item in parts[2].split(',')]
                                    else:
                                        parts.append(None)

                                    codes = {'first':parts[0], 'second':parts[1], 'choices':parts[2]}

                self.cheat_list["cheats"] = cheat

        except IOError as e:
            print(f"Couldn't open cheat database:")
            print(">", e)
