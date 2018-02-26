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

class ConfigDialog(Gtk.Dialog):
    def __init__(self, parent):
        self.parent_widget = parent
        self.former_values = {}
        self.former_update()
        self.is_changed = False

        if g.lock == False and g.m64p_wrapper.compatible == True:
            g.m64p_wrapper.plugins_shutdown()
            g.m64p_wrapper.ConfigOpenSection('Core')

        self.config_window = Gtk.Dialog()
        self.config_window.set_properties(self, title="Configure")
        self.config_window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.config_window.set_default_size(480, 550)
        self.config_window.set_transient_for(parent)

        self.apply_button = self.config_window.add_button("Apply",Gtk.ResponseType.APPLY)
        self.apply_button.set_sensitive(False)
        self.config_window.add_button("Cancel",Gtk.ResponseType.CANCEL)
        self.config_window.add_button("OK",Gtk.ResponseType.OK)

        self.config_tabs()

    def config_tabs(self):
        config_notebook = Gtk.Notebook()
        config_notebook.set_vexpand(True)

        ## Frontend tab ##
        g.frontend_conf.open_section("Frontend")
        frontend_tab = Gtk.Label(label="Frontend")

        m64plib_frame = Gtk.Frame(label="mupen64plus library", shadow_type=1)
        language_frame = Gtk.Frame(label="Language", shadow_type=1)
        HotkeyFrame = Gtk.Frame(label="Hotkey", shadow_type=1)
        FrontendMiscellaneousFrame = Gtk.Frame(label="Miscellaneous", shadow_type=1)

        frontend_box = Gtk.VBox()
        m64p_paths_grid = Gtk.Grid()
        language_box = Gtk.VBox()
        HotkeyBox = Gtk.VBox()
        FrontendMiscellaneousBox = Gtk.VBox()

        m64p_lib_entry = self.insert_entry('M64pLib', 'Frontend', 'frontend', "Mupen64plus library .so, .dll or .dylib", None)
        m64p_lib_button = Gtk.Button.new_with_label("Open")
        m64p_lib_button.connect("clicked", self.on_search_path_lib, m64p_lib_entry)

        m64p_plugins_entry = self.insert_entry('PluginsDir', 'Frontend', 'frontend', "Choose a dir where library and plugins are found", None)
        m64p_plugins_button = Gtk.Button.new_with_label("Open")
        m64p_plugins_button.connect("clicked", self.on_search_path_dir, m64p_plugins_entry)

        config_dir_entry = self.insert_entry('ConfigDir', 'Frontend', 'frontend', "Choose a dir where .cfg will be stored", None)
        config_dir_button = Gtk.Button.new_with_label("Open")
        config_dir_button.connect("clicked", self.on_search_path_dir, config_dir_entry)

        data_dir_entry = self.insert_entry('DataDir', 'Frontend', 'frontend', "Choose a dir where INIs will be stored", None)
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

        m64plib_frame.add(m64p_paths_grid)

        language_combo_choices = ["English"]

        language_combo = Gtk.ComboBoxText()
        for key,lang in enumerate(language_combo_choices):
            language_combo.append(str(key),lang)

        if g.frontend_conf.get('Language') != None:
            language_combo.set_active_id(str(g.frontend_conf.get('Language')))

        language_combo.connect('changed', self.on_combobox_changed, 'Language')

        language_box.add(language_combo)
        language_frame.add(language_box)

        #FrontendMiscellaneousBox.add()
        #FrontendMiscellaneousFrame.add(FrontendMiscellaneousBox)

        frontend_box.pack_start(m64plib_frame, False, False, 0)
        frontend_box.pack_start(language_frame, False, False, 0)
        #frontend_box.pack_start(HotkeyFrame, False, False, 0)
        #frontend_box.pack_start(FrontendMiscellaneousFrame, False, False, 0)

        config_notebook.append_page(frontend_box, frontend_tab)


        ## Emulation tab ##
        emulation_tab = Gtk.Label(label="Emulation")

        cpu_core_frame = Gtk.Frame(label="CPU Core",shadow_type=1)
        compatibility_frame = Gtk.Frame(label="Compatibility",shadow_type=1)
        emu_miscellaneous_frame = Gtk.Frame(label="Miscellaneous",shadow_type=1)

        emulation_box = Gtk.VBox()
        cpu_core_box = Gtk.VBox()
        compatibility_box = Gtk.VBox()
        emu_miscellaneous_grid = Gtk.Grid()

        cpu_core_combo = Gtk.ComboBoxText()
        # Use Pure Interpreter if 0, Cached Interpreter if 1, or Dynamic Recompiler if 2 or more
        cpu_core_combo.append('0',"Pure Interpreter")
        cpu_core_combo.append('1',"Interpreter")
        cpu_core_combo.append('2',"Dynamic Recompiler")
        if g.lock == False and g.m64p_wrapper.compatible == True:
            if g.m64p_wrapper.ConfigGetParameter('R4300Emulator') != None:
                cpu_core_combo.set_active_id(str(g.m64p_wrapper.ConfigGetParameter('R4300Emulator')))
        else:
            cpu_core_combo.set_sensitive(False)
        cpu_core_combo.connect('changed', self.on_combobox_changed, 'R4300Emulator')

        no_spec_recomp_chkbox = self.insert_checkbox('DisableSpecRecomp', "Core", "m64p", "Disable speculative precompilation in new dynarec", None)

        cpu_core_box.pack_start(cpu_core_combo, False, False, 0)
        cpu_core_box.pack_start(no_spec_recomp_chkbox, False, False, 0)
        cpu_core_frame.add(cpu_core_box)

        no_comp_jump_chkbox = self.insert_checkbox('NoCompiledJump', "Core", "m64p", "Disable compiled jump", None)
        no_expansionpak_chkbox = self.insert_checkbox('DisableExtraMem', "Core", "m64p", "Disable memory expansion (8 MB)", None)

        compatibility_box.pack_start(no_comp_jump_chkbox, False, False, 0)
        compatibility_box.pack_start(no_expansionpak_chkbox, False, False, 0)
        compatibility_frame.add(compatibility_box)

        auto_saveslot_chkbox = self.insert_checkbox('AutoStateSlotIncrement', "Core", "m64p", "Auto increment save slot", None)
        random_interrupt_chkbox = self.insert_checkbox('RandomizeInterrupt', "Core", "m64p", "Randomize PI/SI Interrupt Timing", None)
        osd_chkbox = self.insert_checkbox('OnScreenDisplay', "Core", "m64p", "Enable On Screen Display (OSD)", None)

        sidma_adjustment = Gtk.Adjustment(value=0, lower=-1, upper=5, step_increment=1.0) #TODO: Check if exists a maximum value here
        sidma_spin = Gtk.SpinButton.new(sidma_adjustment, 1.0, 0)
        if g.lock == False and g.m64p_wrapper.compatible == True:
            sidma_spin.set_value(g.m64p_wrapper.ConfigGetParameter('SiDmaDuration'))
        else:
            sidma_spin.set_sensitive(False)
        sidma_spin.connect("value-changed", self.on_spinbutton_changed, 'Core', 'SiDmaDuration')
        sidma_label = Gtk.Label(label="Duration of SI DMA (-1: use per game settings)")

        countxop_adjustment = Gtk.Adjustment(value=0, lower=0, upper=5, step_increment=1.0) #TODO: Check if exists a maximum value here
        countxop_spin = Gtk.SpinButton.new(countxop_adjustment, 1.0, 0)
        if g.lock == False and g.m64p_wrapper.compatible == True:
            countxop_spin.set_value(g.m64p_wrapper.ConfigGetParameter('CountPerOp'))
        else:
            countxop_spin.set_sensitive(False)
        countxop_spin.connect("value-changed", self.on_spinbutton_changed, 'Core', 'CountPerOp')
        countxop_label = Gtk.Label(label="Force n° of cycles per emulated instruction (if > 0)")

        emu_miscellaneous_grid.attach(auto_saveslot_chkbox, 0, 0, 2, 1)
        emu_miscellaneous_grid.attach(random_interrupt_chkbox, 0, 1, 2, 1)
        emu_miscellaneous_grid.attach(sidma_spin, 0, 2, 1, 1)
        emu_miscellaneous_grid.attach(sidma_label, 1, 2, 1, 1)
        emu_miscellaneous_grid.attach(osd_chkbox, 0, 3, 2, 1)
        emu_miscellaneous_grid.attach(countxop_spin, 0, 4, 1, 1)
        emu_miscellaneous_grid.attach(countxop_label, 1, 4, 1, 1)
        emu_miscellaneous_frame.add(emu_miscellaneous_grid)

        emulation_box.pack_start(cpu_core_frame, False, False, 0)
        emulation_box.pack_start(compatibility_frame, False, False, 0)
        emulation_box.pack_start(emu_miscellaneous_frame, False, False, 0)

        config_notebook.append_page(emulation_box, emulation_tab)

        ## Video-General tab ##
        video_tab = Gtk.Label(label="Video")

        video_general_frame = Gtk.Frame(label="General",shadow_type=1)
        rotate_frame = Gtk.Frame(label="Rotate Screen",shadow_type=1)
        resolution_frame = Gtk.Frame(label="Resolution",shadow_type=1)

        video_box = Gtk.VBox()
        video_general_box = Gtk.VBox()

        if g.lock == False and g.m64p_wrapper.compatible == True:
            g.m64p_wrapper.ConfigOpenSection('Video-General')
        fullscreen_chkbox = self.insert_checkbox('Fullscreen', 'Video-General', 'm64p', "Always start in fullscreen mode", None)
        vsync_chkbox = self.insert_checkbox('VerticalSync', 'Video-General', 'm64p', "Enable VerticalSync", None)

        video_general_box.pack_start(fullscreen_chkbox, False, False, 0)
        video_general_box.pack_start(vsync_chkbox, False, False, 0)

        video_general_frame.add(video_general_box)

        rotate_combo = Gtk.ComboBoxText()
        rotate_combo.append('0',"Normal (0°)")
        rotate_combo.append('1',"(90°)")
        rotate_combo.append('2',"Flipped (180°)")
        rotate_combo.append('3',"(270°)")
        if g.lock == False and g.m64p_wrapper.compatible == True:
            if g.m64p_wrapper.ConfigGetParameter('Rotate') != None:
                rotate_combo.set_active_id(str(g.m64p_wrapper.ConfigGetParameter('Rotate')))
        else:
            rotate_combo.set_sensitive(False)

        rotate_combo.connect('changed', self.on_combobox_changed, 'Rotate')
        rotate_frame.add(rotate_combo)

        video_box.pack_start(video_general_frame, False, False, 0)
        video_box.pack_start(rotate_frame, False, False, 0)
        #video_box.pack_start(resolution_frame, False, False, 0)

        config_notebook.append_page(video_box, video_tab)

        ## Plugins ##
        plugins_tab = Gtk.Label(label="Plugins")

        gfx_frame = Gtk.Frame(label="Graphics Plugin", shadow_type=1)
        audio_frame = Gtk.Frame(label="Audio Plugin", shadow_type=1)
        input_frame = Gtk.Frame(label="Input Plugin", shadow_type=1)
        rsp_frame = Gtk.Frame(label="RSP Plugin", shadow_type=1)

        plugins_box = Gtk.VBox()
        gfx_box = Gtk.HBox()
        audio_box = Gtk.HBox()
        input_box = Gtk.HBox()
        rsp_box = Gtk.HBox()

        if g.lock == False and g.m64p_wrapper.compatible == True:
            g.m64p_wrapper.ConfigOpenSection('Core')

        gfx_combo = Gtk.ComboBoxText()
        gfx_combo.append("dummy", "No video")
        for key,val in g.m64p_wrapper.gfx_plugins.items():
            gfx_combo.append(key, val)

        if g.frontend_conf.get('GfxPlugin') != None:
            gfx_combo.set_active_id(g.frontend_conf.get('GfxPlugin'))

        gfx_combo.connect('changed', self.on_combobox_changed, 'GfxPlugin')

        self.gfx_configure_button = Gtk.Button(label="Configure")
        self.gfx_configure_button.connect("clicked", self.on_configure_button, self.parent_widget, 'gfx')
        if g.lock == True and g.m64p_wrapper.compatible == False:
            gfx_combo.set_sensitive(False)
            self.gfx_configure_button.set_sensitive(False)

        gfx_box.pack_start(gfx_combo, True, True, 5)
        gfx_box.pack_start(self.gfx_configure_button, False, False, 0)
        gfx_frame.add(gfx_box)

        audio_combo = Gtk.ComboBoxText()
        audio_combo.append("dummy", "No audio")
        for key,val in g.m64p_wrapper.audio_plugins.items():
             audio_combo.append(key, val)

        if g.frontend_conf.get('AudioPlugin') != None:
            audio_combo.set_active_id(g.frontend_conf.get('AudioPlugin'))

        audio_combo.connect('changed', self.on_combobox_changed, 'AudioPlugin')
        self.audio_configure_button = Gtk.Button(label="Configure")
        self.audio_configure_button.connect("clicked", self.on_configure_button, self.parent_widget, 'audio')
        if g.lock == True and g.m64p_wrapper.compatible == False:
            audio_combo.set_sensitive(False)
            self.audio_configure_button.set_sensitive(False)

        audio_box.pack_start(audio_combo, True, True, 5)
        audio_box.pack_start(self.audio_configure_button, False, False, 0)
        audio_frame.add(audio_box)

        input_combo = Gtk.ComboBoxText()
        input_combo.append("dummy", "No input")
        for key,val in g.m64p_wrapper.input_plugins.items():
             input_combo.append(key, val)

        if g.frontend_conf.get('InputPlugin') != None:
            input_combo.set_active_id(g.frontend_conf.get('InputPlugin'))

        input_combo.connect('changed', self.on_combobox_changed, 'InputPlugin')
        self.input_configure_button = Gtk.Button(label="Configure")
        self.input_configure_button.connect("clicked", self.on_configure_button, self.parent_widget, 'input')
        if g.frontend_conf.get('InputPlugin') == "mupen64plus-input-raphnetraw.so": #TODO: Is still necessary?
            self.input_configure_button.set_sensitive(False)
        if g.lock == True and g.m64p_wrapper.compatible == False:
            input_combo.set_sensitive(False)
            self.input_configure_button.set_sensitive(False)

        input_box.pack_start(input_combo, True, True, 5)
        input_box.pack_start(self.input_configure_button, False, False, 0)
        input_frame.add(input_box)

        rsp_combo = Gtk.ComboBoxText()
        rsp_combo.append("dummy", "No RSP")
        for key,val in g.m64p_wrapper.rsp_plugins.items():
             rsp_combo.append(key, val)

        if g.frontend_conf.get('RSPPlugin') != None:
            rsp_combo.set_active_id(g.frontend_conf.get('RSPPlugin'))

        rsp_combo.connect('changed', self.on_combobox_changed, 'RSPPlugin')
        self.rsp_configure_button = Gtk.Button(label="Configure")
        self.rsp_configure_button.connect("clicked", self.on_configure_button, self.parent_widget, 'rsp')
        if g.lock == True and g.m64p_wrapper.compatible == False:
            rsp_combo.set_sensitive(False)
            self.rsp_configure_button.set_sensitive(False)

        rsp_box.pack_start(rsp_combo, True, True, 5)
        rsp_box.pack_start(self.rsp_configure_button, False, False, 0)
        rsp_frame.add(rsp_box)

        plugins_box.pack_start(gfx_frame, False, False, 0)
        plugins_box.pack_start(audio_frame, False, False, 0)
        plugins_box.pack_start(input_frame, False, False, 0)
        plugins_box.pack_start(rsp_frame, False, False, 0)

        config_notebook.append_page(plugins_box, plugins_tab)

        ## Paths ##
        if g.lock == False and g.m64p_wrapper.compatible == True:
            g.m64p_wrapper.ConfigOpenSection('Core')
        paths_tab = Gtk.Label(label="Paths")

        paths_box = Gtk.VBox()
        m64p_paths_grid2 = Gtk.Grid()
        gamedir_box = Gtk.HBox()

        m64p_frame = Gtk.Frame(label="mupen64plus directories", shadow_type=1)
        gamedir_frame = Gtk.Frame(label="game image directories", shadow_type=1)

        sram_dir_entry = self.insert_entry('SaveSRAMPath', 'Core', 'm64p', "Choose a dir where SRAM/EEPROM/FlashRAM saves will be stored", None)
        sram_dir_button = Gtk.Button.new_with_label("Open")
        sram_dir_button.connect("clicked", self.on_search_path_dir, sram_dir_entry)

        shared_dir_entry = self.insert_entry('SharedDataPath', 'Core', 'm64p', "Choose a dir where shared data will be stored", None)
        shared_data_dir_button = Gtk.Button.new_with_label("Open")
        shared_data_dir_button.connect("clicked", self.on_search_path_dir, shared_dir_entry)

        save_dir_entry = self.insert_entry('SaveStatePath', 'Core', 'm64p', "Choose a dir where save states will be stored", None)
        save_dir_button = Gtk.Button.new_with_label("Open")
        save_dir_button.connect("clicked", self.on_search_path_dir, save_dir_entry)

        screenshot_entry = self.insert_entry('ScreenshotPath', 'Core', 'm64p', "Choose a dir where screenshots will be stored", None)
        screenshot_button = Gtk.Button.new_with_label("Open")
        screenshot_button.connect("clicked", self.on_search_path_dir, screenshot_entry)

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

        m64p_frame.add(m64p_paths_grid2)

        # TODO: Replace with ListStore or CellRenderer? to allow multi directories
        g.frontend_conf.open_section("GameDirs")
        gamedir_entry = self.insert_entry('path1', 'GameDirs', 'frontend', "Choose the dir where game images are found", None)
        gamedir_button = Gtk.Button.new_with_label("Open")
        gamedir_button.connect("clicked", self.on_search_path_dir, gamedir_entry)

        gamedir_box.pack_start(gamedir_entry, True, True, 5)
        gamedir_box.pack_start(gamedir_button, False, False, 0)
        gamedir_frame.add(gamedir_box)

        paths_box.pack_start(m64p_frame, False, False, 0)
        paths_box.pack_start(gamedir_frame, False, False, 0)
        g.frontend_conf.open_section("Frontend")

        config_notebook.append_page(paths_box, paths_tab)

        #Hotkey Tab

        # NOTE: get_content_area() is needed because a Gtk.Box already exists as the child container of the Gtk.Dialog, let's give a name to dialog's box
        self.config_box = self.config_window.get_content_area()
        self.config_box.add(config_notebook)
        self.config_window.show_all()

        # NOTE: "while" is needed to relaunch dialog if Apply Button was hit
        response = Gtk.ResponseType.APPLY
        while response == Gtk.ResponseType.APPLY:
            response = self.config_window.run()
            if response == Gtk.ResponseType.OK:
                g.frontend_conf.write()

                if g.lock == False and g.m64p_wrapper.compatible == True:
                    g.m64p_wrapper.plugins_preload()
                    g.m64p_wrapper.plugins_startup()
                    g.m64p_wrapper.ConfigSaveFile()

                    #g.m64p_wrapper.restart(g.frontend_conf.get('CoreLib'))

                self.config_window.destroy()
            elif response == Gtk.ResponseType.APPLY:
                g.frontend_conf.write()
                if self.is_changed == True:
                    self.apply_button.set_sensitive(False)
                    self.former_update()

                    if g.lock == False and g.m64p_wrapper.compatible == True:
                        if g.m64p_wrapper.ConfigHasUnsavedChanges("Core") == True:
                            g.m64p_wrapper.ConfigSaveSection("Core")
                        if g.m64p_wrapper.ConfigHasUnsavedChanges("CoreEvents") == True:
                            g.m64p_wrapper.ConfigSaveSection("CoreEvents")
                        if g.m64p_wrapper.ConfigHasUnsavedChanges("Video-General") == True:
                            g.m64p_wrapper.ConfigSaveSection("Video-General")

                if g.lock == False and g.m64p_wrapper.compatible == True:
                    g.m64p_wrapper.plugins_preload()
                    #g.m64p_wrapper.restart(g.frontend_conf.get('CoreLib'))

            else:
                if self.is_changed == True:
                    self.revert()

                    if g.lock == False and g.m64p_wrapper.compatible == True:
                        if g.m64p_wrapper.ConfigHasUnsavedChanges("Core") == True:
                            g.m64p_wrapper.ConfigRevertChanges("Core")
                        if g.m64p_wrapper.ConfigHasUnsavedChanges("CoreEvents") == True:
                            g.m64p_wrapper.ConfigRevertChanges("CoreEvents")
                        if g.m64p_wrapper.ConfigHasUnsavedChanges("Video-General") == True:
                            g.m64p_wrapper.ConfigRevertChanges("Video-General")

                if g.lock == False and g.m64p_wrapper.compatible == True:
                    g.m64p_wrapper.plugins_startup()
                self.config_window.destroy()

    def on_combobox_changed(self, widget, param):
        self.is_changed = True
        self.apply_button.set_sensitive(True)
        widget_id = widget.get_active_id()
        active_plugin = os.path.splitext(widget_id)[0]
        if param == 'R4300Emulator':
            g.m64p_wrapper.ConfigOpenSection('Core')
            g.m64p_wrapper.ConfigSetParameter('R4300Emulator', int(widget_id))
        elif param == 'Language':
            g.frontend_conf.set('Language', str(widget_id))
        elif param == 'GfxPlugin':
            g.frontend_conf.set('GfxPlugin', widget_id)
            g.m64p_wrapper.gfx_filename = widget_id
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
        elif param == 'AudioPlugin':
            g.frontend_conf.set('AudioPlugin', widget_id)
            g.m64p_wrapper.audio_filename = widget_id
            if active_plugin == 'mupen64plus-audio-sdl':
                self.audio_configure_button.set_sensitive(True)
            else:
                self.audio_configure_button.set_sensitive(False)
        elif param == 'InputPlugin':
            g.frontend_conf.set('InputPlugin', widget_id)
            g.m64p_wrapper.input_filename = widget_id
            if active_plugin == 'mupen64plus-input-sdl':
                self.input_configure_button.set_sensitive(True)
            elif active_plugin == 'mupen64plus-input-raphnetraw':
                self.input_configure_button.set_sensitive(False)
            else:
                self.input_configure_button.set_sensitive(False)
        elif param == 'RSPPlugin':
            g.frontend_conf.set('RSPPlugin', widget_id)
            g.m64p_wrapper.rsp_filename = widget_id
            if active_plugin == 'mupen64plus-rsp-hle':
                self.rsp_configure_button.set_sensitive(True)
            elif active_plugin == 'mupen64plus-rsp-cxd4':
                self.rsp_configure_button.set_sensitive(True)
            elif active_plugin == 'mupen64plus-rsp-z64':
                self.rsp_configure_button.set_sensitive(True)
            else:
                self.rsp_configure_button.set_sensitive(False)
        elif param == 'Rotate':
            g.m64p_wrapper.ConfigOpenSection('Video-General')
            g.m64p_wrapper.ConfigSetParameter('Rotate', int(widget_id))
        else:
            print("Config: Unknown parameter.")

    def on_checkbox_toggled(self, widget, section, param):
        self.is_changed = True
        self.apply_button.set_sensitive(True)
        if section != None:
            g.m64p_wrapper.ConfigOpenSection(section)
            if widget.get_active() == True:
                g.m64p_wrapper.ConfigSetParameter(param, True)
            elif widget.get_active() == False:
                g.m64p_wrapper.ConfigSetParameter(param, False)
            else:
                print("Config: Unexpected error")

    def on_spinbutton_changed(self, widget, section, param):
        self.is_changed = True
        self.apply_button.set_sensitive(True)
        if section != None:
            g.m64p_wrapper.ConfigOpenSection(section)
            g.m64p_wrapper.ConfigSetParameter(param, widget.get_value_as_int())

    def on_search_path_lib(self, widget, entry):
        dialog = w_dialog.LibraryChooserDialog(self.config_window)
        library = dialog.path
        if library != None:
            self.is_changed = True
            self.apply_button.set_sensitive(True)
            entry.set_text(library)

    def on_search_path_dir(self, widget, entry):
        dialog = w_dialog.DirChooserDialog(self.config_window)
        dir_path = dialog.path
        if dir_path != None:
            self.is_changed = True
            self.apply_button.set_sensitive(True)
            entry.set_text(dir_path)

    def on_configure_button(self, widget, parent, plugin):
        w_plugin.PluginDialog(parent, plugin)

    def on_entry_changed(self, widget, section, param):
        self.is_changed = True
        self.apply_button.set_sensitive(True)
        value = widget.get_text()
        if section == "Frontend" or section == "GameDirs":
            g.frontend_conf.open_section(section)
            g.frontend_conf.set(param, value)
        else:
            g.m64p_wrapper.ConfigOpenSection(section)
            g.m64p_wrapper.ConfigSetParameter(param, value)
        #print(section, param, value)

    def revert(self):
        self.is_changed = False
        self.apply_button.set_sensitive(False)
        g.frontend_conf.open_section("Frontend")
        g.frontend_conf.set('PluginsDir', self.former_values['plugins_dir'])
        g.frontend_conf.set('ConfigDir', self.former_values['config_dir'])
        g.frontend_conf.set('DataDir', self.former_values['data_dir'])
        #g.frontend_conf.set('GameDirs', self.former_values['game_directories'])
        g.frontend_conf.set('GfxPlugin', self.former_values['gfx_plugin'])
        g.frontend_conf.set('AudioPlugin', self.former_values['audio_plugin'])
        g.frontend_conf.set('InputPlugin', self.former_values['input_plugin'])
        g.frontend_conf.set('RSPPlugin', self.former_values['rsp_plugin'])
        g.frontend_conf.open_section("GameDirs")
        g.frontend_conf.set('path1', self.former_values['path1'])
        g.frontend_conf.set('path2', self.former_values['path2'])
        g.frontend_conf.set('path3', self.former_values['path3'])

    def former_update(self):
        self.is_changed = False
        g.frontend_conf.open_section("Frontend")
        self.former_values['plugins_dir'] = g.frontend_conf.get('PluginsDir')
        self.former_values['config_dir'] = g.frontend_conf.get('ConfigDir')
        self.former_values['data_dir'] = g.frontend_conf.get('DataDir')
        #self.former_values['game_directories'] = g.frontend_conf.get('GameDirs')
        self.former_values['gfx_plugin'] = g.frontend_conf.get('GfxPlugin')
        self.former_values['audio_plugin'] = g.frontend_conf.get('AudioPlugin')
        self.former_values['input_plugin'] = g.frontend_conf.get('InputPlugin')
        self.former_values['rsp_plugin'] = g.frontend_conf.get('RSPPlugin')
        g.frontend_conf.open_section("GameDirs")
        self.former_values['path1'] = g.frontend_conf.get('path1')
        self.former_values['path2'] = g.frontend_conf.get('path2')
        self.former_values['path3'] = g.frontend_conf.get('path3')

    def insert_entry(self, param, section, config, placeholder, help):
        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        entry.set_hexpand(True)
        if config == "frontend":
            if g.frontend_conf.get(param) != None:
                entry.set_text(g.frontend_conf.get(param))
        elif config == "m64p":
            if g.lock == False and g.m64p_wrapper.compatible == True:
                if g.m64p_wrapper.ConfigGetParameter(param) != None:
                    entry.set_text(g.m64p_wrapper.ConfigGetParameter(param))
            else:
                entry.set_sensitive(False)
        entry.connect("changed", self.on_entry_changed, section, param)
        return entry

    def insert_checkbox(self, param, section, config, label, help):
        checkbox = Gtk.CheckButton.new_with_label(label)
        if config == "frontend":
            if g.frontend_conf.get(param) == True:
                checkbox.set_active(True)
        elif config == "m64p":
            if g.lock == False and g.m64p_wrapper.compatible == True:
                if g.m64p_wrapper.ConfigGetParameter(param) == True:
                    checkbox.set_active(True)
            else:
                checkbox.set_sensitive(False)
        checkbox.connect("toggled", self.on_checkbox_toggled, section, param)
        return checkbox
        
