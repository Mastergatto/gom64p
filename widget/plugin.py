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
import wrapper.callback as cb

#############
## CLASSES ##
#############
class PluginDialog(Gtk.Dialog):
    def __init__(self, parent, section):
        self.section = None
        self.former_values = None
        #self.former_update()
        self.is_changed = False

        if section == 'gfx':
            self.section = self.get_section(g.m64p_wrapper.gfx_filename)
        elif section == 'audio':
            self.section = self.get_section(g.m64p_wrapper.audio_filename)
        elif section == 'input':
            self.section = self.get_section(g.m64p_wrapper.input_filename)
            print(self.section)
        elif section == 'rsp':
            self.section = self.get_section(g.m64p_wrapper.rsp_filename)

        title = self.section + " config"
        self.plugin_window = Gtk.Dialog()
        self.plugin_window.set_properties(self, title=title)
        self.plugin_window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.plugin_window.set_default_size(480, 550)
        self.plugin_window.set_transient_for(parent)

        #self.apply_button = self.plugin_window.add_button("Apply",Gtk.ResponseType.APPLY)
        #self.apply_button.set_sensitive(False)
        self.plugin_window.add_button("Cancel",Gtk.ResponseType.CANCEL)
        self.plugin_window.add_button("OK",Gtk.ResponseType.OK)

        if self.section == 'SDL_input':
            self.input_tabs()
        else:
            self.generic(self.section)

        self.plugin_window.show_all()

        response = Gtk.ResponseType.APPLY
        while response == Gtk.ResponseType.APPLY:
            response = self.plugin_window.run()
            if response == Gtk.ResponseType.OK:
                g.m64p_wrapper.ConfigSaveFile()
                self.plugin_window.destroy()
            elif response == Gtk.ResponseType.APPLY:
                pass
            else:
                if self.section == 'SDL_input':
                    if g.m64p_wrapper.ConfigHasUnsavedChanges("Input-SDL-Control1") == 1:
                        g.m64p_wrapper.ConfigRevertChanges("Input-SDL-Control1")
                    if g.m64p_wrapper.ConfigHasUnsavedChanges("Input-SDL-Control2") == 1:
                        g.m64p_wrapper.ConfigRevertChanges("Input-SDL-Control2")
                    if g.m64p_wrapper.ConfigHasUnsavedChanges("Input-SDL-Control3") == 1:
                        g.m64p_wrapper.ConfigRevertChanges("Input-SDL-Control3")
                    if g.m64p_wrapper.ConfigHasUnsavedChanges("Input-SDL-Control4") == 1:
                        g.m64p_wrapper.ConfigRevertChanges("Input-SDL-Control4")
                else:
                    if g.m64p_wrapper.ConfigHasUnsavedChanges(self.section) == 1:
                        g.m64p_wrapper.ConfigRevertChanges(self.section)

                self.plugin_window.destroy()

    def generic(self, section):
        grid = Gtk.Grid()
        value_param = {}
        counter = 0

        g.m64p_wrapper.ConfigOpenSection(section)
        g.m64p_wrapper.ConfigListParameters()
        parameters = cb.parameters[section]
        for parameter in parameters:
            param_type = parameters[parameter]
            if param_type == 1 or param_type == 2: #int
                value = g.m64p_wrapper.ConfigGetParameter(parameter)
                value_param[parameter] = value
                label = Gtk.Label(parameter)
                entry = Gtk.Entry()
                entry.set_text(str(value))
                entry.connect("changed", self.on_EntryChanged, parameter, param_type, value_param, section)
                entry.set_tooltip_text(g.m64p_wrapper.ConfigGetParameterHelp(parameter))
                grid.attach(label, 0, counter, 1, 1)
                grid.attach(entry, 1, counter, 1, 1)
                counter += 1
            #elif param_type == 2: #float
            #    pass
            elif param_type == 3: #bool
                value = g.m64p_wrapper.ConfigGetParameter(parameter)
                value_param[parameter] = value
                checkbox = Gtk.CheckButton.new_with_label(parameter)
                if value == True:
                    checkbox.set_active(True)
                checkbox.connect("toggled", self.on_CheckboxToggled, section, parameter, value_param)
                checkbox.set_tooltip_text(g.m64p_wrapper.ConfigGetParameterHelp(parameter))
                grid.attach(checkbox, 0, counter, 1, 1)
                counter += 1
            elif param_type == 4: #str
                value = g.m64p_wrapper.ConfigGetParameter(parameter)
                value_param[parameter] = value
                label = Gtk.Label(parameter)
                entry = Gtk.Entry()
                entry.set_text(value)
                entry.connect("changed", self.on_EntryChanged, parameter, param_type, value_param, section)
                entry.set_tooltip_text(g.m64p_wrapper.ConfigGetParameterHelp(parameter))
                grid.attach(label, 0, counter, 1, 1)
                grid.attach(entry, 1, counter, 1, 1)
                counter += 1
            else:
                print("Unknown option, ignored")
        if len(value_param) == 0:
            empty = Gtk.Label("No option have been found here!")
            grid.attach(empty, 0, counter, 1, 1)
        scroll = Gtk.ScrolledWindow()
        scroll.add(grid)
        scroll.set_propagate_natural_height(True)

        # If there are tabs for multiple section opened in once, just return it, otherwise let's add it to dialog
        if self.section == 'SDL_input':
            return scroll
        else:
            dialog_box = self.plugin_window.get_content_area()
            dialog_box.add(scroll)

    def input_tabs(self):
        input_notebook = Gtk.Notebook()
        input_notebook.set_vexpand(True)

        # Tab "Player 1"#
        player1_tab = Gtk.Label(label="Player1")
        player1_box = Gtk.VBox()

        area_input1 = self.generic('Input-SDL-Control1')
        player1_box.pack_start(area_input1, False, False, 0)
        print(cb.parameters['Input-SDL-Control1'])

        input_notebook.append_page(player1_box, player1_tab)

        # Tab "Player 2"
        player2_tab = Gtk.Label(label="Player2")
        player2_box = Gtk.VBox()

        area_input2 = self.generic('Input-SDL-Control2')
        player2_box.pack_start(area_input2, False, False, 0)

        input_notebook.append_page(player2_box, player2_tab)

        # Tab "Player 3"
        player3_tab = Gtk.Label(label="Player3")
        player3_box = Gtk.VBox()

        area_input3 = self.generic('Input-SDL-Control3')
        player3_box.pack_start(area_input3, False, False, 0)

        input_notebook.append_page(player3_box, player3_tab)

        # Tab "Player 4"
        player4_tab = Gtk.Label(label="Player4")
        player4_box = Gtk.VBox()

        area_input4 = self.generic('Input-SDL-Control4')
        player4_box.pack_start(area_input4, False, False, 0)

        input_notebook.append_page(player4_box, player4_tab)

        dialog_box = self.plugin_window.get_content_area()
        dialog_box.add(input_notebook)

    def on_EntryChanged(self, widget, param, param_type, array, section):
        g.m64p_wrapper.ConfigOpenSection(section)
        value = widget.get_text()
        if param_type == 1:
            if value != '':
                array[param] = int(value)
                g.m64p_wrapper.ConfigSetParameter(param, int(value))
        elif param_type == 2:
            if value != '':
                array[param] = float(value)
                g.m64p_wrapper.ConfigSetParameter(param, float(value))
        else:
            array[param] = value
            g.m64p_wrapper.ConfigSetParameter(param, value)
        print(section, array)

    def on_CheckboxToggled(self, widget, section, param, array):
        #self.is_changed = True
        #self.apply_button.set_sensitive(True)
        g.m64p_wrapper.ConfigOpenSection(section)
        value = widget.get_active()
        array[param] = value
        g.m64p_wrapper.ConfigSetParameter(param, value)
        print(section, array)

    def revert(self):
        self.is_changed = False
        #self.apply_button.set_sensitive(False)
        #something here


    def former_update(self):
        self.is_changed = False
        self.former_values = {}

    def get_section(self, plugin):
        # We try to guess the name to give at the library for looking it in the .cfg, by striping off the extension
        active_plugin = os.path.splitext(plugin)[0]
        active_plugin = active_plugin.replace("mupen64plus-", "")
        if active_plugin == "input-sdl":
            return "SDL_input"
        else:
            return active_plugin
