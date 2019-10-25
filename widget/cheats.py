#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk
import logging as log

#############
## CLASSES ##
#############


class Cheats:
    def __init__(self, parent):
        self.parent = parent
        self.cheat_list = {}

    def page(self):
        grid = Gtk.Grid()
        crc1, crc2 = '635a2bff', '8b022326'

        self.parse_ini(crc1, crc2, 45)
        lb_cheats = Gtk.ListBox()
        tv_codes = Gtk.TreeView()

        for i in self.cheat_list["cheats"]:
            lb_row = Gtk.ListBoxRow()
            lb_row.set_tooltip_text(i[1]) # description

            lb_hbox = Gtk.HBox()
            lb_row.add(lb_hbox)
            check = Gtk.CheckButton()
            lb_hbox.pack_start(check, False, False, 0)
            label = Gtk.Label(i[0], xalign=0) # cheat name
            lb_hbox.pack_start(label, True, True, 0)

            edit = Gtk.Button(label="Edit", always_show_image=True)
            lb_hbox.pack_start(edit, False, False, 0)

            remove_img = Gtk.Image()
            remove_img.set_from_icon_name("list-remove-symbolic", Gtk.IconSize.BUTTON)
            remove_button = Gtk.Button(label="", image=remove_img, always_show_image=True)
            lb_hbox.pack_start(remove_button, False, True, 0)

            lb_cheats.add(lb_row)

        add_img = Gtk.Image()
        add_img.set_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        add_button = Gtk.Button(label="", image=add_img, always_show_image=True)

        lb_cheats.add(add_button)

        grid.attach(Gtk.Label(f'{self.cheat_list["game"]} ({crc1}-{crc2})'), 0, 0, 1, 1)
        grid.attach(lb_cheats, 0, 1, 1, 1)
        grid.attach(tv_codes, 0, 2, 1, 1)

        scroll = Gtk.ScrolledWindow()
        scroll.add(grid)
        scroll.set_propagate_natural_height(True)
        scroll.set_propagate_natural_width(True)

        return scroll


    def parse_ini(self, crc1, crc2, country):
        cheat_fn = f"{self.parent.m64p_wrapper.ConfigGetSharedDataFilepath('mupencheat.txt')}"

        #country: 4A = Jap, 45= U, 50 = E, 55 = A, 46 = F, 44 = D, 49 = I, 53 = S || & 0xff is needed?

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
                                #make sure to exclude every other lines that don't contain codes
                                if line.startswith('  '):
                                    parts = line[2:].rstrip("\n").split(" ", 2)
                                    if '?' in parts[1]:
                                        parts[2] = [item.split(':') for item in parts[2].split(',')]
                                    else:
                                        parts.append(None)

                                    codes = {'first':parts[0], 'second':parts[1], 'choices':parts[2]}

                self.cheat_list["cheats"] = cheat

        except IOError as e:
            log.error(f"Couldn't open cheat database:\n >{e}")
