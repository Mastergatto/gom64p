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
import ctypes as c

import global_module as g
import widget.dialog as w_dialog
import widget.plugin as w_plugin
import wrapper.datatypes as wrp_dt

#############
## CLASSES ##
#############


class MediaDialog(Gtk.Dialog):
    def __init__(self, parent):
        self.filename = None
        self.num_controller = None
        self.cb_data = None

        self.media_window = Gtk.Dialog()
        self.media_window.set_properties(self, title="Media Loader")
        self.media_window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.media_window.set_default_size(550, 550)
        self.media_window.set_transient_for(parent)

        self.apply_button = self.media_window.add_button("Apply",Gtk.ResponseType.APPLY)
        self.apply_button.set_sensitive(False)
        self.media_window.add_button("Cancel",Gtk.ResponseType.CANCEL)
        self.media_window.add_button("OK",Gtk.ResponseType.OK)

        tpak_frame = Gtk.Frame(label="Transfer Pak options", shadow_type=1)
        n64dd_frame = Gtk.Frame(label="64DD options", shadow_type=1)

        tpak_grid = Gtk.Grid()

        g.m64p_wrapper.ConfigOpenSection("Transferpak")

        player1_rom_label = Gtk.Label("GB game (1):")
        player1_rom = self.insert_entry("GB-rom-1", "Filename of the GB ROM to load into TP 1", "Filename of the GB ROM to load into transferpak 1")
        player1_rom_open = Gtk.Button.new_with_label("Open")
        player1_rom_open.connect("clicked", self.on_search_file_path, player1_rom, "rom")
        player1_rom_clear = Gtk.Button.new_with_label("Clear")
        player1_rom_clear.connect("clicked", self.on_clear_entry, player1_rom)
        player1_ram_label = Gtk.Label("GB save (1):")
        player1_ram = self.insert_entry("GB-ram-1", "Filename of the GB RAM to load into TP 1", "Filename of the GB RAM to load into transferpak 1")
        player1_ram_open = Gtk.Button.new_with_label("Open")
        player1_ram_open.connect("clicked", self.on_search_file_path, player1_ram, "ram")
        player1_ram_clear = Gtk.Button.new_with_label("Clear")
        player1_ram_clear.connect("clicked", self.on_clear_entry, player1_ram)

        player2_rom_label = Gtk.Label("GB game (2):")
        player2_rom = self.insert_entry("GB-rom-2", "Filename of the GB ROM to load into TP 2", "Filename of the GB ROM to load into transferpak 2")
        player2_rom_open = Gtk.Button.new_with_label("Open")
        player2_rom_open.connect("clicked", self.on_search_file_path, player2_rom, "rom")
        player2_rom_clear = Gtk.Button.new_with_label("Clear")
        player2_rom_clear.connect("clicked", self.on_clear_entry, player2_rom)
        player2_ram_label = Gtk.Label("GB save (2):")
        player2_ram = self.insert_entry("GB-ram-2", "Filename of the GB RAM to load into TP 2", "Filename of the GB RAM to load into transferpak 2")
        player2_ram_open = Gtk.Button.new_with_label("Open")
        player2_ram_open.connect("clicked", self.on_search_file_path, player2_ram, "ram")
        player2_ram_clear = Gtk.Button.new_with_label("Clear")
        player2_ram_clear.connect("clicked", self.on_clear_entry, player2_ram)

        player3_rom_label = Gtk.Label("GB game (3):")
        player3_rom = self.insert_entry("GB-rom-3", "Filename of the GB ROM to load into TP 3", "Filename of the GB ROM to load into transferpak 3")
        player3_rom_open = Gtk.Button.new_with_label("Open")
        player3_rom_open.connect("clicked", self.on_search_file_path, player3_rom, "rom")
        player3_rom_clear = Gtk.Button.new_with_label("Clear")
        player3_rom_clear.connect("clicked", self.on_clear_entry, player3_rom)
        player3_ram_label = Gtk.Label("GB save (3):")
        player3_ram = self.insert_entry("GB-ram-3", "Filename of the GB RAM to load into TP 3", "Filename of the GB RAM to load into transferpak 3")
        player3_ram_open = Gtk.Button.new_with_label("Open")
        player3_ram_open.connect("clicked", self.on_search_file_path, player3_ram, "ram")
        player3_ram_clear = Gtk.Button.new_with_label("Clear")
        player3_ram_clear.connect("clicked", self.on_clear_entry, player3_ram)

        player4_rom_label = Gtk.Label("GB game (4):")
        player4_rom = self.insert_entry("GB-rom-4", "Filename of the GB ROM to load into TP 4", "Filename of the GB ROM to load into transferpak 4")
        player4_rom_open = Gtk.Button.new_with_label("Open")
        player4_rom_open.connect("clicked", self.on_search_file_path, player4_rom, "rom")
        player4_rom_clear = Gtk.Button.new_with_label("Clear")
        player4_rom_clear.connect("clicked", self.on_clear_entry, player4_rom)
        player4_ram_label = Gtk.Label("GB save (4):")
        player4_ram = self.insert_entry("GB-ram-4", "Filename of the GB RAM to load into TP 4", "Filename of the GB RAM to load into transferpak 4")
        player4_ram_open = Gtk.Button.new_with_label("Open")
        player4_ram_open.connect("clicked", self.on_search_file_path, player4_ram, "ram")
        player4_ram_clear = Gtk.Button.new_with_label("Clear")
        player4_ram_clear.connect("clicked", self.on_clear_entry, player4_ram)


        tpak_grid.attach(player1_rom_label, 0, 1, 1, 1)
        tpak_grid.attach(player1_rom, 1, 1, 1, 1)
        tpak_grid.attach(player1_rom_open, 2, 1, 1, 1)
        tpak_grid.attach(player1_rom_clear, 3, 1, 1, 1)
        tpak_grid.attach(player1_ram_label, 0, 2, 1, 1)
        tpak_grid.attach(player1_ram, 1, 2, 1, 1)
        tpak_grid.attach(player1_ram_open, 2, 2, 1, 1)
        tpak_grid.attach(player1_ram_clear, 3, 2, 1, 1)
        #tpak_grid.attach(, 1, 3, 1, 1)
        #tpak_grid.attach(, 0, 4, 1, 1)
        tpak_grid.attach(player2_rom_label, 0, 5, 1, 1)
        tpak_grid.attach(player2_rom, 1, 5, 1, 1)
        tpak_grid.attach(player2_rom_open, 2, 5, 1, 1)
        tpak_grid.attach(player2_rom_clear, 3, 5, 1, 1)
        tpak_grid.attach(player2_ram_label, 0, 6, 1, 1)
        tpak_grid.attach(player2_ram, 1, 6, 1, 1)
        tpak_grid.attach(player2_ram_open, 2, 6, 1, 1)
        tpak_grid.attach(player2_ram_clear, 3, 6, 1, 1)
        #tpak_grid.attach(, 0, 7, 1, 1)
        #tpak_grid.attach(, 0, 8, 1, 1)
        tpak_grid.attach(player3_rom_label, 0, 9, 1, 1)
        tpak_grid.attach(player3_rom, 1, 9, 1, 1)
        tpak_grid.attach(player3_rom_open, 2, 9, 1, 1)
        tpak_grid.attach(player3_rom_clear, 3, 9, 1, 1)
        tpak_grid.attach(player3_ram_label, 0, 10, 1, 1)
        tpak_grid.attach(player3_ram, 1, 10, 1, 1)
        tpak_grid.attach(player3_ram_open, 2, 10, 1, 1)
        tpak_grid.attach(player3_ram_clear, 3, 10, 1, 1)
        #tpak_grid.attach(, 0, 11, 1, 1)
        #tpak_grid.attach(, 0, 12, 1, 1)
        tpak_grid.attach(player4_rom_label, 0, 13, 1, 1)
        tpak_grid.attach(player4_rom, 1, 13, 1, 1)
        tpak_grid.attach(player4_rom_open, 2, 13, 1, 1)
        tpak_grid.attach(player4_rom_clear, 3, 13, 1, 1)
        tpak_grid.attach(player4_ram_label, 0, 14, 1, 1)
        tpak_grid.attach(player4_ram, 1, 14, 1, 1)
        tpak_grid.attach(player4_ram_open, 2, 14, 1, 1)
        tpak_grid.attach(player4_ram_clear, 3, 14, 1, 1)

        tpak_frame.add(tpak_grid)

        n64dd_grid = Gtk.Grid()

        g.m64p_wrapper.ConfigOpenSection("64DD")

        ipl_rom_label = Gtk.Label("IPL ROM:")
        ipl_rom = self.insert_entry("IPL-ROM", "Filename of the IPL ROM, required for 64DD games to work", "Filename of the IPL ROM, required for 64DD games to work")
        ipl_rom_open = Gtk.Button.new_with_label("Open")
        ipl_rom_open.connect("clicked", self.on_search_64dd_path, ipl_rom, "ipl")
        ipl_rom_clear = Gtk.Button.new_with_label("Clear")
        ipl_rom_clear.connect("clicked", self.on_clear_entry, ipl_rom)
        disk_rom_label = Gtk.Label("Disk ROM:")
        disk_rom = self.insert_entry("Disk", "Filename .ndd of the disk game", "Filename .ndd of the disk game")
        disk_rom_open = Gtk.Button.new_with_label("Open")
        disk_rom_open.connect("clicked", self.on_search_64dd_path, disk_rom, "disk")
        disk_rom_clear = Gtk.Button.new_with_label("Clear")
        disk_rom_clear.connect("clicked", self.on_clear_entry, disk_rom)

        n64dd_grid.attach(ipl_rom_label, 0, 1, 1, 1)
        n64dd_grid.attach(ipl_rom, 1, 1, 1, 1)
        n64dd_grid.attach(ipl_rom_open, 2, 1, 1, 1)
        n64dd_grid.attach(ipl_rom_clear, 3, 1, 1, 1)
        n64dd_grid.attach(disk_rom_label, 0, 2, 1, 1)
        n64dd_grid.attach(disk_rom, 1, 2, 1, 1)
        n64dd_grid.attach(disk_rom_open, 2, 2, 1, 1)
        n64dd_grid.attach(disk_rom_clear, 3, 2, 1, 1)
        #n64dd_grid.attach(, 1, 3, 1, 1)
        #n64dd_grid.attach(, 0, 4, 1, 1)

        n64dd_frame.add(n64dd_grid)

        media_box = self.media_window.get_content_area()
        media_box.pack_start(tpak_frame, False, False, 0)
        media_box.pack_start(n64dd_frame, False, False, 0)

        self.media_window.show_all()

        response = Gtk.ResponseType.APPLY
        while response == Gtk.ResponseType.APPLY:
            response = self.media_window.run()
            if response == Gtk.ResponseType.OK:
                if g.m64p_wrapper.ConfigHasUnsavedChanges("Transferpak") == True:
                    g.m64p_wrapper.ConfigSaveSection("Transferpak")
                if g.m64p_wrapper.ConfigHasUnsavedChanges("64DD") == True:
                    g.m64p_wrapper.ConfigSaveSection("64DD")

                g.m64p_wrapper.set_media_loader()
                self.media_window.destroy()
            elif response == Gtk.ResponseType.APPLY:
                if self.is_changed == True:
                    pass

            else:
                if g.m64p_wrapper.ConfigHasUnsavedChanges("Transferpak") == True:
                    g.m64p_wrapper.ConfigRevertChanges("Transferpak")
                if g.m64p_wrapper.ConfigHasUnsavedChanges("64DD") == True:
                    g.m64p_wrapper.ConfigRevertChanges("64DD")
                self.media_window.destroy()

    def insert_entry(self, param, placeholder, help):
        entry = Gtk.Entry()
        entry.set_placeholder_text(placeholder)
        entry.set_hexpand(True)

        try:
            if g.m64p_wrapper.ConfigGetParameter(param) != None:
                entry.set_text(g.m64p_wrapper.ConfigGetParameter(param))
        except KeyError:
            print(param, "not found. Creating it.")
            g.m64p_wrapper.ConfigSetDefaultString(param, "", help)

        entry.connect("changed", self.on_entry_changed, param)
        return entry

    def on_entry_changed(self, widget, param):
        self.is_changed = True
        self.apply_button.set_sensitive(True)
        value = widget.get_text()
        g.m64p_wrapper.ConfigSetParameter(param, value)

    def on_clear_entry(self, widget, entry):
        entry.set_text("")
        self.filename = ""

    def on_search_file_path(self, widget, entry, mem):
        dialog = w_dialog.GBChooserDialog(self.media_window, mem)
        self.filename = dialog.path
        if self.filename != None:
            self.is_changed = True
            self.apply_button.set_sensitive(True)
            entry.set_text(self.filename)
        else:
            print('Dialog is canceled.')

    def on_search_64dd_path(self, widget, entry, mem):
        dialog = w_dialog.N64DDChooserDialog(self.media_window, mem)
        self.filename = dialog.path
        if self.filename != None:
            self.is_changed = True
            self.apply_button.set_sensitive(True)
            entry.set_text(self.filename)
        else:
            print('Dialog is canceled.')

class N64DD_Dialog(Gtk.Dialog):
    def __init__(self, parent):
        self.filename = None
        self.num_controller = None
        self.cb_data = None

        self.n64dd_window = Gtk.Dialog()
        self.n64dd_window.set_properties(self, title="64DD")
        self.n64dd_window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.n64dd_window.set_default_size(550, 550)
        self.n64dd_window.set_transient_for(parent)

        self.apply_button = self.n64dd_window.add_button("Apply",Gtk.ResponseType.APPLY)
        self.apply_button.set_sensitive(False)
        self.n64dd_window.add_button("Cancel",Gtk.ResponseType.CANCEL)
        self.n64dd_window.add_button("OK",Gtk.ResponseType.OK)

        n64dd_grid = Gtk.Grid()

        g.m64p_wrapper.ConfigOpenSection("64DD")

        ipl_rom_label = Gtk.Label("IPL ROM:")
        ipl_rom = self.insert_entry("IPL-ROM", "Filename of the IPL ROM, required for 64DD games to work", "Filename of the IPL ROM, required for 64DD games to work")
        ipl_rom_open = Gtk.Button.new_with_label("Open")
        ipl_rom_open.connect("clicked", self.on_search_64dd_path, ipl_rom, "rom")
        ipl_rom_clear = Gtk.Button.new_with_label("Clear")
        ipl_rom_clear.connect("clicked", self.on_clear_entry, ipl_rom)
        disk_rom_label = Gtk.Label("Disk ROM:")
        disk_rom = self.insert_entry("Disk", "Filename .ndd of the disk game", "Filename .ndd of the disk game")
        disk_rom_open = Gtk.Button.new_with_label("Open")
        disk_rom_open.connect("clicked", self.on_search_64dd_path, disk_rom, "ram")
        disk_rom_clear = Gtk.Button.new_with_label("Clear")
        disk_rom_clear.connect("clicked", self.on_clear_entry, disk_rom)


        
