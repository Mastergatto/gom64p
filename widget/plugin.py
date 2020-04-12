#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import os.path, threading, time, pathlib

import wrapper.callback as cb
import widget.keysym as w_key
import sdl2 as sdl

#############
## CLASSES ##
#############
class BindDialog(Gtk.MessageDialog):
    def __init__(self, parent, widget, device, label, controller):
        Gtk.MessageDialog.__init__(self)
        text = "Press any key or button for '" + label + "'. \n Press Backspace to erase its value. \n Press Escape to close without bind."
        self.parent = parent
        self.key_pressed = None
        self.desired_gamepad = controller
        self.gamepad_pressed = None
        self.gamepad_type = None
        self.pending = False

        # Reset those variables to make sure that they stay on None when calling poll_sdl_events()
        self.parent.gamepad_input = None
        self.parent.gamepad_pressed = None
        self.parent.gamepad_type = None

        self.set_markup(text)
        self.connect("key-press-event", self.on_key_events, device)
        if device == "gamepad" and self.desired_gamepad != None:
            thread = threading.Thread(name="Binding", target=self.poll_sdl_events)
            try:
                thread.start()
            except:
                print("The binding thread has encountered an unexpected error")
                threading.main_thread()
        self.run()

    def on_key_events(self, widget, event, device):
        if device == "keyboard" or (device == "gamepad" and (event.hardware_keycode == 22 or event.hardware_keycode == 9)):
            if event.hardware_keycode != 9:
                self.key_pressed = w_key.keysym2sdl(event.hardware_keycode)
            if self.pending == True:
                self.pending = False
            else:
                self.destroy()
        return True

    def poll_sdl_events(self):
        self.pending = True
        while self.pending:
            if self.parent.gamepad_input == sdl.SDL_JoystickInstanceID(self.desired_gamepad):
                if self.parent.gamepad_pressed != None and self.parent.gamepad_type != None:
                    self.gamepad_pressed = self.parent.gamepad_pressed
                    self.gamepad_type = self.parent.gamepad_type
                    self.pending = False
        self.destroy()

class PluginDialog(Gtk.Dialog):
    def __init__(self, parent, section):
        self.parent = parent
        self.section = None
        self.former_values = None
        #self.former_update()
        self.is_changed = False
        self.page_check = [False, False, False, False]
        #self.map_controls = {}
        self.scale_factor = parent.get_scale_factor()

        # SDL
        self.pending = True
        self.gamepad_input = None
        self.gamepad_pressed = None
        self.gamepad_type = None

        if section == 'gfx':
            self.section = self.get_section(self.parent.m64p_wrapper.gfx_filename)
        elif section == 'audio':
            self.section = self.get_section(self.parent.m64p_wrapper.audio_filename)
        elif section == 'input':
            self.section = self.get_section(self.parent.m64p_wrapper.input_filename)
        elif section == 'rsp':
            self.section = self.get_section(self.parent.m64p_wrapper.rsp_filename)

        title = self.section + " configuration"
        self.plugin_window = Gtk.Dialog()
        self.plugin_window.set_properties(self, title=title)
        self.plugin_window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.plugin_window.set_transient_for(parent)

        #self.apply_button = self.plugin_window.add_button("Apply",Gtk.ResponseType.APPLY)
        #self.apply_button.set_sensitive(False)
        self.plugin_window.add_button("Cancel",Gtk.ResponseType.CANCEL)
        self.plugin_window.add_button("OK",Gtk.ResponseType.OK)

        if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
            if self.section == 'input-sdl':
                self.plugin_window.set_default_size(550 * self.scale_factor, 480 * self.scale_factor)
                self.input_config()
                #self.plugin_window.connect("key-press-event", self.on_key_events)
                #self.plugin_window.connect("key-release-event", self.on_key_events)
            else:
                self.plugin_window.set_default_size(480 * self.scale_factor, 550 * self.scale_factor)
                self.generic(self.section)
        else:
            label = Gtk.Label("Mupen64plus' core library is incompatible, please upgrade it.")
            dialog_box = self.plugin_window.get_content_area()
            dialog_box.add(label)

        self.plugin_window.show_all()

        response = Gtk.ResponseType.APPLY
        while response == Gtk.ResponseType.APPLY:
            response = self.plugin_window.run()
            if response == Gtk.ResponseType.OK:
                self.parent.m64p_wrapper.ConfigSaveFile()
                #sdl.SDL_JoystickUpdate()
                self.pending = False
                if sdl.SDL_WasInit(sdl.SDL_INIT_JOYSTICK):
                    sdl.SDL_QuitSubSystem(sdl.SDL_INIT_JOYSTICK)
                if sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO):
                    sdl.SDL_QuitSubSystem(sdl.SDL_INIT_VIDEO)
                self.plugin_window.destroy()
            elif response == Gtk.ResponseType.APPLY:
                pass
            else:
                if self.section == 'input-sdl':
                    if self.parent.m64p_wrapper.ConfigHasUnsavedChanges("Input-SDL-Control1") == 1:
                        self.parent.m64p_wrapper.ConfigRevertChanges("Input-SDL-Control1")
                    if self.parent.m64p_wrapper.ConfigHasUnsavedChanges("Input-SDL-Control2") == 1:
                        self.parent.m64p_wrapper.ConfigRevertChanges("Input-SDL-Control2")
                    if self.parent.m64p_wrapper.ConfigHasUnsavedChanges("Input-SDL-Control3") == 1:
                        self.parent.m64p_wrapper.ConfigRevertChanges("Input-SDL-Control3")
                    if self.parent.m64p_wrapper.ConfigHasUnsavedChanges("Input-SDL-Control4") == 1:
                        self.parent.m64p_wrapper.ConfigRevertChanges("Input-SDL-Control4")
                else:
                    if self.parent.m64p_wrapper.ConfigHasUnsavedChanges(self.section) == 1:
                        self.parent.m64p_wrapper.ConfigRevertChanges(self.section)
                self.pending = False
                if sdl.SDL_WasInit(sdl.SDL_INIT_JOYSTICK):
                    sdl.SDL_QuitSubSystem(sdl.SDL_INIT_JOYSTICK)
                if sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO):
                    sdl.SDL_QuitSubSystem(sdl.SDL_INIT_VIDEO)
                self.plugin_window.destroy()

    def generic(self, section):
        grid = Gtk.Grid()
        value_param = {}
        counter = 0

        self.parent.m64p_wrapper.ConfigOpenSection(section)
        self.parent.m64p_wrapper.ConfigListParameters()
        parameters = cb.parameters[section]
        for parameter in parameters:
            param_type = parameters[parameter]
            if param_type == 1 or param_type == 2: #int
                value = self.parent.m64p_wrapper.ConfigGetParameter(parameter)
                value_param[parameter] = value
                label = Gtk.Label(parameter)
                entry = Gtk.Entry()
                entry.set_text(str(value))
                entry.connect("changed", self.on_EntryChanged, parameter, param_type, value_param, section)
                entry.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp(parameter))
                grid.attach(label, 0, counter, 1, 1)
                grid.attach(entry, 1, counter, 1, 1)
                counter += 1
            #elif param_type == 2: #float
            #    pass
            elif param_type == 3: #bool
                value = self.parent.m64p_wrapper.ConfigGetParameter(parameter)
                value_param[parameter] = value
                checkbox = Gtk.CheckButton.new_with_label(parameter)
                if value == True:
                    checkbox.set_active(True)
                checkbox.connect("toggled", self.on_CheckboxToggled, section, parameter, value_param)
                checkbox.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp(parameter))
                grid.attach(checkbox, 0, counter, 1, 1)
                counter += 1
            elif param_type == 4: #str
                value = self.parent.m64p_wrapper.ConfigGetParameter(parameter)
                value_param[parameter] = value
                label = Gtk.Label(parameter)
                entry = Gtk.Entry()
                entry.set_text(value)
                entry.connect("changed", self.on_EntryChanged, parameter, param_type, value_param, section)
                entry.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp(parameter))
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
        if self.section == 'input-sdl':
            return scroll
        else:
            dialog_box = self.plugin_window.get_content_area()
            dialog_box.add(scroll)

    def input_page(self, section):
        grid = Gtk.Grid()
        grid.set_hexpand(True)
        #grid.set_halign(Gtk.Align.FILL)

        self.parent.m64p_wrapper.ConfigOpenSection(section)
        self.parent.m64p_wrapper.ConfigListParameters()
        parameters = cb.parameters[section]

        mode_label = Gtk.Label("Mode:")
        self.mode_combo = Gtk.ComboBoxText()
        self.mode_combo.set_hexpand(True)
        self.mode_combo.set_halign(Gtk.Align.FILL)
        self.mode_combo.append('0',"Fully manual")
        self.mode_combo.append('1',"Auto with named SDL Device")
        self.mode_combo.append('2',"Fully automatic")

        if self.parent.m64p_wrapper.ConfigGetParameter('mode') != None:
            self.mode_combo.set_active_id(str(self.parent.m64p_wrapper.ConfigGetParameter('mode')))
            self.mode_combo.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp('mode'))
        self.mode_combo.connect('changed', self.on_combobox_changed, section, 'mode')

        plugged_button = Gtk.ToggleButton()
        if self.parent.m64p_wrapper.ConfigGetParameter('plugged') == True:
            plugged_button.set_label("Plugged")
            plugged_button.set_active(True)
        else:
            plugged_button.set_label("Unplugged")
        plugged_button.connect("toggled", self.on_toggle_button)


        pak_combo = Gtk.ComboBoxText()
        pak_combo.append('1',"None")
        pak_combo.append('2',"Memory Pak")
        #pak_combo.append('3',"")
        pak_combo.append('4',"Transfer Pak")
        pak_combo.append('5',"Rumble Pak")

        if self.parent.m64p_wrapper.ConfigGetParameter('plugin') != None:
            pak_combo.set_active_id(str(self.parent.m64p_wrapper.ConfigGetParameter('plugin')))
            pak_combo.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp('plugin'))
        pak_combo.connect('changed', self.on_combobox_changed, section, 'plugin')

        device_label = Gtk.Label("Device:")
        self.device_combo = Gtk.ComboBoxText()
        self.device_combo.insert(-1, '-1',"Keyboard")

        # For gamepads let's wait for the SDL polling, which will happen later. Meanwhile we retrieve device and name of gamepad for each player from the configuration.
        if self.parent.m64p_wrapper.ConfigGetParameter('device') != None:
            gamepad = [self.parent.m64p_wrapper.ConfigGetParameter('device'), self.parent.m64p_wrapper.ConfigGetParameter('name')]
            if self.parent.m64p_wrapper.ConfigGetParameter('device') == -1:
                self.device_combo.set_active_id(str(self.parent.m64p_wrapper.ConfigGetParameter('device')))
            self.device_combo.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp('device'))
        self.device_combo.connect('changed', self.on_combobox_changed, section, 'device')


        grid.attach(mode_label, 0, 0, 1, 1)
        grid.attach(self.mode_combo, 1, 0, 4, 1) #Gtk.PositionType.RIGHT
        grid.attach(plugged_button, 0, 1, 1, 1)
        grid.attach(pak_combo, 1, 1, 1, 1)
        grid.attach(device_label, 3, 1, 1, 1)
        grid.attach(self.device_combo, 4, 1, 1, 1)

        buttons_frame = Gtk.Frame(label="Controller buttons")

        buttons_grid = Gtk.Grid()
        #buttons_grid.set_hexpand(True)

        size = (50 * self.scale_factor)
        label_a = self.insert_image("ui/icons/ButtonIcon-N64-A.svg", size)
        button_a = self.insert_bind_button('A Button', section, "A button")
        label_b = self.insert_image("ui/icons/ButtonIcon-N64-B.svg", size)
        button_b = self.insert_bind_button('B Button',  section, "B button")
        label_z = self.insert_image("ui/icons/ButtonIcon-N64-Z.svg", size)
        button_z = self.insert_bind_button('Z Trig',  section, "Z trigger")
        label_l = self.insert_image("ui/icons/ButtonIcon-N64-L.svg", size)
        button_l = self.insert_bind_button('L Trig',  section, "L trigger")
        label_r = self.insert_image("ui/icons/ButtonIcon-N64-R.svg", size)
        button_r = self.insert_bind_button('R Trig',  section, "R trigger")
        label_start = self.insert_image("ui/icons/ButtonIcon-N64-Start.svg", size)
        button_start = self.insert_bind_button('Start',  section, "Start button")
        label_c_up = self.insert_image("ui/icons/ButtonIcon-N64-C-Up.svg", size)
        button_c_up = self.insert_bind_button('C Button U',  section, 'C↑ button')
        label_c_left = self.insert_image("ui/icons/ButtonIcon-N64-C-Left.svg", size)
        button_c_left = self.insert_bind_button('C Button L',  section, 'C← button')
        label_c_right = self.insert_image("ui/icons/ButtonIcon-N64-C-Right.svg", size)
        button_c_right = self.insert_bind_button('C Button R',  section, 'C→ button')
        label_c_down = self.insert_image("ui/icons/ButtonIcon-N64-C-Down.svg", size)
        button_c_down = self.insert_bind_button('C Button D',  section, 'C↓ button')
        label_mempak = Gtk.Label("Mempak ")
        button_mempak = self.insert_bind_button('Mempak switch',  section, "Mempak switch")
        label_rumble = Gtk.Label("Rumble ")
        button_rumble = self.insert_bind_button('Rumblepak switch',  section, "Rumblepak switch")
        label_d_up = self.insert_image("ui/icons/ButtonIcon-N64-D-Pad-U.svg", size)
        button_d_up = self.insert_bind_button("DPad U",  section, 'DPad ↑')
        label_d_left = self.insert_image("ui/icons/ButtonIcon-N64-D-Pad-L.svg", size)
        button_d_left = self.insert_bind_button("DPad L",  section, 'DPad ←')
        label_d_right = self.insert_image("ui/icons/ButtonIcon-N64-D-Pad-R.svg", size)
        button_d_right = self.insert_bind_button("DPad R",  section, 'DPad →')
        label_d_down = self.insert_image("ui/icons/ButtonIcon-N64-D-Pad-D.svg", size)
        button_d_down = self.insert_bind_button("DPad D",  section, 'DPad ↓')
        x_axis_label = self.insert_image("ui/icons/ButtonIcon-N64-Control_Stick-LR.svg", size)
        x_axis_button = self.insert_bind_button("X Axis",  section, 'X Axis', True)
        y_axis_label = self.insert_image("ui/icons/ButtonIcon-N64-Control_Stick-UD.svg", size)
        y_axis_button = self.insert_bind_button("Y Axis",  section, 'Y Axis', True)

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
        buttons_grid.attach(Gtk.Label.new("          "), 2, 0, 1, 1)
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
        if self.parent.m64p_wrapper.ConfigGetParameter("Mouse") == True:
            mouse_checkbox.set_active(True)
        mouse_checkbox.connect("toggled", self.on_CheckboxToggled, section, "Mouse", None)
        mouse_checkbox.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp("Mouse"))

        mouse_sensitivity = self.insert_double_spinbutton("MouseSensitivity", section, other_grid)
        analog_deadzone = self.insert_double_spinbutton("AnalogDeadzone", section, other_grid)
        analog_peak = self.insert_double_spinbutton("AnalogPeak", section, other_grid)

        other_grid.attach(mouse_checkbox, 0, 0, 1, 1)
        other_grid.attach(Gtk.Label("X"), 0, 1, 1, 1)
        other_grid.attach(Gtk.Label("Y"), 0, 2, 1, 1)
        other_frame.add(other_grid)
        grid.attach(other_frame, 0, 3, 5, 1)

        page = self.filter_number(section)
        self.pages_list[page] = [self.mode_combo, self.device_combo, button_a, button_b, button_z, button_l, button_r, button_start, button_c_up,
                            button_c_left, button_c_right, button_c_down, button_mempak, button_rumble, button_d_up,
                            button_d_left, button_d_right, button_d_down, x_axis_button, y_axis_button]
        self.gamepads_stored[page] = gamepad

        self.sensitive_mode(section, self.mode_combo.get_active_id())

        return grid

    def input_config(self):
        self.pages_list = [None, None, None, None, None]
        self.gamepads_stored = [None, None, None, None, None]

        input_notebook = Gtk.Notebook()
        input_notebook.set_vexpand(True)
        input_notebook.connect("switch-page", self.on_change_page)

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

        #sdl.SDL_SetHint(sdl.SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, b"1")
        sdl.SDL_InitSubSystem(sdl.SDL_INIT_VIDEO) #necessary for SDL_GetKeyFromScancode
        sdl.SDL_InitSubSystem(sdl.SDL_INIT_JOYSTICK)
        thread = threading.Thread(name="Polling", target=self.poll_sdl_events)
        try:
            thread.start()
        except:
            print("The polling thread has encountered an unexpected error")
            threading.main_thread()

    def poll_sdl_events(self):
        import ctypes as c
        sdl.SDL_JoystickEventState(sdl.SDL_ENABLE)

        self.num_gamepads = sdl.SDL_NumJoysticks()
        self.active_gamepads = {}

        while self.pending:
            event = sdl.SDL_Event()
            while sdl.SDL_PollEvent(c.byref(event)):
                if event.type == sdl.SDL_JOYBUTTONDOWN:
                    button = event.jbutton
                    self.gamepad_input = button.which
                    self.gamepad_pressed = button.button
                    self.gamepad_type = "button"
                elif event.type == sdl.SDL_JOYAXISMOTION:
                    axis = event.jaxis
                    if event.jaxis.value < -16000:
                        self.gamepad_input = axis.which
                        self.gamepad_pressed = axis.axis
                        self.gamepad_type = "Naxis"
                    elif event.jaxis.value > 16000:
                        self.gamepad_input = axis.which
                        self.gamepad_pressed = axis.axis
                        self.gamepad_type = "Paxis"
                elif event.type == sdl.SDL_JOYDEVICEADDED:
                    n = event.jdevice.which
                    device = sdl.SDL_JoystickOpen(n)
                    joy_id = sdl.SDL_JoystickInstanceID(device)
                    self.active_gamepads[joy_id] = device

                    name = sdl.SDL_JoystickName(device).decode("utf-8")

                    page = 1
                    while page < 5:
                        self.pages_list[page][1].insert(n, str(n), str(n) + ": " + name)
                        if self.gamepads_stored[page][1] == name:
                            self.pages_list[page][1].set_active_id(str(self.gamepads_stored[page][0]))
                        page += 1

                    print("Controller added: ", name)
                    print("Current active controllers: ", sdl.SDL_NumJoysticks())
                elif event.type == sdl.SDL_JOYDEVICEREMOVED:
                    joy_id = event.jdevice.which
                    device = self.active_gamepads[joy_id]
                    if sdl.SDL_JoystickGetAttached(device):
                        sdl.SDL_JoystickClose(device)

                    name = sdl.SDL_JoystickName(device).decode("utf-8")
                    page = 1
                    while page < 5:
                        if self.gamepads_stored[page][1] == name:
                            self.pages_list[page][1].set_active_id("-1")
                            self.pages_list[page][1].remove(self.gamepads_stored[page][0])
                        page += 1
                    print("Controller removed: ", name)
                    self.active_gamepads.pop(joy_id)
                    print("Current active controllers: ", sdl.SDL_NumJoysticks())

    def on_EntryChanged(self, widget, param, param_type, array, section):
        self.parent.m64p_wrapper.ConfigOpenSection(section)
        value = widget.get_text()
        if param_type == 1:
            if value != '':
                array[param] = int(value)
                self.parent.m64p_wrapper.ConfigSetParameter(param, int(value))
        elif param_type == 2:
            if value != '':
                array[param] = float(value)
                self.parent.m64p_wrapper.ConfigSetParameter(param, float(value))
        else:
            array[param] = value
            self.parent.m64p_wrapper.ConfigSetParameter(param, value)
        print(section, array)

    def on_CheckboxToggled(self, widget, section, param, array):
        #self.is_changed = True
        #self.apply_button.set_sensitive(True)
        self.parent.m64p_wrapper.ConfigOpenSection(section)
        value = widget.get_active()
        if array != None:
            array[param] = value
        self.parent.m64p_wrapper.ConfigSetParameter(param, value)
        print(section, array)

    def on_combobox_changed(self, widget, section, param):
        self.is_changed = True
        #self.widget.set_sensitive(True)
        widget_id = widget.get_active_id()

        self.parent.m64p_wrapper.ConfigOpenSection(section)
        self.parent.m64p_wrapper.ConfigSetParameter(param, int(widget_id))
        if param == "mode":
            self.sensitive_mode(section, int(widget_id))
            # Something there to reset binding?
        elif param == "device":
            if int(self.pages_list[self.filter_number(section)][0].get_active_id()) < 2:
                if int(widget_id) != -1:
                    text = widget.get_active_text()
                    self.parent.m64p_wrapper.ConfigSetParameter("name", text[3:]) # Hopefully there won't ever be more than 10 joysticks attached!
                else:
                    self.parent.m64p_wrapper.ConfigSetParameter("name", "Keyboard")
                #Something there to reset binding?
                self.parent.m64p_wrapper.ConfigSaveSection(section)
        #else:
        #    print("Config: Unknown parameter.")

    def on_spinbutton_changed(self, widget, section, param):
        self.is_changed = True
        #self.apply_button.set_sensitive(True)
        if section != None:
            self.parent.m64p_wrapper.ConfigOpenSection(section)
            self.parent.m64p_wrapper.ConfigSetParameter(param, widget.get_value_as_int())

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
        return active_plugin

    def on_change_page(self, widget, page, number):
        # When the Notebook is being realized, this signal is quickly emited four times, so we avoid to change the section uselessly.
        if self.page_check[number] == False:
            self.page_check[number] = True
        else:
            if number == 0:
                self.parent.m64p_wrapper.ConfigOpenSection('Input-SDL-Control1')
            elif number == 1:
                self.parent.m64p_wrapper.ConfigOpenSection('Input-SDL-Control2')
            elif number == 2:
                self.parent.m64p_wrapper.ConfigOpenSection('Input-SDL-Control3')
            elif number == 3:
                self.parent.m64p_wrapper.ConfigOpenSection('Input-SDL-Control4')

    def insert_bind_button(self, param, section, name, double=False):
        button = Gtk.Button()
        button.set_size_request(105 * self.scale_factor, -1)
        raw_value = self.parent.m64p_wrapper.ConfigGetParameter(param)
        #self.map_controls[param] = raw_value
        if raw_value != '':
            if self.parent.m64p_wrapper.ConfigGetParameter('name') == "Keyboard":
                raw_value = raw_value.split(',')
                if len(raw_value) == 2:
                    first_value = sdl.SDL_GetKeyName(self.filter_number(raw_value[0]))
                    second_value = sdl.SDL_GetKeyName(self.filter_number(raw_value[1]))
                    keyname = b"(" + self.purify(first_value) + b", " + self.purify(second_value) + b")"
                else:
                    keyname = self.purify(sdl.SDL_GetKeyName(self.filter_number(raw_value[0])))

                button.set_label(keyname.decode('utf-8'))
            else:
                button.set_label(raw_value)
        else:
            button.set_label("(empty)")
        button.connect("clicked", self.on_bind_key, param, section, name, double)

        return button

    def on_bind_key(self, widget, param, section, name, double):
        controller = None
        if self.parent.m64p_wrapper.ConfigGetParameter('name') == "Keyboard":
            device = "keyboard"
        else:
            device = "gamepad"
            stored_name = self.parent.m64p_wrapper.ConfigGetParameter('name')
            for joy_id, instance in self.active_gamepads.items():
                this_name = sdl.SDL_JoystickName(instance).decode("utf-8")
                if this_name == stored_name:
                    controller = self.active_gamepads[joy_id]

        # Now we start preparations for the dialog
        if double == True:
            # In case we have to bind twice in a single GUI button, e.g. for an axis of the controller
            if name == "X Axis":
                first_name = "X Axis (Left)"
                second_name = "X Axis (Right)"
            elif name == "Y Axis":
                first_name = "Y Axis (Up)"
                second_name = "Y Axis (Down)"

            first_value = self.binding(widget, param, device, first_name, controller, False)
            if first_value[1] != None:
                if first_value[0] != "" and first_value[1] != "empty":
                    if first_value[1] == "Naxis" or first_value[1] == "Paxis":
                        input_type = "axis"
                    else:
                        input_type = first_value[1]
                    different = True
                    while different:
                        # We give some time to the user to reset the control stick to zero.
                        time.sleep(0.2)
                        second_value = self.binding(widget, param, device, second_name, controller, False)
                        if second_value[1] == "Naxis" or second_value[1] == "Paxis":
                            input_type2 = "axis"
                        elif second_value[1] == None or second_value[1] == "empty":
                            break
                        else:
                            input_type2 = second_value[1]

                        if input_type == input_type2:
                            different = False
                    if second_value[1] != None:
                        if second_value[0] != "" and second_value[1] != "empty":
                            if input_type == "axis":
                                store = input_type + "(" + first_value[0] + ("+" if first_value[1] == "Paxis" else "-") + "," + second_value[0] + \
                                    ("+" if second_value[1] == "Paxis" else "-") + ")"
                                widget.set_label(store)
                                self.parent.m64p_wrapper.ConfigSetParameter(param, store)
                            elif input_type == "button":
                                store = input_type + "(" + first_value[0] + "," + second_value[0] + ")"
                                widget.set_label(store)
                                self.parent.m64p_wrapper.ConfigSetParameter(param, store)
                            elif input_type == "key":
                                widget.set_label("(" + sdl.SDL_GetKeyName(int(first_value[0])).decode("utf-8") + ", " + sdl.SDL_GetKeyName(int(second_value[0])).decode("utf-8") + ")")
                        else:
                            widget.set_label("(empty)")
                            self.parent.m64p_wrapper.ConfigSetParameter(param, second_value[0])

                else:
                    widget.set_label("(empty)")
                    self.parent.m64p_wrapper.ConfigSetParameter(param, first_value[0])
        else:
            self.binding(widget, param, device, name, controller, True)

    def insert_image(self, file, size):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(file)), size, -1, True)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        return image

    def insert_spinbutton_fragment(self, minimum, maximum, adj_step=1.0, spin_climb=1.0):
        adj_value = 0
        if adj_step < 1.0:
            digits = 2
        else:
            digits = 0

        adjustment = Gtk.Adjustment(value=adj_value, lower=minimum, upper=maximum, step_increment=adj_step)
        spin = Gtk.SpinButton.new(adjustment, spin_climb, digits)
        #spin.set_snap_to_ticks(True)
        return spin

    def insert_double_spinbutton(self, param, section, grid):
        value = self.parent.m64p_wrapper.ConfigGetParameter(param)
        if param == "MouseSensitivity":
            # Due to a possible bug, in this case the comma may be used as decimal separator AND as value separator.
            workaround = value.split(',')
            spin_values = [None, None]
            try:
                # We try to convert the comma into a period
                spin_values[0] = format(float('.'.join(workaround[:2])),'.2f')
                spin_values[1] = format(float('.'.join(workaround[2:])),'.2f')
            except:
                spin_values = workaround
            first_spin = self.insert_spinbutton_fragment(0, 32, 0.01, 0.01)
            second_spin = self.insert_spinbutton_fragment(0, 32, 0.01, 0.01)
            first_spin.set_value(float(spin_values[0]))
            second_spin.set_value(float(spin_values[1]))
        else:
            spin_values = value.split(',')
            first_spin = self.insert_spinbutton_fragment(-32768, 32768)
            first_spin.set_value(int(spin_values[0]))
            second_spin = self.insert_spinbutton_fragment(-32768, 32768)
            second_spin.set_value(int(spin_values[1]))

        first_spin.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp(param) + "\n This value refers to the axis X.")
        first_spin.connect("value-changed", self.on_double_spinbutton_changed, section, param, 0, spin_values)

        second_spin.connect("value-changed", self.on_double_spinbutton_changed, section, param, 1, spin_values)
        second_spin.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp(param) + "\n This value refers to the axis Y.")

        if param == "MouseSensitivity":
            label = Gtk.Label("Mouse sensitivity: ")
            position = 1
        elif param == "AnalogDeadzone":
            label = Gtk.Label("Analog deadzone: ")
            position = 2
        elif param == "AnalogPeak":
            label = Gtk.Label("Analog peak: ")
            position = 3
        grid.attach(label, position, 0, 1, 1)
        grid.attach(first_spin, position, 1, 1, 1)
        grid.attach(second_spin, position, 2, 1, 1)

    def on_double_spinbutton_changed(self, widget, section, param, which, spin):
        if param == "MouseSensitivity":
            spin[which] = str(format(round(widget.get_value(),2),'.2f'))
        else:
            spin[which] = str(widget.get_value_as_int())
        if section != None:
            value = ','.join(str(x) for x in spin) #.replace(".", ",")
            self.parent.m64p_wrapper.ConfigSetParameter(param, value)

    def binding(self, widget, param, device, name, controller, execute):
        dialog = BindDialog(self, widget, device, name, controller)

        if dialog.key_pressed != None:
            if dialog.key_pressed.value == 42:
                store = ""
                if execute == True:
                    widget.set_label("(empty)")
                    self.parent.m64p_wrapper.ConfigSetParameter(param, store)
                return [store, "empty"]
            else:
                value = dialog.key_pressed.value
                keycode = sdl.SDL_GetKeyFromScancode(value)
                store = "key(" + str(keycode) + ")"
                if execute == True:
                    widget.set_label(sdl.SDL_GetKeyName(keycode).decode("utf-8"))
                    self.parent.m64p_wrapper.ConfigSetParameter(param, store)
                else:
                    return [str(keycode), "key"]

        elif dialog.gamepad_pressed != None:
            value = dialog.gamepad_pressed
            if dialog.gamepad_type == "button":
                store = "button(" + str(value) + ")"
            else:
                if dialog.gamepad_type == "Naxis":
                    store = "axis(" + str(value) + "-)"
                elif dialog.gamepad_type == "Paxis":
                    store = "axis(" + str(value) + "+)"
            if execute == True:
                widget.set_label(store)
                self.parent.m64p_wrapper.ConfigSetParameter(param, store)
            else:
                return [str(value), dialog.gamepad_type]
        else:
            return ["", None]

    def on_toggle_button(self, widget):
        status = widget.get_active()
        if status == True:
            widget.set_label("Plugged")
        else:
            widget.set_label("Unplugged")
        self.parent.m64p_wrapper.ConfigSetParameter("plugged", status)

    def sensitive_mode(self, section, mode):
        page = self.filter_number(section)
        mode = int(mode)
        if mode == 0: #Manual
            self.pages_list[page][1].set_sensitive(True)
            self.pages_list[page][2].set_sensitive(True)
            self.pages_list[page][3].set_sensitive(True)
            self.pages_list[page][4].set_sensitive(True)
            self.pages_list[page][5].set_sensitive(True)
            self.pages_list[page][6].set_sensitive(True)
            self.pages_list[page][7].set_sensitive(True)
            self.pages_list[page][8].set_sensitive(True)
            self.pages_list[page][9].set_sensitive(True)
            self.pages_list[page][10].set_sensitive(True)
            self.pages_list[page][11].set_sensitive(True)
            self.pages_list[page][12].set_sensitive(True)
            self.pages_list[page][13].set_sensitive(True)
            self.pages_list[page][14].set_sensitive(True)
            self.pages_list[page][15].set_sensitive(True)
            self.pages_list[page][16].set_sensitive(True)
            self.pages_list[page][17].set_sensitive(True)
            self.pages_list[page][18].set_sensitive(True)
            self.pages_list[page][19].set_sensitive(True)
        else:
            if mode == 1: #Automatic with named device
                self.pages_list[page][1].set_sensitive(True)
            elif mode == 2: #fully automatic
                self.pages_list[page][1].set_sensitive(False)

            self.pages_list[page][2].set_sensitive(False)
            self.pages_list[page][3].set_sensitive(False)
            self.pages_list[page][4].set_sensitive(False)
            self.pages_list[page][5].set_sensitive(False)
            self.pages_list[page][6].set_sensitive(False)
            self.pages_list[page][7].set_sensitive(False)
            self.pages_list[page][8].set_sensitive(False)
            self.pages_list[page][9].set_sensitive(False)
            self.pages_list[page][10].set_sensitive(False)
            self.pages_list[page][11].set_sensitive(False)
            self.pages_list[page][12].set_sensitive(False)
            self.pages_list[page][13].set_sensitive(False)
            self.pages_list[page][14].set_sensitive(False)
            self.pages_list[page][15].set_sensitive(False)
            self.pages_list[page][16].set_sensitive(False)
            self.pages_list[page][17].set_sensitive(False)
            self.pages_list[page][18].set_sensitive(False)
            self.pages_list[page][19].set_sensitive(False)

    def filter_number(self, string):
        #alt: int(''.join(c for c in string if c.isdigit()))
        return int(''.join(filter(str.isdigit, string)))
        
    def purify(self, string):
        # Workaround: For some reason SDL doesn't return the correct name for those key, so let's correct them.
        if string == b'\xc4\xb0':
            return b"Left Shift"
        elif string == b'\xc4\xb2':
            return b"Left Ctrl"
        elif string == b'\xc4\x91':
            return b"Up"
        elif string == b'\xc4\x92':
            return b"Down"
        elif string == b'\xc4\x93':
            return b"Right"
        elif string == b'\xc4\x94':
            return b"Left"
        else:
            return string
