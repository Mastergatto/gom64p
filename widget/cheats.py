#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk
import os.path

import global_module as g
import widget.dialog as w_dialog
import widget.plugin as w_plugin

#############
## CLASSES ##
#############


class CheatsDialog(Gtk.Dialog):
    def __init__(self, parent):
        self.cheats_window = Gtk.Dialog()
        self.cheats_window.set_properties(self, title="Cheats")
        self.cheats_window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.cheats_window.set_default_size(480, 550)
        self.cheats_window.set_transient_for(parent)

        self.apply_button = self.cheats_window.add_button("Apply",Gtk.ResponseType.APPLY)
        self.apply_button.set_sensitive(False)
        self.cheats_window.add_button("Cancel",Gtk.ResponseType.CANCEL)
        self.cheats_window.add_button("OK",Gtk.ResponseType.OK)

        #player1_rom = self.insert_entry(self, param, section, config, placeholder, help)
        grid = Gtk.Grid()
        value_param = {}
        counter = 0

        #g.m64p_wrapper.ConfigOpenSection(section)
        #g.m64p_wrapper.ConfigListParameters()




        self.cheats_window.show_all()

        response = Gtk.ResponseType.APPLY
        while response == Gtk.ResponseType.APPLY:
            response = self.cheats_window.run()
            if response == Gtk.ResponseType.OK:


                self.cheats_window.destroy()
            elif response == Gtk.ResponseType.APPLY:
                if self.is_changed == True:
                    pass

            else:
                self.cheats_window.destroy()

    def insert_entry(self, param, section, config, placeholder, help):
        #TODO: Erase it
        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        entry.set_hexpand(True)
        if config == "frontend":
            if g.frontend_conf.get(param) != None:
                entry.set_text(g.frontend_conf.get(param))
        elif config == "m64p":
            if g.m64p_wrapper.ConfigGetParameter(param) != None:
                entry.set_text(g.m64p_wrapper.ConfigGetParameter(param))
        entry.connect("changed", self.on_EntryChanged, section, param)
        return entry

    def on_EntryChanged(self, widget, section, param):
        #TODO: Erase it
        self.is_changed = True
        self.apply_button.set_sensitive(True)
        value = widget.get_text()
        if section == "Frontend" or section == "GameDirs":
            g.frontend_conf.open_section(section)
            g.frontend_conf.set(param, value)
        else:
            g.m64p_wrapper.ConfigOpenSection(section)
            g.m64p_wrapper.ConfigSetParameter(param, value)
