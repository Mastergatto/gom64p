#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, GLib, Gio
import logging as log
import pathlib

import widget.configure as w_conf
import widget.dialog as w_dialog
import widget.plugin as w_plugin
import widget.media as w_media

###############
## VARIABLES ##
###############

map_slot = { "slot-zero": 0,
             "slot-one": 1,
             "slot-two": 2,
             "slot-three": 3,
             "slot-four": 4,
             "slot-five": 5,
             "slot-six": 6,
             "slot-seven": 7,
             "slot-eight": 8,
             "slot-nine": 9
            }

#############
## CLASSES ##
#############

class Menu:
    def __init__(self, parent):
        self.frontend = parent
        self.active_slot = self.frontend.m64p_wrapper.current_slot # Don't ever remove it!

    def toolbar_init(self):
        self.toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.toolbar.add_css_class("toolbar")

        self.toolbar_load_rom = self.insert_toolbar_item("document-open", self.frontend.action.return_state_lock(), self.on_choosing_rom)
        self.toolbar_play = self.insert_toolbar_item("media-playback-start", False, self.frontend.action.on_resume)
        self.toolbar_pause = self.insert_toolbar_item("media-playback-pause", False, self.frontend.action.on_pause)
        self.toolbar_stop = self.insert_toolbar_item("media-playback-stop", False, self.frontend.action.on_stop)
        self.toolbar_next = self.insert_toolbar_item("media-skip-forward", False, self.frontend.action.on_advance)
        self.toolbar_save_state = self.insert_toolbar_item("document-save", False, self.frontend.action.on_savestate)
        self.toolbar_load_state = self.insert_toolbar_item("document-revert", False, self.frontend.action.on_loadstate)

        self.toolbar_configure = Gtk.Button(icon_name="preferences-system")
        self.toolbar_configure.connect_object("clicked", w_conf.ConfigDialog, self.frontend, None)

        self.toolbar_fullscreen = self.insert_toolbar_item_obj("view-fullscreen", False, self.frontend.action.on_fullscreen, True)
        self.toolbar_screenshot = self.insert_toolbar_item("camera-photo", False, self.frontend.action.on_screenshot)

        self.toolbar.append(self.toolbar_load_rom)
        self.toolbar.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self.toolbar.append(self.toolbar_play)
        self.toolbar.append(self.toolbar_pause)
        self.toolbar.append(self.toolbar_stop)
        self.toolbar.append(self.toolbar_next)
        self.toolbar.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self.toolbar.append(self.toolbar_save_state)
        self.toolbar.append(self.toolbar_load_state)
        self.toolbar.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self.toolbar.append(self.toolbar_configure)
        self.toolbar.append(self.toolbar_fullscreen)
        self.toolbar.append(self.toolbar_screenshot)

        if self.frontend.frontend_conf.get("Frontend", "ToolbarConfig") == "False":
            self.toolbar.hide()

        return self.toolbar

    def menubar_call2(self):
        # TODO: Remove

        #self.recent_chooser_cb = Gtk.RecentChooser
        #self.recent_chooser_cb.set_limit(10)
        self.recent_manager = Gtk.RecentManager.get_default()
        self.recent_filter = Gtk.RecentFilter()
        self.recent_filter.add_pattern('*.z64')
        self.recent_filter.add_pattern('*.v64')
        self.recent_filter.add_pattern('*.n64')

        self.file_menu_recents = Gtk.MenuItem(label="Recents")
        self.file_menu_recents.set_sensitive(self.frontend.action.return_state_lock())
        self.file_menu_recents_submenu = Gtk.RecentChooserMenu.new_for_manager(self.recent_manager)
        self.file_menu_recents_submenu.set_show_numbers(False)
        self.file_menu_recents_submenu.add_filter(self.recent_filter)
        self.file_menu_recents_submenu.connect("item-activated", self.on_recent_activated)
        #self.file_menu_recents_clear_recents = Gtk.MenuItem(label="Clear history")
        #self.file_menu_recents.append(self.file_menu_recents_clear_recents) # self.recent_manager.purge_items()

        self.file_menu_recents.set_submenu(self.file_menu_recents_submenu)



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

    def menubar_init(self):
        self.model = Gtk.Builder()
        self.model.add_from_file(str(pathlib.Path("../data/ui/menubar.ui")))

        self.menubar = Gtk.PopoverMenuBar.new_from_model(self.model.get_object('menubar'))

        ## "File" Menu ##
        self.file_menu_loadrom = self.insert_action("simple", "open", not self.frontend.lock, self.on_choosing_rom)
        self.file_menu_refresh = self.insert_action("simple", "refresh", not self.frontend.lock, self.frontend.on_refresh)
        #self.file_menu_recents
        self.file_menu_quit = self.insert_action("simple", "quit", True, self.frontend.quit_cb)

        ## "Emulation" Menu ##
        self.emulation_menu_play = self.insert_action("simple", "play", False, self.frontend.action.on_resume)
        self.emulation_menu_pause = self.insert_action("simple", "pause", False, self.frontend.action.on_pause)
        self.emulation_menu_stop = self.insert_action("simple", "stop", False, self.frontend.action.on_stop)
        self.emulation_menu_soft_reset = self.insert_action("simple", "sreset", False, self.frontend.action.on_sreset)
        self.emulation_menu_hard_reset = self.insert_action("simple", "hreset", False, self.frontend.action.on_hreset)
        self.emulation_menu_save_state = self.insert_action("simple", "save", False, self.frontend.action.on_savestate, option1=False)
        self.emulation_menu_save_state_as = self.insert_action("simple", "save-as", False, self.frontend.action.on_savestate, option1=True)
        self.emulation_menu_load_state = self.insert_action("simple", "load", False, self.frontend.action.on_loadstate, option1=False)
        self.emulation_menu_load_state_from = self.insert_action("simple", "load-from", False, self.frontend.action.on_loadstate, option1=True)

        self.emulation_menu_current_slot = self.insert_action("radio", "radioslot", False, self.on_slot_select, target="slot-zero")
        self.emulation_menu_media_loader = self.insert_action("simple", "media-loader", True, w_media.MediaDialog, option1=self.frontend)

        ## "Options" Menu ##
        self.options_menu_configure = self.insert_action("simple", "configure", True, w_conf.ConfigDialog, option1=self.frontend)
        self.options_menu_gfx_configure = self.insert_action("simple", "gfx", not self.frontend.lock, w_plugin.PluginDialog, option1=self.frontend, option2='gfx')
        self.options_menu_audio_configure = self.insert_action("simple", "audio", not self.frontend.lock, w_plugin.PluginDialog, option1=self.frontend, option2='audio')
        self.options_menu_input_configure = self.insert_action("simple", "input", not self.frontend.lock, w_plugin.PluginDialog, option1=self.frontend, option2='input')
        self.options_menu_rsp_configure = self.insert_action("simple", "rsp", not self.frontend.lock, w_plugin.PluginDialog, option1=self.frontend, option2='rsp')
        self.options_menu_fullscreen = self.insert_action("simple", "fullscreen", False, self.frontend.action.on_fullscreen, option1=True)

        ## "View" Menu ##
        self.view_menu_toolbar = self.insert_action("checkbox", "view-tool", True, self.on_toolbar_toggle, option1=self.frontend.frontend_conf.get_bool("Frontend", "ToolbarConfig"))
        self.view_menu_filter = self.insert_action("checkbox", "view-filter", True, self.on_filter_toggle, option1=self.frontend.frontend_conf.get_bool("Frontend", "FilterConfig"))
        self.view_menu_status = self.insert_action("checkbox", "view-status", True, self.on_statusbar_toggle, option1=self.frontend.frontend_conf.get_bool("Frontend", "StatusConfig"))

        ## "Help" Menu ##
        self.help_menu_about_core = self.insert_action("simple", "about_m64p", True, w_dialog.DialogAbout, option1=self.frontend, option2="core")
        self.help_menu_about_frontend = self.insert_action("simple", "about_frontend", True, w_dialog.DialogAbout, option1=self.frontend, option2="frontend")

        return self.menubar

    def on_choosing_rom(self, *args):
        dialog = w_dialog.FileChooserDialog(self.frontend, "rom", None)
        self.frontend.action.status_push("Selecting the ROM...")
        self.frontend.rom = dialog.path
        if dialog.path != None:
            rom_uri = GLib.filename_to_uri(self.frontend.rom, None)
            if self.recent_manager.has_item(rom_uri) == False:
                self.recent_manager.add_item(rom_uri)

        self.frontend.action.thread_rom()

    def on_slot_select(self, action, slot):
        action.set_state(slot)
        s_slot = slot.get_string()
        if self.active_slot != map_slot[s_slot]:
            self.active_slot = map_slot[s_slot]
            self.frontend.m64p_wrapper.state_set_slot(map_slot[s_slot])

    def sensitive_menu_run(self, *args):
        self.file_menu_loadrom.set_property("enabled", False)
        self.file_menu_refresh.set_property("enabled", False)
        # self.file_menu_recents.set_property("enabled", False)
        self.emulation_menu_play.set_property("enabled", False)
        self.emulation_menu_pause.set_property("enabled", True)
        self.emulation_menu_stop.set_property("enabled", True)
        self.emulation_menu_soft_reset.set_property("enabled", True)
        self.emulation_menu_hard_reset.set_property("enabled", True)
        self.emulation_menu_save_state.set_property("enabled", True)
        self.emulation_menu_save_state_as.set_property("enabled", True)
        self.emulation_menu_load_state.set_property("enabled", True)
        self.emulation_menu_load_state_from.set_property("enabled", True)
        self.emulation_menu_current_slot.set_property("enabled", True)
        self.options_menu_configure.set_property("enabled", False)
        self.options_menu_gfx_configure.set_property("enabled", False)
        self.options_menu_audio_configure.set_property("enabled", False)
        self.options_menu_input_configure.set_property("enabled", False)
        self.options_menu_rsp_configure.set_property("enabled", False)
        self.options_menu_fullscreen.set_property("enabled", True)
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
        self.file_menu_loadrom.set_property("enabled", True)
        self.file_menu_refresh.set_property("enabled", True)
        # self.file_menu_recents.set_property("enabled", True)
        self.emulation_menu_play.set_property("enabled", False)
        self.emulation_menu_pause.set_property("enabled", False)
        self.emulation_menu_stop.set_property("enabled", False)
        self.emulation_menu_soft_reset.set_property("enabled", False)
        self.emulation_menu_hard_reset.set_property("enabled", False)
        self.emulation_menu_save_state.set_property("enabled", False)
        self.emulation_menu_save_state_as.set_property("enabled", False)
        self.emulation_menu_load_state.set_property("enabled", False)
        self.emulation_menu_load_state_from.set_property("enabled", False)
        self.emulation_menu_current_slot.set_property("enabled", False)
        self.options_menu_configure.set_property("enabled", True)
        self.options_menu_gfx_configure.set_property("enabled", True)
        self.options_menu_audio_configure.set_property("enabled", True)
        self.options_menu_input_configure.set_property("enabled", True)
        self.options_menu_rsp_configure.set_property("enabled", True)
        self.options_menu_fullscreen.set_property("enabled", False)
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
        self.emulation_menu_play.set_property("enabled", True)
        self.emulation_menu_pause.set_property("enabled", False)
        self.toolbar_play.set_sensitive(True)
        self.toolbar_pause.set_sensitive(False)
        self.toolbar_next.set_sensitive(True)

    def insert_toolbar_item(self, name, sensitive, action):
        item = Gtk.Button(icon_name=name)
        item.set_sensitive(sensitive)
        item.connect("clicked", action)

        return item

    def insert_toolbar_item_obj(self, name, sensitive, action, value=None):
        item = Gtk.Button(icon_name=name)
        item.set_sensitive(sensitive)
        item.connect("clicked", action, value)

        return item

    # def insert_menu_item(self, label, sensitive, action=None, option=None, submenu=None):
    #     item = Gtk.MenuItem(label=label)
    #     item.set_sensitive(sensitive)
    #     if action != None:
    #         item.connect("activate", action, option)
        #if append_item != None:
        #    item.append(append_item)
    #     if submenu != None:
    #         item.set_submenu(submenu)

    #     return item

    # def insert_menu_item_obj(self, label, sensitive, obj, value1=None, value2=None, value3=None):
    #     item = Gtk.MenuItem(label=label)
    #     item.set_sensitive(sensitive)
    #     if value1 != None and value2 == None and value3 == None:
    #         item.connect_object("activate", obj, value1)
    #     elif value1 != None and value2 != None and value3 == None:
    #         item.connect_object("activate", obj, value1, value2)
    #     elif value1 != None and value2 != None and value3 != None:
    #         item.connect_object("activate", obj, value1, value2, value3)
    #     return item

    def on_recent_activated(self, widget):
        # TODO: currently unused
        #item = recentchoosermenu.get_current_item()
        #if item:
        #    name = item.get_display_name()
        #    uri = item.get_uri()
        #   log.debug(f"Recent item selected: {name}, {uri}")
            
        rom_uri = widget.get_current_uri()
        raw_path = GLib.filename_from_uri(rom_uri)
        self.frontend.rom = raw_path[0]

        self.frontend.action.thread_rom()

    def insert_action(self, widget, action_id, sensitive, callback, target=None, option1=None, option2=None):
        if widget == "radio":
            action = Gio.SimpleAction.new_stateful(action_id, \
                               GLib.VariantType.new("s"), \
                               GLib.Variant("s", target))
            action.connect("activate", callback)
        elif widget == "checkbox":
            action = Gio.SimpleAction.new_stateful(action_id, None, \
                                     GLib.Variant.new_boolean(bool(option1)))
            action.connect("change-state", callback)
        else:
            action = Gio.SimpleAction.new(action_id, None)
            if option2 != None:
                action.connect_object("activate", callback, option1, option2)
            else:
                if option1 != None:
                    action.connect_object("activate", callback, option1)
                else:
                    action.connect("activate", callback)

        action.set_property("enabled", sensitive)

        if action_id in ["open", "quit"]:
            self.frontend.application.add_action(action)
        else:
            self.frontend.add_action(action)

        return action

    def on_filter_toggle(self, action, state):
        action.set_state(GLib.Variant.new_boolean(state))
        if state:
            self.frontend.filter_box.show()
            self.frontend.frontend_conf.set("Frontend", "FilterConfig", "True")
        else:
            self.frontend.filter_box.hide()
            self.frontend.frontend_conf.set("Frontend", "FilterConfig", "False")

    def on_statusbar_toggle(self, action, state):
        action.set_state(GLib.Variant.new_boolean(state))
        if state:
            self.frontend.statusbar.show()
            self.frontend.frontend_conf.set("Frontend", "StatusConfig", "True")
        else:
            self.frontend.statusbar.hide()
            self.frontend.frontend_conf.set("Frontend", "StatusConfig", "False")

    def on_toolbar_toggle(self, action, state):
        action.set_state(GLib.Variant.new_boolean(state))
        if state:
            self.frontend.toolbar.show()
            self.frontend.frontend_conf.set("Frontend", "ToolbarConfig", "True")
        else:
            self.frontend.toolbar.hide()
            self.frontend.frontend_conf.set("Frontend", "ToolbarConfig", "False")
