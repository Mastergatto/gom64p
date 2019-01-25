#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, Gdk
import os.path

import global_module as g
import wrapper.callback as cb
import widget.keysym as w_key
import external.sdl2 as sdl

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
        self.plugin_window.set_transient_for(parent)

        #self.apply_button = self.plugin_window.add_button("Apply",Gtk.ResponseType.APPLY)
        #self.apply_button.set_sensitive(False)
        self.plugin_window.add_button("Cancel",Gtk.ResponseType.CANCEL)
        self.plugin_window.add_button("OK",Gtk.ResponseType.OK)

        if self.section == 'SDL_input':
            self.input_tabs()
            self.plugin_window.set_default_size(480, 550)
        elif self.section == 'input-sdl':
            self.input_config()
            self.plugin_window.set_default_size(550, 480)
            self.plugin_window.connect("key-press-event", self.on_key_events)
            self.plugin_window.connect("key-release-event", self.on_key_events)
        else:
            self.plugin_window.set_default_size(480, 550)
            self.generic(self.section)

        self.plugin_window.show_all()

        response = Gtk.ResponseType.APPLY
        while response == Gtk.ResponseType.APPLY:
            if sdl.SDL_WasInit(sdl.SDL_INIT_JOYSTICK):
                sdl.SDL_QuitSubSystem(sdl.SDL_INIT_JOYSTICK)
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
        if self.section == 'SDL_input' or self.section == 'input-sdl':
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
        #print(cb.parameters['Input-SDL-Control1'])

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

    def input_page(self, section):
        grid = Gtk.Grid()
        grid.set_hexpand(True)
        #grid.set_halign(Gtk.Align.FILL)

        g.m64p_wrapper.ConfigOpenSection(section)
        g.m64p_wrapper.ConfigListParameters()
        parameters = cb.parameters[section]

        mode_label = Gtk.Label("Mode:")
        mode_combo = Gtk.ComboBoxText()
        mode_combo.set_hexpand(True)
        mode_combo.set_halign(Gtk.Align.FILL)
        mode_combo.append('0',"Fully manual")
        mode_combo.append('1',"Auto with named SDL Device")
        mode_combo.append('2',"Fully automatic")

        if g.m64p_wrapper.ConfigGetParameter('mode') != None:
            mode_combo.set_active_id(str(g.m64p_wrapper.ConfigGetParameter('mode')))
            mode_combo.set_tooltip_text(g.m64p_wrapper.ConfigGetParameterHelp('mode'))
        mode_combo.connect('changed', self.on_combobox_changed, section, 'mode')

        plugged = Gtk.ToggleButton()
        plugged.set_label("Unplugged")

        pak_combo = Gtk.ComboBoxText()
        pak_combo.append('1',"None")
        pak_combo.append('2',"Memory Pak")
        #pak_combo.append('3',"")
        pak_combo.append('4',"Transfer Pak")
        pak_combo.append('5',"Rumble Pak")

        if g.m64p_wrapper.ConfigGetParameter('plugin') != None:
            pak_combo.set_active_id(str(g.m64p_wrapper.ConfigGetParameter('plugin')))
            pak_combo.set_tooltip_text(g.m64p_wrapper.ConfigGetParameterHelp('plugin'))
        pak_combo.connect('changed', self.on_combobox_changed, section, 'plugin')

        device_label = Gtk.Label("Device:")
        device_combo = Gtk.ComboBoxText()
        device_combo.append('-1',"Keyboard")
        if g.m64p_wrapper.ConfigGetParameter('name') != "Keyboard":
            device_combo.append('0', g.m64p_wrapper.ConfigGetParameter('name'))
        #device_combo.append('2',"")

        if g.m64p_wrapper.ConfigGetParameter('device') != None:
            device_combo.set_active_id(str(g.m64p_wrapper.ConfigGetParameter('device')))
            device_combo.set_tooltip_text(g.m64p_wrapper.ConfigGetParameterHelp('device'))
        device_combo.connect('changed', self.on_combobox_changed, section, 'device')


        grid.attach(mode_label, 0, 0, 1, 1)
        grid.attach(mode_combo, 1, 0, 5, 1) #Gtk.PositionType.RIGHT
        grid.attach(plugged, 0, 1, 1, 1)
        grid.attach(pak_combo, 1, 1, 1, 1)
        grid.attach(device_label, 4, 1, 1, 1)
        grid.attach(device_combo, 5, 1, 1, 1)

        buttons_frame = Gtk.Frame(label="Controller buttons")

        buttons_grid = Gtk.Grid()
        buttons_grid.set_hexpand(True)
        #buttons_grid.set_vexpand(True)

        #empty = Gtk.Label.new("")
        label_a = Gtk.Label("A") # key(304)
        button_a = Gtk.Button()
        label_b = Gtk.Label("B")
        button_b = Gtk.Button()
        label_z = Gtk.Label("Z")
        button_z = Gtk.Button()
        label_l = Gtk.Label("L")
        button_l = Gtk.Button()
        label_r = Gtk.Label("R")
        button_r = Gtk.Button()
        label_start = Gtk.Label("START")
        button_start = Gtk.Button()
        label_c_up = Gtk.Label("C-UP")
        button_c_up = Gtk.Button()
        label_c_left = Gtk.Label("C-LEFT")
        button_c_left = Gtk.Button()
        label_c_right = Gtk.Label("C-RIGHT")
        button_c_right = Gtk.Button()
        label_c_down = Gtk.Label("C-DOWN")
        button_c_down = Gtk.Button()
        label_mempak = Gtk.Label("Mempak")
        button_mempak = Gtk.Button()
        label_rumble = Gtk.Label("Rumble")
        button_rumble = Gtk.Button()
        label_d_up = Gtk.Label("D-UP")
        button_d_up = Gtk.Button()
        label_d_left = Gtk.Label("D-LEFT")
        button_d_left = Gtk.Button()
        label_d_right = Gtk.Label("D-RIGHT")
        button_d_right = Gtk.Button()
        label_d_down = Gtk.Label("D-DOWN")
        button_d_down = Gtk.Button()
        x_axis_label = Gtk.Label("X axis")
        x_axis_button = Gtk.Button()
        y_axis_label = Gtk.Label("Y axis")
        y_axis_button = Gtk.Button()

        buttons_grid.attach(label_a, 0, 0, 1, 1)
        buttons_grid.attach(button_a, 1, 0, 1, 1)
        buttons_grid.attach(label_b, 0, 1, 1, 1)
        buttons_grid.attach(button_b, 1, 1, 1, 1)
        buttons_grid.attach(label_z, 0, 2, 1, 1)
        buttons_grid.attach(button_z, 1, 2, 1, 1)
        buttons_grid.attach(label_l, 0, 3, 1, 1)
        buttons_grid.attach(button_l, 1, 3, 1, 1)
        buttons_grid.attach(label_r, 0, 4, 1, 1)
        buttons_grid.attach(button_r, 1, 4, 1, 1)
        buttons_grid.attach(label_start, 0, 5, 1, 1)
        buttons_grid.attach(button_start, 1, 5, 1, 1)
        buttons_grid.attach(Gtk.Label.new("          "), 2, 0, 1, 1) #TODO: There must be a better solution
        buttons_grid.attach(label_c_up, 3, 0, 1, 1)
        buttons_grid.attach(button_c_up, 4, 0, 1, 1)
        buttons_grid.attach(label_c_left, 3, 1, 1, 1)
        buttons_grid.attach(button_c_left, 4, 1, 1, 1)
        buttons_grid.attach(label_c_right, 3, 2, 1, 1)
        buttons_grid.attach(button_c_right, 4, 2, 1, 1)
        buttons_grid.attach(label_c_down, 3, 3, 1, 1)
        buttons_grid.attach(button_c_down, 4, 3, 1, 1)
        buttons_grid.attach(label_mempak, 3, 4, 1, 1)
        buttons_grid.attach(button_mempak, 4, 4, 1, 1)
        buttons_grid.attach(label_rumble, 3, 5, 1, 1)
        buttons_grid.attach(button_rumble, 4, 5, 1, 1)
        buttons_grid.attach(Gtk.Label.new("          "), 5, 0, 1, 1)
        buttons_grid.attach(label_d_up, 6, 0, 1, 1)
        buttons_grid.attach(button_d_up, 7, 0, 1, 1)
        buttons_grid.attach(label_d_left, 6, 1, 1, 1)
        buttons_grid.attach(button_d_left, 7, 1, 1, 1)
        buttons_grid.attach(label_d_right, 6, 2, 1, 1)
        buttons_grid.attach(button_d_right, 7, 2, 1, 1)
        buttons_grid.attach(label_d_down, 6, 3, 1, 1)
        buttons_grid.attach(button_d_down, 7, 3, 1, 1)
        buttons_grid.attach(x_axis_label, 6, 4, 1, 1)
        buttons_grid.attach(x_axis_button, 7, 4, 1, 1)
        buttons_grid.attach(y_axis_label, 6, 5, 1, 1)
        buttons_grid.attach(y_axis_button, 7, 5, 1, 1)

        buttons_frame.add(buttons_grid)
        grid.attach(buttons_frame, 0, 2, 5, 1)

        other_frame = Gtk.Frame(label="Other options")
        other_grid = Gtk.Grid()
        other_grid.set_hexpand(True)

        mouse_checkbox = Gtk.CheckButton.new_with_label("Mouse")
        if g.m64p_wrapper.ConfigGetParameter("Mouse") == True:
            mouse_checkbox.set_active(True)
        mouse_checkbox.connect("toggled", self.on_CheckboxToggled, section, "Mouse", None)
        mouse_checkbox.set_tooltip_text(g.m64p_wrapper.ConfigGetParameterHelp("Mouse"))
        #MouseSensitivity, AnalogDeadzone, AnalogPeak,

        other_grid.attach(mouse_checkbox, 0, 0, 1, 1)
        other_frame.add(other_grid)
        grid.attach(other_frame, 0, 3, 5, 1)

        #if len(value_param) == 0:
        #    empty = Gtk.Label("No option have been found here!")
        #    grid.attach(empty, 0, 0, 1, 1)
        scroll = Gtk.ScrolledWindow()
        scroll.add(grid)
        scroll.set_propagate_natural_height(True)

        return scroll

    def input_config(self):
        sdl.SDL_InitSubSystem(sdl.SDL_INIT_JOYSTICK)

        input_notebook = Gtk.Notebook()
        input_notebook.set_vexpand(True)

        # Tab "Player 1"#
        player1_tab = Gtk.Label(label="Player1")
        player1_box = Gtk.VBox()

        area_input1 = self.input_page('Input-SDL-Control1')
        player1_box.pack_start(area_input1, False, False, 0)

        input_notebook.append_page(player1_box, player1_tab)

        # Tab "Player 2"
        player2_tab = Gtk.Label(label="Player2")
        player2_box = Gtk.VBox()

        area_input2 = self.input_page('Input-SDL-Control2')
        player2_box.pack_start(area_input2, False, False, 0)

        input_notebook.append_page(player2_box, player2_tab)

        # Tab "Player 3"
        player3_tab = Gtk.Label(label="Player3")
        player3_box = Gtk.VBox()

        area_input3 = self.input_page('Input-SDL-Control3')
        player3_box.pack_start(area_input3, False, False, 0)

        input_notebook.append_page(player3_box, player3_tab)

        # Tab "Player 4"
        player4_tab = Gtk.Label(label="Player4")
        player4_box = Gtk.VBox()

        area_input4 = self.input_page('Input-SDL-Control4')
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
        if array != None:
            array[param] = value
        g.m64p_wrapper.ConfigSetParameter(param, value)
        print(section, array)

    def on_combobox_changed(self, widget, section, param):
        self.is_changed = True
        #self.widget.set_sensitive(True)
        widget_id = widget.get_active_id()

        g.m64p_wrapper.ConfigOpenSection(section)
        g.m64p_wrapper.ConfigSetParameter(param, int(widget_id))
        #else:
        #    print("Config: Unknown parameter.")

    def on_spinbutton_changed(self, widget, section, param):
        self.is_changed = True
        #self.apply_button.set_sensitive(True)
        if section != None:
            g.m64p_wrapper.ConfigOpenSection(section)
            g.m64p_wrapper.ConfigSetParameter(param, widget.get_value_as_int())

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
        # TODO: Temporary until the new input dialog is ready
        if active_plugin == "input-sdl":
            return "SDL_input"
        else:
            return active_plugin

    def on_key_events(self, widget, event):
        if event.get_event_type() == Gdk.EventType.KEY_PRESS:
            print(event.hardware_keycode)
            print(w_key.keysym2sdl(event.hardware_keycode).name)
            #g.m64p_wrapper.send_sdl_keydown(w_key.keysym2sdl(event.hardware_keycode).value)
        elif event.get_event_type() == Gdk.EventType.KEY_RELEASE:
            #g.m64p_wrapper.send_sdl_keyup(w_key.keysym2sdl(event.hardware_keycode).value)
            pass
        return True
