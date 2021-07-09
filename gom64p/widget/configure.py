#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk
import os.path
import logging as log

import widget.dialog as w_dialog
import widget.plugin as w_plugin

#############
## CLASSES ##
#############

class ConfigDialog(Gtk.Dialog):
    def __init__(self, parent, unused):
        self.parent = parent
        self.former_values = {}
        self.former_update()
        self.is_changed = False

        if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
            self.parent.m64p_wrapper.plugins_shutdown()
            self.parent.m64p_wrapper.ConfigOpenSection('Core')

        self.window = Gtk.Dialog()
        self.window.set_properties(self, title="Configure")
        #self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.window.set_default_size(480, 550)
        self.window.set_transient_for(parent)
        self.window.set_modal(True)
        self.window.connect("response", self.on_response)

        self.apply_button = self.window.add_button("Apply",Gtk.ResponseType.APPLY)
        self.apply_button.set_sensitive(False)
        self.window.add_button("Cancel",Gtk.ResponseType.CANCEL)
        self.window.add_button("OK",Gtk.ResponseType.OK)

        self.config_tabs()

        self.window.show()

    def set_margin(self, widget, left, right, top, bottom):
        widget.set_margin_start(left)
        widget.set_margin_end(right)
        widget.set_margin_top(top)
        widget.set_margin_bottom(bottom)

    def on_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            self.parent.frontend_conf.write()

            if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
                self.parent.m64p_wrapper.plugins_preload()
                self.parent.m64p_wrapper.plugins_startup()
                self.parent.m64p_wrapper.ConfigSaveFile()

            self.window.destroy()
        elif response_id == Gtk.ResponseType.APPLY:
            self.parent.frontend_conf.write()
            if self.is_changed == True:
                self.apply_button.set_sensitive(False)
                self.former_update()

                if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
                    if self.parent.m64p_wrapper.ConfigHasUnsavedChanges("Core") == True:
                        self.parent.m64p_wrapper.ConfigSaveSection("Core")
                    if self.parent.m64p_wrapper.ConfigHasUnsavedChanges("CoreEvents") == True:
                        self.parent.m64p_wrapper.ConfigSaveSection("CoreEvents")
                    if self.parent.m64p_wrapper.ConfigHasUnsavedChanges("Video-General") == True:
                        self.parent.m64p_wrapper.ConfigSaveSection("Video-General")

            if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
                self.parent.m64p_wrapper.plugins_preload()

        else:
            if self.is_changed == True:
                self.revert()

                if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
                    if self.parent.m64p_wrapper.ConfigHasUnsavedChanges("Core") == True:
                        self.parent.m64p_wrapper.ConfigRevertChanges("Core")
                    if self.parent.m64p_wrapper.ConfigHasUnsavedChanges("CoreEvents") == True:
                        self.parent.m64p_wrapper.ConfigRevertChanges("CoreEvents")
                    if self.parent.m64p_wrapper.ConfigHasUnsavedChanges("Video-General") == True:
                        self.parent.m64p_wrapper.ConfigRevertChanges("Video-General")

            if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
                self.parent.m64p_wrapper.plugins_startup()
            self.window.destroy()


    def config_tabs(self):
        config_notebook = Gtk.Notebook()
        config_notebook.set_vexpand(True)

        ## Frontend tab ##
        frontend_tab = Gtk.Label(label="Frontend")

        m64plib_frame = Gtk.Frame(label="mupen64plus library")
        language_frame = Gtk.Frame(label="Language")
        HotkeyFrame = Gtk.Frame(label="Hotkey")
        FrontendMiscellaneousFrame = Gtk.Frame(label="Miscellaneous")

        frontend_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        m64p_paths_grid = Gtk.Grid()
        language_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        HotkeyBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        FrontendMiscellaneousBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        m64p_lib_entry = self.insert_entry('M64pLib', 'Frontend', 'frontend', "Mupen64plus library .so, .dll or .dylib", "Mupen64plus library .so, .dll or .dylib")
        m64p_lib_button = Gtk.Button.new_with_label("Open")
        m64p_lib_button.connect("clicked", self.on_search_path, m64p_lib_entry, "library")

        m64p_plugins_entry = self.insert_entry('PluginsDir', 'Frontend', 'frontend', "Choose a dir where library and plugins are found", "Choose a dir where library and plugins are found")
        m64p_plugins_button = Gtk.Button.new_with_label("Open")
        m64p_plugins_button.connect("clicked", self.on_search_path_dir, m64p_plugins_entry)

        config_dir_entry = self.insert_entry('ConfigDir', 'Frontend', 'frontend', "Choose a dir where .cfg will be stored", "Choose a dir where .cfg will be stored")
        config_dir_button = Gtk.Button.new_with_label("Open")
        config_dir_button.connect("clicked", self.on_search_path_dir, config_dir_entry)

        data_dir_entry = self.insert_entry('DataDir', 'Frontend', 'frontend', "Choose a dir where INIs will be stored", "Choose a dir where INIs will be stored")
        data_dir_button = Gtk.Button.new_with_label("Open")
        data_dir_button.connect("clicked", self.on_search_path_dir, data_dir_entry)

        library_warning = Gtk.Label(label="NOTE: Any change in these paths to be effective will need restart")

        m64p_paths_grid.attach(m64p_lib_entry, 0, 0, 1, 1)
        m64p_paths_grid.attach(m64p_lib_button, 1, 0, 1, 1)
        m64p_paths_grid.attach(m64p_plugins_entry, 0, 1, 1, 1)
        m64p_paths_grid.attach(m64p_plugins_button, 1, 1, 1, 1)
        m64p_paths_grid.attach(config_dir_entry, 0, 2, 1, 1)
        m64p_paths_grid.attach(config_dir_button, 1, 2, 1, 1)
        m64p_paths_grid.attach(data_dir_entry, 0, 3, 1, 1)
        m64p_paths_grid.attach(data_dir_button, 1, 3, 1, 1)
        m64p_paths_grid.attach(library_warning, 0, 4, 1, 1)

        m64plib_frame.set_child(m64p_paths_grid)
        self.set_margin(m64plib_frame, 5,5,5,5)

        language_combo_choices = ["English"]

        language_combo = Gtk.ComboBoxText()
        for key,lang in enumerate(language_combo_choices):
            language_combo.append(str(key),lang)

        if self.parent.frontend_conf.get("Frontend", "Language") != None:
            language_combo.set_active_id(str(self.parent.frontend_conf.get("Frontend", "Language")))

        language_combo.connect('changed', self.on_combobox_changed, 'Language')

        language_box.append(language_combo)
        language_frame.set_child(language_box)
        self.set_margin(language_frame, 5,5,5,5)

        #FrontendMiscellaneousBox.add()
        #FrontendMiscellaneousFrame.add(FrontendMiscellaneousBox)

        frontend_box.append(m64plib_frame)
        frontend_box.append(language_frame)
        #frontend_box.pack_start(HotkeyFrame, False, False, 0)
        #frontend_box.pack_start(FrontendMiscellaneousFrame, False, False, 0)

        config_notebook.append_page(frontend_box, frontend_tab)


        ## Emulation tab ##
        emulation_tab = Gtk.Label(label="Emulation")

        cpu_core_frame = Gtk.Frame(label="CPU Core")
        compatibility_frame = Gtk.Frame(label="Compatibility")
        emu_miscellaneous_frame = Gtk.Frame(label="Miscellaneous")

        emulation_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        cpu_core_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        compatibility_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        emu_miscellaneous_grid = Gtk.Grid()

        cpu_core_combo = Gtk.ComboBoxText()
        # Use Pure Interpreter if 0, Cached Interpreter if 1, or Dynamic Recompiler if 2 or more
        cpu_core_combo.append('0',"Pure Interpreter")
        cpu_core_combo.append('1',"Interpreter")
        cpu_core_combo.append('2',"Dynamic Recompiler")
        if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
            if self.parent.m64p_wrapper.ConfigGetParameter('R4300Emulator') != None:
                cpu_core_combo.set_active_id(str(self.parent.m64p_wrapper.ConfigGetParameter('R4300Emulator')))
                cpu_core_combo.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp('R4300Emulator'))
        else:
            cpu_core_combo.set_sensitive(False)
        cpu_core_combo.connect('changed', self.on_combobox_changed, 'R4300Emulator')

        cpu_core_box.append(cpu_core_combo)
        cpu_core_frame.set_child(cpu_core_box)
        self.set_margin(cpu_core_frame, 5,5,5,5)

        no_comp_jump_chkbox = self.insert_checkbox('NoCompiledJump', "Core", "m64p", "Disable compiled jump", None)
        no_expansionpak_chkbox = self.insert_checkbox('DisableExtraMem', "Core", "m64p", "Disable memory expansion (8 MB)", None)

        compatibility_box.append(no_comp_jump_chkbox)
        compatibility_box.append(no_expansionpak_chkbox)
        compatibility_frame.set_child(compatibility_box)
        self.set_margin(compatibility_frame, 5,5,5,5)

        auto_saveslot_chkbox = self.insert_checkbox('AutoStateSlotIncrement', "Core", "m64p", "Auto increment save slot", None)
        random_interrupt_chkbox = self.insert_checkbox('RandomizeInterrupt', "Core", "m64p", "Randomize PI/SI Interrupt Timing", None)
        osd_chkbox = self.insert_checkbox('OnScreenDisplay', "Core", "m64p", "Enable On Screen Display (OSD)", None)

        sidma_spin = self.insert_spinbutton("SiDmaDuration", "Core", "m64p", -1, 5) #TODO: Check if exists a maximum value here
        sidma_label = Gtk.Label(label="Duration of SI DMA (-1: use per game settings)")
        if self.parent.lock == True or self.parent.m64p_wrapper.compatible == False:
            sidma_label.set_sensitive(False)

        countxop_spin = self.insert_spinbutton("CountPerOp", "Core", "m64p", 0, 5) #TODO: Check if exists a maximum value here
        countxop_label = Gtk.Label(label="Force n° of cycles per emulated instruction (if > 0)")
        if self.parent.lock == True or self.parent.m64p_wrapper.compatible == False:
            countxop_label.set_sensitive(False)

        emu_miscellaneous_grid.attach(auto_saveslot_chkbox, 0, 0, 2, 1)
        emu_miscellaneous_grid.attach(random_interrupt_chkbox, 0, 1, 2, 1)
        emu_miscellaneous_grid.attach(sidma_spin, 0, 2, 1, 1)
        emu_miscellaneous_grid.attach(sidma_label, 1, 2, 1, 1)
        emu_miscellaneous_grid.attach(osd_chkbox, 0, 3, 2, 1)
        emu_miscellaneous_grid.attach(countxop_spin, 0, 4, 1, 1)
        emu_miscellaneous_grid.attach(countxop_label, 1, 4, 1, 1)
        emu_miscellaneous_frame.set_child(emu_miscellaneous_grid)
        self.set_margin(emu_miscellaneous_frame, 5,5,5,5)

        emulation_box.append(cpu_core_frame)
        emulation_box.append(compatibility_frame)
        emulation_box.append(emu_miscellaneous_frame)

        config_notebook.append_page(emulation_box, emulation_tab)

        ## Video-General tab ##
        video_tab = Gtk.Label(label="Video")

        video_general_frame = Gtk.Frame(label="General")
        rotate_frame = Gtk.Frame(label="Rotate Screen")
        webcam_frame = Gtk.Frame(label="Webcam")

        video_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        video_general_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        video_width_height_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
            self.parent.m64p_wrapper.ConfigOpenSection('Video-General')
        fullscreen_chkbox = self.insert_checkbox('Fullscreen', 'Video-General', 'm64p', "Always start in fullscreen mode", None)
        vsync_chkbox = self.insert_checkbox('VerticalSync', 'Video-General', 'm64p', "Enable VerticalSync", None)
        vidext_chkbox = self.insert_checkbox('VidExt', 'Frontend', 'frontend', "Enable Vidext", "This option will allow to play the game inside frontend's window")

        widthxheight_label = Gtk.Label(label="Screen width x height: ")
        if self.parent.lock == True or self.parent.m64p_wrapper.compatible == False:
            widthxheight_label.set_sensitive(False)
        width_spin = self.insert_spinbutton("ScreenWidth", "Video-General", "m64p", 1, 4096) #TODO: Check if exists a maximum value here
        height_spin = self.insert_spinbutton("ScreenHeight", "Video-General", "m64p", 1, 4096) #TODO: Check if exists a maximum value here

        video_width_height_box.append(widthxheight_label)
        video_width_height_box.append(width_spin)
        video_width_height_box.append(height_spin)

        video_general_box.append(fullscreen_chkbox)
        video_general_box.append(vsync_chkbox)
        video_general_box.append(vidext_chkbox)
        video_general_box.append(video_width_height_box)

        video_general_frame.set_child(video_general_box)
        self.set_margin(video_general_frame, 5,5,5,5)

        rotate_combo = Gtk.ComboBoxText()
        rotate_combo.append('0',"Normal (0°)")
        rotate_combo.append('1',"(90°)")
        rotate_combo.append('2',"Flipped (180°)")
        rotate_combo.append('3',"(270°)")
        if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
            try:
                rotate_combo.set_active_id(str(self.parent.m64p_wrapper.ConfigGetParameter('Rotate')))
            except KeyError:
                rotate_combo.set_sensitive(False)

        else:
            rotate_combo.set_sensitive(False)

        rotate_combo.connect('changed', self.on_combobox_changed, 'Rotate')
        rotate_frame.set_child(rotate_combo)
        self.set_margin(rotate_frame, 5,5,5,5)

        webcam_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL) #TODO: Change with Gtk.Grid()

        if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
            self.parent.m64p_wrapper.ConfigOpenSection('Core')
        webcam1_entry = self.insert_entry('GbCameraVideoCaptureBackend1', 'Core', 'm64p', "Gameboy Camera Video Capture backend", None)
        #webcam1_button = Gtk.Button.new_with_label("Open")
        #webcam_button.connect("clicked", self.on_search_path_lib, webcam1_entry)

        webcam_box.append(webcam1_entry)
        webcam_frame.set_child(webcam_box)
        self.set_margin(webcam_frame, 5,5,5,5)

        video_box.append(video_general_frame)
        video_box.append(rotate_frame)
        video_box.append(webcam_frame)

        config_notebook.append_page(video_box, video_tab)

        ## Plugins ##
        plugins_tab = Gtk.Label(label="Plugins")

        gfx_frame = Gtk.Frame(label="Graphics Plugin")
        audio_frame = Gtk.Frame(label="Audio Plugin")
        input_frame = Gtk.Frame(label="Input Plugin")
        rsp_frame = Gtk.Frame(label="RSP Plugin")

        plugins_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        gfx_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        audio_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        rsp_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
            self.parent.m64p_wrapper.ConfigOpenSection('Core')

        gfx_combo = Gtk.ComboBoxText()
        gfx_combo.set_hexpand(True)
        gfx_combo.append("dummy", "No video")
        for key,val in self.parent.m64p_wrapper.gfx_plugins.items():
            gfx_combo.append(key, val)

        if self.parent.frontend_conf.get("Frontend", "GfxPlugin") != None:
            gfx_combo.set_active_id(self.parent.frontend_conf.get("Frontend", "GfxPlugin"))

        gfx_combo.connect('changed', self.on_combobox_changed, 'GfxPlugin')

        self.gfx_configure_button = Gtk.Button(label="Configure")
        self.gfx_configure_button.connect("clicked", self.on_configure_button, self.parent, 'gfx')
        if self.parent.lock == True or self.parent.m64p_wrapper.compatible == False:
            gfx_combo.set_sensitive(False)
            self.gfx_configure_button.set_sensitive(False)

        gfx_box.append(gfx_combo)
        gfx_box.append(self.gfx_configure_button)
        gfx_frame.set_child(gfx_box)
        self.set_margin(gfx_frame, 5,5,5,5)

        audio_combo = Gtk.ComboBoxText()
        audio_combo.set_hexpand(True)
        audio_combo.append("dummy", "No audio")
        for key,val in self.parent.m64p_wrapper.audio_plugins.items():
             audio_combo.append(key, val)

        if self.parent.frontend_conf.get("Frontend", "AudioPlugin") != None:
            audio_combo.set_active_id(self.parent.frontend_conf.get("Frontend", "AudioPlugin"))

        audio_combo.connect('changed', self.on_combobox_changed, 'AudioPlugin')
        self.audio_configure_button = Gtk.Button(label="Configure")
        self.audio_configure_button.connect("clicked", self.on_configure_button, self.parent, 'audio')
        if self.parent.lock == True or self.parent.m64p_wrapper.compatible == False:
            audio_combo.set_sensitive(False)
            self.audio_configure_button.set_sensitive(False)

        audio_box.append(audio_combo)
        audio_box.append(self.audio_configure_button)
        audio_frame.set_child(audio_box)
        self.set_margin(audio_frame, 5,5,5,5)

        input_combo = Gtk.ComboBoxText()
        input_combo.set_hexpand(True)
        input_combo.append("dummy", "No input")
        for key,val in self.parent.m64p_wrapper.input_plugins.items():
             input_combo.append(key, val)

        if self.parent.frontend_conf.get("Frontend", "InputPlugin") != None:
            input_combo.set_active_id(self.parent.frontend_conf.get("Frontend", "InputPlugin"))

        input_combo.connect('changed', self.on_combobox_changed, 'InputPlugin')
        self.input_configure_button = Gtk.Button(label="Configure")
        self.input_configure_button.connect("clicked", self.on_configure_button, self.parent, 'input')
        if self.parent.frontend_conf.get("Frontend", "InputPlugin") == "mupen64plus-input-raphnetraw": #TODO: Is still necessary?
            self.input_configure_button.set_sensitive(False)
        if self.parent.lock == True or self.parent.m64p_wrapper.compatible == False:
            input_combo.set_sensitive(False)
            self.input_configure_button.set_sensitive(False)

        input_box.append(input_combo)
        input_box.append(self.input_configure_button)
        input_frame.set_child(input_box)
        self.set_margin(input_frame, 5,5,5,5)

        rsp_combo = Gtk.ComboBoxText()
        rsp_combo.set_hexpand(True)
        rsp_combo.append("dummy", "No RSP")
        for key,val in self.parent.m64p_wrapper.rsp_plugins.items():
             rsp_combo.append(key, val)

        if self.parent.frontend_conf.get("Frontend", "RSPPlugin") != None:
            rsp_combo.set_active_id(self.parent.frontend_conf.get("Frontend", "RSPPlugin"))

        rsp_combo.connect('changed', self.on_combobox_changed, 'RSPPlugin')
        self.rsp_configure_button = Gtk.Button(label="Configure")
        self.rsp_configure_button.connect("clicked", self.on_configure_button, self.parent, 'rsp')
        if self.parent.lock == True or self.parent.m64p_wrapper.compatible == False:
            rsp_combo.set_sensitive(False)
            self.rsp_configure_button.set_sensitive(False)

        rsp_box.append(rsp_combo)
        rsp_box.append(self.rsp_configure_button)
        rsp_frame.set_child(rsp_box)
        self.set_margin(rsp_frame, 5,5,5,5)

        plugins_box.append(gfx_frame)
        plugins_box.append(audio_frame)
        plugins_box.append(input_frame)
        plugins_box.append(rsp_frame)

        config_notebook.append_page(plugins_box, plugins_tab)

        ## Paths ##
        if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
            self.parent.m64p_wrapper.ConfigOpenSection('Core')
        paths_tab = Gtk.Label(label="Paths")

        paths_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        m64p_paths_grid2 = Gtk.Grid()
        gamedir_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        gamedir1_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        gamedir2_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        gamedir3_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        pif_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        pif_ntsc_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        pif_pal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        m64p_frame = Gtk.Frame(label="mupen64plus directories")
        gamedir_frame = Gtk.Frame(label="game image directories")
        pif_frame = Gtk.Frame(label="PIF ROM path")

        sram_dir_entry = self.insert_entry('SaveSRAMPath', 'Core', 'm64p', "Choose a dir where SRAM/EEPROM/FlashRAM saves will be stored", None)
        sram_dir_button = Gtk.Button.new_with_label("Open")
        sram_dir_button.connect("clicked", self.on_search_path_dir, sram_dir_entry)
        if self.parent.lock == True or self.parent.m64p_wrapper.compatible == False:
            sram_dir_button.set_sensitive(False)

        shared_dir_entry = self.insert_entry('SharedDataPath', 'Core', 'm64p', "Choose a dir where shared data will be stored", None)
        shared_data_dir_button = Gtk.Button.new_with_label("Open")
        shared_data_dir_button.connect("clicked", self.on_search_path_dir, shared_dir_entry)
        if self.parent.lock == True or self.parent.m64p_wrapper.compatible == False:
            shared_data_dir_button.set_sensitive(False)

        save_dir_entry = self.insert_entry('SaveStatePath', 'Core', 'm64p', "Choose a dir where save states will be stored", None)
        save_dir_button = Gtk.Button.new_with_label("Open")
        save_dir_button.connect("clicked", self.on_search_path_dir, save_dir_entry)
        if self.parent.lock == True or self.parent.m64p_wrapper.compatible == False:
            save_dir_button.set_sensitive(False)

        screenshot_entry = self.insert_entry('ScreenshotPath', 'Core', 'm64p', "Choose a dir where screenshots will be stored", None)
        screenshot_button = Gtk.Button.new_with_label("Open")
        screenshot_button.connect("clicked", self.on_search_path_dir, screenshot_entry)
        if self.parent.lock == True or self.parent.m64p_wrapper.compatible == False:
            screenshot_button.set_sensitive(False)

        # Path to directory where SRAM/EEPROM data (in-game saves) are stored. If this is blank, the default value of
        # Path to a directory to search when looking for shared data files

        # child, left, top, width, height)
        m64p_paths_grid2.attach(sram_dir_entry, 0, 1, 1, 1)
        m64p_paths_grid2.attach(sram_dir_button, 1, 1, 1, 1)
        m64p_paths_grid2.attach(shared_dir_entry, 0, 2, 1, 1)
        m64p_paths_grid2.attach(shared_data_dir_button, 1, 2, 1, 1)
        m64p_paths_grid2.attach(save_dir_entry, 0, 3, 1, 1)
        m64p_paths_grid2.attach(save_dir_button, 1, 3, 1, 1)
        m64p_paths_grid2.attach(screenshot_entry, 0, 4, 1, 1)
        m64p_paths_grid2.attach(screenshot_button, 1, 4, 1, 1)

        m64p_frame.set_child(m64p_paths_grid2)
        self.set_margin(m64p_frame, 5,5,5,5)

        # TODO: Replace with ListStore or CellRenderer? to allow multi directories
        #self.parent.frontend_conf.open_section("GameDirs")
        gamedir_entry = self.insert_entry('path1', 'GameDirs', 'frontend', "Choose the dir where game images are found", None)
        gamedir_entry.set_hexpand(True)
        gamedir_button = Gtk.Button.new_with_label("Open")
        gamedir_button.connect("clicked", self.on_search_path_dir, gamedir_entry)

        gamedir2_entry = self.insert_entry('path2', 'GameDirs', 'frontend', "Choose the dir where game images are found", None)
        gamedir2_entry.set_hexpand(True)
        gamedir2_button = Gtk.Button.new_with_label("Open")
        gamedir2_button.connect("clicked", self.on_search_path_dir, gamedir2_entry)

        gamedir3_entry = self.insert_entry('path3', 'GameDirs', 'frontend', "Choose the dir where game images are found", None)
        gamedir3_entry.set_hexpand(True)
        gamedir3_button = Gtk.Button.new_with_label("Open")
        gamedir3_button.connect("clicked", self.on_search_path_dir, gamedir3_entry)

        gamedir1_box.append(gamedir_entry)
        gamedir1_box.append(gamedir_button)
        gamedir2_box.append(gamedir2_entry)
        gamedir2_box.append(gamedir2_button)
        gamedir3_box.append(gamedir3_entry)
        gamedir3_box.append(gamedir3_button)
        gamedir_box.append(gamedir1_box)
        gamedir_box.append(gamedir2_box)
        gamedir_box.append(gamedir3_box)

        recursive_chkbox = self.insert_checkbox('Recursive', 'Frontend', 'frontend', "Recursive mode", "The frontend will scan for games even in subdirectories")
        gamedir_box.append(recursive_chkbox)

        gamedir_frame.set_child(gamedir_box)
        self.set_margin(gamedir_frame, 5,5,5,5)

        pif_chkbox = self.insert_checkbox('PifLoad', 'Frontend', 'frontend', "Enable PIFROM loading", "This option will allow to load the PIFROM at start of emulation")

        pif_ntsc_path_entry = self.insert_entry('PifNtscPath', 'Frontend', 'frontend', "Indicate the location of the NTSC N64 PIF ROM", "Indicate the location of the NTSC N64 PIF ROM")
        pif_ntsc_path_entry.set_hexpand(True)
        pif_ntsc_path_button = Gtk.Button.new_with_label("Open")
        pif_ntsc_path_button.connect("clicked", self.on_search_path, pif_ntsc_path_entry, "pif")

        pif_ntsc_box.append(pif_ntsc_path_entry)
        pif_ntsc_box.append(pif_ntsc_path_button)

        pif_pal_path_entry = self.insert_entry('PifPalPath', 'Frontend', 'frontend', "Indicate the location of the PAL N64 PIF ROM", "Indicate the location of the PAL N64 PIF ROM")
        pif_pal_path_entry.set_hexpand(True)
        pif_pal_path_button = Gtk.Button.new_with_label("Open")
        pif_pal_path_button.connect("clicked", self.on_search_path, pif_pal_path_entry, "pif")

        pif_pal_box.append(pif_pal_path_entry)
        pif_pal_box.append(pif_pal_path_button)

        pif_box.append(pif_chkbox)
        pif_box.append(pif_ntsc_box)
        pif_box.append(pif_pal_box)

        pif_frame.set_child(pif_box)
        self.set_margin(pif_frame, 5,5,5,5)

        paths_box.append(m64p_frame)
        paths_box.append(gamedir_frame)
        paths_box.append(pif_frame)

        config_notebook.append_page(paths_box, paths_tab)

        #Hotkey Tab

        # NOTE: get_content_area() is needed because a Gtk.Box already exists as the child container of the Gtk.Dialog
        self.config_box = self.window.get_content_area()
        self.config_box.append(config_notebook)

    def on_combobox_changed(self, widget, param):
        self.is_changed = True
        self.apply_button.set_sensitive(True)
        widget_id = widget.get_active_id()
        active_plugin = os.path.splitext(widget_id)[0]
        if param == 'R4300Emulator':
            self.parent.m64p_wrapper.ConfigOpenSection('Core')
            self.parent.m64p_wrapper.ConfigSetParameter('R4300Emulator', int(widget_id))
        elif param == 'Language':
            self.parent.frontend_conf.set("Frontend", "Language", str(widget_id))
        elif param == 'GfxPlugin':
            self.parent.frontend_conf.set("Frontend", "GfxPlugin", widget_id)
            #self.parent.m64p_wrapper.gfx_filename = widget_id
            #for item in self.parent.m64p_wrapper.gfx_plugins.items():
            #if widget_id in self.parent.m64p_wrapper.gfx_plugins:
            self.parent.m64p_wrapper.gfx_filename = widget_id
            # if active_plugin in ['mupen64plus-video-GLideN64', 'mupen64plus-video-angrylion-plus', 'mupen64plus-video-glide64mk2', 'mupen64plus-video-rice', 'mupen64plus-video-z64']:
            if active_plugin == 'mupen64plus-video-GLideN64':
                self.gfx_configure_button.set_sensitive(True)
            elif active_plugin == 'mupen64plus-video-angrylion-plus':
                self.gfx_configure_button.set_sensitive(True)
            elif active_plugin == 'mupen64plus-video-glide64mk2':
                self.gfx_configure_button.set_sensitive(True)
            elif active_plugin == 'mupen64plus-video-rice':
                self.gfx_configure_button.set_sensitive(True)
            elif active_plugin == 'mupen64plus-video-z64':
                self.gfx_configure_button.set_sensitive(True)
            else:
                self.gfx_configure_button.set_sensitive(False)
            # else:
            #     self.parent.m64p_wrapper.gfx_filename = "dummy"
            #     self.gfx_configure_button.set_sensitive(False)

        elif param == 'AudioPlugin':
            self.parent.frontend_conf.set("Frontend", "AudioPlugin", widget_id)
            self.parent.m64p_wrapper.audio_filename = widget_id
            if active_plugin == 'mupen64plus-audio-sdl':
                self.audio_configure_button.set_sensitive(True)
            else:
                self.audio_configure_button.set_sensitive(False)
        elif param == 'InputPlugin':
            self.parent.frontend_conf.set("Frontend", "InputPlugin", widget_id)
            self.parent.m64p_wrapper.input_filename = widget_id
            if active_plugin == 'mupen64plus-input-sdl':
                self.input_configure_button.set_sensitive(True)
            elif active_plugin == 'mupen64plus-input-raphnetraw':
                self.input_configure_button.set_sensitive(False)
            else:
                self.input_configure_button.set_sensitive(False)
        elif param == 'RSPPlugin':
            self.parent.frontend_conf.set("Frontend", "RSPPlugin", widget_id)
            self.parent.m64p_wrapper.rsp_filename = widget_id
            if active_plugin == 'mupen64plus-rsp-hle':
                self.rsp_configure_button.set_sensitive(True)
            elif active_plugin == 'mupen64plus-rsp-cxd4':
                self.rsp_configure_button.set_sensitive(True)
            elif active_plugin == 'mupen64plus-rsp-z64':
                self.rsp_configure_button.set_sensitive(True)
            else:
                self.rsp_configure_button.set_sensitive(False)
        elif param == 'Rotate':
            self.parent.m64p_wrapper.ConfigOpenSection('Video-General')
            self.parent.m64p_wrapper.ConfigSetParameter('Rotate', int(widget_id))
        else:
            log.warning(f"Config: Unknown parameter '{param}'")

    def on_checkbox_toggled(self, widget, section, param):
        self.is_changed = True
        self.apply_button.set_sensitive(True)
        if section == "Frontend" or section == "GameDirs":
            #self.parent.frontend_conf.open_section(section)
            if widget.get_active() == True:
                self.parent.frontend_conf.set(section, param, "True")
            elif widget.get_active() == False:
                self.parent.frontend_conf.set(section, param, "False")
            else:
                log.error("Config: Unexpected error")
        else:
            self.parent.m64p_wrapper.ConfigOpenSection(section)
            if widget.get_active() == True:
                self.parent.m64p_wrapper.ConfigSetParameter(param, True)
            elif widget.get_active() == False:
                self.parent.m64p_wrapper.ConfigSetParameter(param, False)
            else:
                log.error("Config: Unexpected error")

    def on_spinbutton_changed(self, widget, section, param):
        self.is_changed = True
        self.apply_button.set_sensitive(True)
        if section != None:
            self.parent.m64p_wrapper.ConfigOpenSection(section)
            self.parent.m64p_wrapper.ConfigSetParameter(param, widget.get_value_as_int())

    def on_search_path(self, widget, entry, file):
        dialog = w_dialog.FileChooserDialog(self.window, file)
        path = dialog.path
        if path != None:
            self.is_changed = True
            self.apply_button.set_sensitive(True)
            entry.set_text(path)

    def on_search_path_dir(self, widget, entry):
        dialog = w_dialog.FileChooserDialog(self.window, "directory")
        dir_path = dialog.path
        if dir_path != None:
            self.is_changed = True
            self.apply_button.set_sensitive(True)
            entry.set_text(dir_path)

    def on_configure_button(self, widget, parent, plugin):
        w_plugin.PluginDialog(parent, None, plugin)

    def on_entry_changed(self, widget, section, param):
        self.is_changed = True
        self.apply_button.set_sensitive(True)
        value = widget.get_text()
        if section == "Frontend" or section == "GameDirs":
            self.parent.frontend_conf.set(section, param, value)
        else:
            self.parent.m64p_wrapper.ConfigOpenSection(section)
            self.parent.m64p_wrapper.ConfigSetParameter(param, value)
        log.debug(f"{section}, {param}, {value}")

    def revert(self):
        self.is_changed = False
        self.apply_button.set_sensitive(False)
        #self.parent.frontend_conf.open_section("Frontend")
        self.parent.frontend_conf.set("Frontend", 'M64pLib', self.former_values['library'])
        self.parent.frontend_conf.set("Frontend", 'PluginsDir', self.former_values['plugins_dir'])
        self.parent.frontend_conf.set("Frontend", 'ConfigDir', self.former_values['config_dir'])
        self.parent.frontend_conf.set("Frontend", 'DataDir', self.former_values['data_dir'])
        self.parent.frontend_conf.set("Frontend", 'GfxPlugin', self.former_values['gfx_plugin'])
        self.parent.frontend_conf.set("Frontend", 'AudioPlugin', self.former_values['audio_plugin'])
        self.parent.frontend_conf.set("Frontend", 'InputPlugin', self.former_values['input_plugin'])
        self.parent.frontend_conf.set("Frontend", 'RSPPlugin', self.former_values['rsp_plugin'])
        self.parent.frontend_conf.set("Frontend", 'Vidext', self.former_values['vidext'])
        self.parent.frontend_conf.set("Frontend", 'PifNtscPath', self.former_values['pifntsc'])
        self.parent.frontend_conf.set("Frontend", 'PifPalPath', self.former_values['pifpal'])
        #self.parent.frontend_conf.open_section("GameDirs")
        self.parent.frontend_conf.set("GameDirs", 'path1', self.former_values['path1'])
        self.parent.frontend_conf.set("GameDirs", 'path2', self.former_values['path2'])
        self.parent.frontend_conf.set("GameDirs", 'path3', self.former_values['path3'])

    def former_update(self):
        self.is_changed = False
        self.former_values['library'] = self.parent.frontend_conf.get("Frontend", 'M64pLib')
        self.former_values['plugins_dir'] = self.parent.frontend_conf.get("Frontend", 'PluginsDir')
        self.former_values['config_dir'] = self.parent.frontend_conf.get("Frontend", 'ConfigDir')
        self.former_values['data_dir'] = self.parent.frontend_conf.get("Frontend", 'DataDir')
        self.former_values['gfx_plugin'] = self.parent.frontend_conf.get("Frontend", 'GfxPlugin')
        self.former_values['audio_plugin'] = self.parent.frontend_conf.get("Frontend", 'AudioPlugin')
        self.former_values['input_plugin'] = self.parent.frontend_conf.get("Frontend", 'InputPlugin')
        self.former_values['rsp_plugin'] = self.parent.frontend_conf.get("Frontend", 'RSPPlugin')
        self.former_values['vidext'] = self.parent.frontend_conf.get("Frontend", 'Vidext')
        try:
            self.former_values['pifntsc'] = self.parent.frontend_conf.get("Frontend", 'PifNtscPath')
        except:
            self.former_values['pifntsc'] = ''
        try:
            self.former_values['pifpal'] = self.parent.frontend_conf.get("Frontend", 'PifPalPath')
        except:
            self.former_values['pifpal'] = ''
        self.former_values['path1'] = self.parent.frontend_conf.get("GameDirs", 'path1')
        self.former_values['path2'] = self.parent.frontend_conf.get("GameDirs", 'path2')
        self.former_values['path3'] = self.parent.frontend_conf.get("GameDirs", 'path3')

    def insert_entry(self, param, section, config, placeholder, help=None):
        try:
            entry = Gtk.Entry()
            entry.set_placeholder_text(placeholder)
            entry.set_hexpand(True)
            entry.connect("changed", self.on_entry_changed, section, param)

            if config == "frontend":
                entry.set_tooltip_text(help)
                if self.parent.frontend_conf.get(section, param) != None:
                    entry.set_text(self.parent.frontend_conf.get(section, param))

            elif config == "m64p":
                if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
                    entry.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp(param))
                    if self.parent.m64p_wrapper.ConfigGetParameter(param) != None:
                        entry.set_text(self.parent.m64p_wrapper.ConfigGetParameter(param))
                else:
                    entry.set_sensitive(False)

        except KeyError:
            if config == "frontend":
                log.warning(f'{param} parameter NOT found, creating it...')
                self.parent.frontend_conf.set(section, param, '')
            else:
                entry.set_sensitive(False)
                log.warning(f'{param} parameter NOT found, thus disabling the entry.')

        return entry

    def insert_checkbox(self, param, section, config, label, help=None):
        checkbox = Gtk.CheckButton.new_with_label(label)
        checkbox.connect("toggled", self.on_checkbox_toggled, section, param)
        try:
            if config == "frontend":
                checkbox.set_tooltip_text(help)
                if self.parent.frontend_conf.get(section, param) == "True":
                    checkbox.set_active(True)
            elif config == "m64p":
                checkbox.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp(param))
                if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
                    if self.parent.m64p_wrapper.ConfigGetParameter(param) == True:
                        checkbox.set_active(True)
                else:
                    checkbox.set_sensitive(False)
        except KeyError:
            if config == "frontend":
                log.warning(f'{param} parameter NOT found, creating it and setting new default value: False.')
                self.parent.frontend_conf.set(section, param, 'False')
            else:
                log.warning(f'{param} parameter NOT found, thus disabling the checkpoint.')
            checkbox.set_sensitive(False)

        return checkbox

    def insert_spinbutton(self, param, section, config, minimum, maximum, help=None):
        adj_value = 0
        adj_step = 1.0
        spin_climb = 1.0

        adjustment = Gtk.Adjustment(value=adj_value, lower=minimum, upper=maximum, step_increment=adj_step)
        spin = Gtk.SpinButton.new(adjustment, spin_climb, 0)
        spin.set_snap_to_ticks(True)
        spin.connect("value-changed", self.on_spinbutton_changed, section, param)
        try:
            if config == "frontend":
                spin.set_tooltip_text(help)
                spin.set_value(self.parent.frontend_conf.get(section, param))
            elif config == "m64p":
                if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:
                    spin.set_tooltip_text(self.parent.m64p_wrapper.ConfigGetParameterHelp(param))
                    spin.set_value(self.parent.m64p_wrapper.ConfigGetParameter(param))
                else:
                    spin.set_sensitive(False)

        except KeyError:
            log.warning(f'{param} parameter NOT found, thus disabling the spin button.')
            spin.set_sensitive(False)

        return spin
        
