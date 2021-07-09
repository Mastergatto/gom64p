#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk
import os
import logging as log

#############
## CLASSES ##
#############


class Cheats:
    def __init__(self, parent):
        self.frontend = parent
        self.handler = self.frontend.cheats
        self.cheat_list = None

    def page(self, crc1, crc2, country):
        grid = Gtk.Grid()

        self.handler.set_game(crc1, crc2, country)
        if self.handler.check() == True:
            self.handler.read()
        else:
            self.handler.write_default(crc1, crc2, country)

        game = self.handler.list["game"] if "game" in self.handler.list else "Unknown"
        lb_cheats = Gtk.ListBox()
        tv_codes = Gtk.TreeView()

        j = 0
        for i in self.handler.list["cheats"]:
            lb_row = Gtk.ListBoxRow()
            lb_row.set_tooltip_text(i["description"])

            lb_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            lb_row.set_child(lb_hbox)
            checkbox = Gtk.CheckButton()
            if i["activate"] == True:
                checkbox.set_active(True)
            checkbox.connect("toggled", self.on_checkbox_toggled, j)
            lb_hbox.append(checkbox)

            if i["codes"][0]["choices"]:
                pass
            else:
                label = Gtk.Label(label=i["name"], xalign=0)
                lb_hbox.append(label)

                edit = Gtk.Button(label="Edit")#, always_show_image=True)
                #lb_hbox.pack_start(edit, False, False, 0)

                remove_img = Gtk.Image()
                remove_img.set_from_icon_name("list-remove-symbolic")#, Gtk.IconSize.BUTTON)
                remove_button = Gtk.Button(label="")#, image=remove_img, always_show_image=True)
                remove_button.set_child(remove_img)
                #lb_hbox.pack_start(remove_button, False, True, 0)

                lb_cheats.append(lb_row)
            j += 1

        add_img = Gtk.Image()
        add_img.set_from_icon_name("list-add-symbolic")#, Gtk.IconSize.BUTTON)
        add_button = Gtk.Button(label="")#, image=add_img, always_show_image=True)
        add_button.set_child(add_img)

        #lb_cheats.add(add_button)

        if game:
            grid.attach(Gtk.Label(label=f'{game} ({crc1}-{crc2})'), 0, 0, 1, 1)
        grid.attach(lb_cheats, 0, 1, 1, 1)
        grid.attach(tv_codes, 0, 2, 1, 1)

        scroll = Gtk.ScrolledWindow()
        scroll.set_child(grid)
        scroll.set_propagate_natural_height(True)
        scroll.set_propagate_natural_width(True)

        return scroll

    def on_checkbox_toggled(self, widget, index):
        #self.is_changed = True
        #self.apply_button.set_sensitive(True)
        if widget.get_active() == True:
            self.handler.list["cheats"][index]["activate"] = True
        elif widget.get_active() == False:
            self.handler.list["cheats"][index]["activate"] = False
        else:
            log.error("Cheats: Unexpected error")
