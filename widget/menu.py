#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, GLib
import logging as log

import widget.configure as w_conf
import widget.dialog as w_dialog
import widget.plugin as w_plugin
import widget.media as w_media

###############
## VARIABLES ##
###############

#############
## CLASSES ##
#############

class Menu:
    def __init__(self, parent):
        self.parent = parent
        self.active_slot = self.parent.m64p_wrapper.current_slot # Don't ever remove it!
        self.toolbar_call()
        self.menubar_call()

    def toolbar_call(self):
        self.toolbar = Gtk.Toolbar()

        self.toolbar_load_rom = self.insert_toolbar_item("document-open", self.parent.action.return_state_lock(), self.on_choosing_rom)
        self.toolbar_play = self.insert_toolbar_item("media-playback-start", False, self.parent.action.on_resume)
        self.toolbar_pause = self.insert_toolbar_item("media-playback-pause", False, self.parent.action.on_pause)
        self.toolbar_stop = self.insert_toolbar_item("media-playback-stop", False, self.parent.action.on_stop)
        self.toolbar_next = self.insert_toolbar_item("media-skip-forward", False, self.parent.action.on_advance)
        self.toolbar_save_state = self.insert_toolbar_item("document-save", False, self.parent.action.on_savestate)
        self.toolbar_load_state = self.insert_toolbar_item("document-revert", False, self.parent.action.on_loadstate)

        self.toolbar_configure = Gtk.ToolButton(icon_name="preferences-system")
        self.toolbar_configure.connect_object("clicked", w_conf.ConfigDialog, self.parent)

        self.toolbar_fullscreen = self.insert_toolbar_item("view-fullscreen", False, self.parent.action.on_fullscreen)
        self.toolbar_screenshot = self.insert_toolbar_item("camera-photo", False, self.parent.action.on_screenshot)

        self.toolbar.insert(self.toolbar_load_rom, 0)
        self.toolbar.insert(Gtk.SeparatorToolItem(), 1)
        self.toolbar.insert(self.toolbar_play, 2)
        self.toolbar.insert(self.toolbar_pause, 3)
        self.toolbar.insert(self.toolbar_stop, 4)
        self.toolbar.insert(self.toolbar_next, 5)
        self.toolbar.insert(Gtk.SeparatorToolItem(), 6)
        self.toolbar.insert(self.toolbar_save_state, 7)
        self.toolbar.insert(self.toolbar_load_state, 8)
        self.toolbar.insert(Gtk.SeparatorToolItem(), 9)
        self.toolbar.insert(self.toolbar_configure, 10)
        self.toolbar.insert(self.toolbar_fullscreen, 11)
        self.toolbar.insert(self.toolbar_screenshot, 12)

        return self.toolbar

    def menubar_call(self):
        self.menubar = Gtk.MenuBar()

        ## "File" Menu ##
        self.file_menu = Gtk.Menu()
        self.file_menu_label = Gtk.MenuItem(label="File")
        self.file_menu_label.set_submenu(self.file_menu)


        self.file_menu_loadrom = self.insert_menu_item("Load ROM", self.parent.action.return_state_lock(), self.on_choosing_rom, None)

        self.file_menu_reload = Gtk.MenuItem(label="Refresh list")
        self.file_menu_reload.set_sensitive(self.parent.action.return_state_lock())
        #self.file_menu_reload.connect("activate", self.on_UnloadRom)

        #self.recent_chooser_cb = Gtk.RecentChooser
        #self.recent_chooser_cb.set_limit(10)
        self.recent_manager = Gtk.RecentManager.get_default()
        self.recent_filter = Gtk.RecentFilter()
        self.recent_filter.add_pattern('*.z64')
        self.recent_filter.add_pattern('*.v64')
        self.recent_filter.add_pattern('*.n64')

        self.file_menu_recents = Gtk.MenuItem(label="Recents")
        self.file_menu_recents.set_sensitive(self.parent.action.return_state_lock())
        self.file_menu_recents_submenu = Gtk.RecentChooserMenu.new_for_manager(self.recent_manager)
        self.file_menu_recents_submenu.set_show_numbers(False)
        self.file_menu_recents_submenu.add_filter(self.recent_filter)
        self.file_menu_recents_submenu.connect("item-activated", self.on_recent_activated)
        #self.file_menu_recents_clear_recents = Gtk.MenuItem(label="Clear history")
        #self.file_menu_recents.append(self.file_menu_recents_clear_recents) # self.recent_manager.purge_items()

        self.file_menu_recents.set_submenu(self.file_menu_recents_submenu)

        self.file_menu_quit = Gtk.MenuItem(label="Quit")

        self.file_menu.append(self.file_menu_loadrom)
        self.file_menu.append(self.file_menu_reload)
        self.file_menu.append(self.file_menu_recents)
        self.file_menu.append(Gtk.SeparatorMenuItem())
        self.file_menu.append(self.file_menu_quit)
        self.menubar.append(self.file_menu_label)

        ## "Emulation" Menu ##
        self.emulation_menu = Gtk.Menu()
        self.emulation_menu_label = Gtk.MenuItem(label="Emulation")
        self.emulation_menu_label.set_submenu(self.emulation_menu)

        self.emulation_menu_play = self.insert_menu_item("Play", False, self.parent.action.on_resume, None)
        self.emulation_menu_pause = self.insert_menu_item("Pause", False, self.parent.action.on_pause, None)
        self.emulation_menu_stop = self.insert_menu_item("Stop", False, self.parent.action.on_stop, None)
        self.emulation_menu_soft_reset = self.insert_menu_item("Soft reset", False, self.parent.action.on_sreset, None)
        self.emulation_menu_hard_reset = self.insert_menu_item("Hard reset", False, self.parent.action.on_hreset, None)
        self.emulation_menu_save_state = self.insert_menu_item("Save state", False, self.parent.action.on_savestate, option=False)
        self.emulation_menu_save_state_as = self.insert_menu_item("Save state as...", False, self.parent.action.on_savestate, option=True)
        self.emulation_menu_load_state = self.insert_menu_item("Load state", False, self.parent.action.on_loadstate, option=False)
        self.emulation_menu_load_state_from = self.insert_menu_item("Load state from...", False, self.parent.action.on_loadstate, option=True)

        self.save_slot_menu = Gtk.Menu()
        self.save_slot_items = list(["Slot 0", "Slot 1", "Slot 2", "Slot 3", "Slot 4", "Slot 5", "Slot 6", "Slot 7", "Slot 8", "Slot 9"])
        group = []
        for i in range(0,10):
            menu_item = Gtk.RadioMenuItem.new_with_label(group, "Slot "+ str(i))
            group = menu_item.get_group()
            self.save_slot_items[i] = menu_item
            self.save_slot_menu.append(menu_item)
            menu_item.connect("activate", self.on_slot_select, i)

        self.emulation_menu_current_slot = self.insert_menu_item("Current save state slot", False, None, self.save_slot_menu)
        self.emulation_menu_transfer_pak = self.insert_menu_item_obj("Media Loader", self.parent.action.return_state_lock(), w_media.MediaDialog, self.parent)


        self.emulation_menu.append(self.emulation_menu_play)
        self.emulation_menu.append(self.emulation_menu_pause)
        self.emulation_menu.append(self.emulation_menu_stop)
        self.emulation_menu.append(self.emulation_menu_soft_reset)
        self.emulation_menu.append(self.emulation_menu_hard_reset)
        self.emulation_menu.append(Gtk.SeparatorMenuItem())
        self.emulation_menu.append(self.emulation_menu_save_state)
        self.emulation_menu.append(self.emulation_menu_save_state_as)
        self.emulation_menu.append(self.emulation_menu_load_state)
        self.emulation_menu.append(self.emulation_menu_load_state_from)
        self.emulation_menu.append(Gtk.SeparatorMenuItem())
        # "Current save state slot" submenu
        self.emulation_menu.append(self.emulation_menu_current_slot)
        self.emulation_menu.append(Gtk.SeparatorMenuItem())
        self.emulation_menu.append(self.emulation_menu_transfer_pak)
        self.menubar.append(self.emulation_menu_label)
        # End submenu

        ## "Options" Menu ##
        self.options_menu = Gtk.Menu()
        self.options_menu_label = Gtk.MenuItem(label="Options")
        self.options_menu_label.set_submenu(self.options_menu)

        self.options_menu_configure = self.insert_menu_item_obj("Configure", True, w_conf.ConfigDialog, self.parent)
        self.options_menu_gfx_configure = self.insert_menu_item_obj("Graphics Plugin", self.parent.action.return_state_lock(), w_plugin.PluginDialog, self.parent, 'gfx')
        self.options_menu_audio_configure = self.insert_menu_item_obj("Audio Plugin", self.parent.action.return_state_lock(), w_plugin.PluginDialog, self.parent, 'audio')
        self.options_menu_input_configure = self.insert_menu_item_obj("Input Plugin", self.parent.action.return_state_lock(), w_plugin.PluginDialog, self.parent, 'input')
        self.options_menu_rsp_configure = self.insert_menu_item_obj("RSP Plugin", self.parent.action.return_state_lock(), w_plugin.PluginDialog, self.parent, 'rsp')
        self.options_menu_fullscreen = self.insert_menu_item("Full screen", False, self.parent.action.on_fullscreen, None)

        self.options_menu.append(self.options_menu_configure)
        self.options_menu.append(Gtk.SeparatorMenuItem())
        self.options_menu.append(self.options_menu_gfx_configure)
        self.options_menu.append(self.options_menu_audio_configure)
        self.options_menu.append(self.options_menu_input_configure)
        self.options_menu.append(self.options_menu_rsp_configure)
        self.options_menu.append(Gtk.SeparatorMenuItem())
        self.options_menu.append(self.options_menu_fullscreen)
        self.menubar.append(self.options_menu_label)

        ## "View" Menu ##
        self.view_menu = Gtk.Menu()
        self.view_menu_label = Gtk.MenuItem(label="View")
        self.view_menu_label.set_submenu(self.view_menu)
        self.view_menu_toolbar = Gtk.CheckMenuItem(label="Toolbar")
        self.view_menu_filter = Gtk.CheckMenuItem(label="Filter")
        self.view_menu_status = Gtk.CheckMenuItem(label="Status")
        self.view_menu_debugger = Gtk.MenuItem(label="Debugger")

        self.view_menu_toolbar.connect("toggled", self.parent.action.on_toolbar_toggle)

        self.view_menu.append(self.view_menu_toolbar)
        self.view_menu.append(self.view_menu_filter)
        self.view_menu.append(self.view_menu_status)
        #self.view_menu.append(Gtk.SeparatorMenuItem())
        # "Debugger" submenu
        self.debugger_menu = Gtk.Menu()
        #self.view_menu.append(self.view_menu_debugger)
        #self.view_menu_debugger.set_submenu(self.debugger_menu)

        self.debugger_menu_enable = Gtk.CheckMenuItem(label="Debugger")
        self.debugger_menu_registers = Gtk.MenuItem(label="Registers")
        self.debugger_menu_breakpoints = Gtk.MenuItem(label="Breakpoints")
        self.debugger_menu_tlb = Gtk.MenuItem(label="TLB")
        self.debugger_menu_memory = Gtk.MenuItem(label="Memory")
        self.debugger_menu_variables = Gtk.MenuItem(label="Variables")

        self.debugger_menu.append(self.debugger_menu_enable)
        self.debugger_menu.append(self.debugger_menu_registers)
        self.debugger_menu.append(self.debugger_menu_breakpoints)
        self.debugger_menu.append(self.debugger_menu_tlb)
        self.debugger_menu.append(self.debugger_menu_memory)
        self.debugger_menu.append(self.debugger_menu_variables)

        self.view_menu_debugger.set_sensitive(False)
        # End submenu
        self.menubar.append(self.view_menu_label)

        ## "Help" Menu
        self.help_menu = Gtk.Menu()
        self.help_menu_label = Gtk.MenuItem(label="Help")
        self.help_menu_label.set_submenu(self.help_menu)

        self.help_menu_about_core = self.insert_menu_item_obj("About mupen64plus", True, w_dialog.DialogAbout, self.parent, "core")
        self.help_menu_about_frontend = self.insert_menu_item_obj("About the frontend", True, w_dialog.DialogAbout, self.parent, "frontend")

        self.help_menu.append(self.help_menu_about_core)
        self.help_menu.append(self.help_menu_about_frontend)
        self.menubar.append(self.help_menu_label)

        return self.menubar

    # def on_EnableToolbar_toggle(self, *args):
    #     if self.view_menu_toolbar.get_active() == True:
    #         self.toolbar.show_all()
    #         self.parent.frontend_conf.set("Frontend", "ToolbarConfig", "True")
    #     else:
    #         self.toolbar.hide()
    #         self.parent.frontend_conf.set("Frontend", "ToolbarConfig", "False")

    def on_choosing_rom(self, *args):
        dialog = w_dialog.FileChooserDialog(self.parent, "rom")
        self.parent.Statusbar.push(self.parent.StatusbarContext, "Selecting the ROM...")
        self.parent.rom = dialog.path
        if dialog.path != None:
            rom_uri = GLib.filename_to_uri(self.parent.rom, None)
            if self.recent_manager.has_item(rom_uri) == False:
                self.recent_manager.add_item(rom_uri)

        self.parent.action.thread_rom()

    def on_slot_select(self, widget, slot):
        if self.active_slot != slot:
            self.active_slot = slot
            self.parent.m64p_wrapper.state_set_slot(slot)

    def sensitive_menu_run(self, *args):
        self.file_menu_loadrom.set_sensitive(False)
        self.file_menu_reload.set_sensitive(False)
        self.file_menu_recents.set_sensitive(False)
        self.emulation_menu_play.set_sensitive(False)
        self.emulation_menu_pause.set_sensitive(True)
        self.emulation_menu_stop.set_sensitive(True)
        self.emulation_menu_soft_reset.set_sensitive(True)
        self.emulation_menu_hard_reset.set_sensitive(True)
        self.emulation_menu_save_state.set_sensitive(True)
        self.emulation_menu_save_state_as.set_sensitive(True)
        self.emulation_menu_load_state.set_sensitive(True)
        self.emulation_menu_load_state_from.set_sensitive(True)
        self.emulation_menu_current_slot.set_sensitive(True)
        self.options_menu_configure.set_sensitive(False)
        self.options_menu_gfx_configure.set_sensitive(False)
        self.options_menu_audio_configure.set_sensitive(False)
        self.options_menu_input_configure.set_sensitive(False)
        self.options_menu_rsp_configure.set_sensitive(False)
        self.options_menu_fullscreen.set_sensitive(True)
        self.toolbar_load_rom.set_sensitive(False)
        self.toolbar_play.set_sensitive(False)
        self.toolbar_pause.set_sensitive(True)
        self.toolbar_stop.set_sensitive(True)
        self.toolbar_save_state.set_sensitive(True)
        self.toolbar_load_state.set_sensitive(True)
        self.toolbar_configure.set_sensitive(False)
        self.toolbar_fullscreen.set_sensitive(True)
        self.toolbar_screenshot.set_sensitive(True)
        self.toolbar_next.set_sensitive(False)

    def sensitive_menu_stop(self, *args):
        self.file_menu_loadrom.set_sensitive(True)
        self.file_menu_reload.set_sensitive(True)
        self.file_menu_recents.set_sensitive(True)
        self.emulation_menu_play.set_sensitive(False)
        self.emulation_menu_pause.set_sensitive(False)
        self.emulation_menu_stop.set_sensitive(False)
        self.emulation_menu_soft_reset.set_sensitive(False)
        self.emulation_menu_hard_reset.set_sensitive(False)
        self.emulation_menu_save_state.set_sensitive(False)
        self.emulation_menu_save_state_as.set_sensitive(False)
        self.emulation_menu_load_state.set_sensitive(False)
        self.emulation_menu_load_state_from.set_sensitive(False)
        self.emulation_menu_current_slot.set_sensitive(False)
        self.options_menu_configure.set_sensitive(True)
        self.options_menu_gfx_configure.set_sensitive(True)
        self.options_menu_audio_configure.set_sensitive(True)
        self.options_menu_input_configure.set_sensitive(True)
        self.options_menu_rsp_configure.set_sensitive(True)
        self.options_menu_fullscreen.set_sensitive(False)
        self.toolbar_load_rom.set_sensitive(True)
        self.toolbar_play.set_sensitive(False)
        self.toolbar_pause.set_sensitive(False)
        self.toolbar_stop.set_sensitive(False)
        self.toolbar_save_state.set_sensitive(False)
        self.toolbar_load_state.set_sensitive(False)
        self.toolbar_configure.set_sensitive(True)
        self.toolbar_fullscreen.set_sensitive(False)
        self.toolbar_screenshot.set_sensitive(False)
        self.toolbar_next.set_sensitive(False)

    def sensitive_menu_pause(self, *args):
        self.emulation_menu_play.set_sensitive(True)
        self.emulation_menu_pause.set_sensitive(False)
        self.toolbar_play.set_sensitive(True)
        self.toolbar_pause.set_sensitive(False)
        self.toolbar_next.set_sensitive(True)

    def insert_toolbar_item(self, name, sensitive, action):
        item = Gtk.ToolButton(icon_name=name)
        item.set_sensitive(sensitive)
        item.connect("clicked", action)

        return item

    def insert_menu_item(self, label, sensitive, action=None, option=None, submenu=None):
        item = Gtk.MenuItem(label=label)
        item.set_sensitive(sensitive)
        if action != None:
            item.connect("activate", action, option)
        #if append_item != None:
        #    item.append(append_item)
        if submenu != None:
            item.set_submenu(submenu)

        return item

    def insert_menu_item_obj(self, label, sensitive, obj, value1=None, value2=None, value3=None):
        item = Gtk.MenuItem(label=label)
        item.set_sensitive(sensitive)
        if value1 != None and value2 == None and value3 == None:
            item.connect_object("activate", obj, value1)
        elif value1 != None and value2 != None and value3 == None:
            item.connect_object("activate", obj, value1, value2)
        elif value1 != None and value2 != None and value3 != None:
            item.connect_object("activate", obj, value1, value2, value3)
        return item

    def on_recent_activated(self, widget):
        #item = recentchoosermenu.get_current_item()
        #if item:
        #    name = item.get_display_name()
        #    uri = item.get_uri()
        #   log.debug(f"Recent item selected: {name}, {uri}")
            
        rom_uri = widget.get_current_uri()
        raw_path = GLib.filename_from_uri(rom_uri)
        self.parent.rom = raw_path[0]

        self.parent.action.thread_rom()
