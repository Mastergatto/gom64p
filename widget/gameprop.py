#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk

import widget.cheats as w_cht

#############
## CLASSES ##
#############

class PropertiesDialog(Gtk.Dialog):
    def __init__(self, parent, path, tab):
        self.parent = parent
        self.game = path
        self.header = None
        self.settings = None
        self.scan_element(path)

        self.cheats = w_cht.Cheats(self.parent)

        self.former_values = None
        #self.former_update()
        self.is_changed = False
        self.page_check = [False, False, False, False]
        #self.map_controls = {}
        self.scale_factor = parent.get_scale_factor()

        #self.section_info = self.get_section(g.m64p_wrapper.gfx_filename)
        #self.section_settings = self.get_section(g.m64p_wrapper.audio_filename)
        #self.section_cheats = self.get_section(g.m64p_wrapper.input_filename)

        title = f"Configuration for {self.game}"
        self.game_window = Gtk.Dialog()
        self.game_window.set_properties(self, title=title)
        self.game_window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.game_window.set_transient_for(parent)

        #self.apply_button = self.game_window.add_button("Apply",Gtk.ResponseType.APPLY)
        #self.apply_button.set_sensitive(False)
        self.game_window.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.game_window.add_button("OK", Gtk.ResponseType.OK)

        if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:

            notebook = Gtk.Notebook()
            notebook.set_vexpand(True)
            #notebook.connect("switch-page", self.on_change_page)

            info_tab = self.info_handler()
            info_label = Gtk.Label(label="Informations")

            cheats_tab = self.cheats.page()
            cheats_label = Gtk.Label(label="Cheats")

            custom_tab = self.custom_settings()
            custom_label = Gtk.Label(label="Custom settings")

            notebook.append_page(info_tab, info_label)
            notebook.append_page(cheats_tab, cheats_label)
            notebook.append_page(custom_tab, custom_label)

            dialog_box = self.game_window.get_content_area()
            dialog_box.add(notebook)

        else:
            label = Gtk.Label("Mupen64plus' core library is incompatible, please upgrade it.")
            dialog_box = self.game_window.get_content_area()
            dialog_box.add(label)

        self.game_window.show_all()

        response = Gtk.ResponseType.APPLY
        while response == Gtk.ResponseType.APPLY:
            response = self.game_window.run()
            if response == Gtk.ResponseType.OK:
                self.parent.m64p_wrapper.ConfigSaveFile()
                self.game_window.destroy()
            elif response == Gtk.ResponseType.APPLY:
                pass
            else:
                self.game_window.destroy()

    def info_handler(self):
        # Tab ROM handler#
        info_box = Gtk.VBox()

        file_entry = self.insert_entry("File name:", self.game) #TODO: filter to just the last part
        path_entry = self.insert_entry("Path:", self.game)
        name_entry = self.insert_entry("Name:", self.settings["goodname"])
        md5_entry = self.insert_entry("MD5 checksum:", self.settings["md5"])
        save_entry = self.insert_entry("Save type:", self.settings["savetype"])
        status_entry = self.insert_entry("Status:", self.settings["status"])
        players_entry = self.insert_entry("Players:", self.settings["players"])
        rumble_entry = self.insert_entry("Rumble support:", self.settings["rumble"])

        country_entry = self.insert_entry("Country:", self.header["country"])
        crc_box = Gtk.HBox()
        crc1_entry = self.insert_entry("CRC1:", self.header["crc1"])
        crc2_entry = self.insert_entry("CRC2:", self.header["crc2"])

        internal_entry = self.insert_entry("Internal name:", self.header["internalname"], "internal")
        manufacturer_entry = self.insert_entry("Manufacturer:", self.header["manufacturer"])
        cartridge_entry = self.insert_entry("Cartridge:", self.header["cartridge"])
        release_entry = self.insert_entry("Release:", self.header["release"])
        clockrate_entry = self.insert_entry("Clock rate:", self.header["clockrate"])

        # TODO: Yet to be decoded
        lat_entry = self.insert_entry("lat:", self.header["lat"])
        pgs1_entry = self.insert_entry("pgs1:", self.header["pgs1"])
        pgs2_entry = self.insert_entry("pgs2:", self.header["pgs2"])
        pwd_entry = self.insert_entry("pwd:", self.header["pwd"])
        pc_entry = self.insert_entry("pc:", self.header["pc"])


        info_box.pack_start(name_entry, False, False, 0)
        info_box.pack_start(country_entry, False, False, 0)
        info_box.pack_start(file_entry, False, False, 0)
        info_box.pack_start(status_entry, False, False, 0)
        info_box.pack_start(path_entry, False, False, 0)
        info_box.pack_start(internal_entry, False, False, 0)
        info_box.pack_start(md5_entry, False, False, 0)

        crc_box.pack_start(crc1_entry, False, False, 0)
        crc_box.pack_start(crc2_entry, False, False, 0)
        info_box.pack_start(crc_box, False, False, 0)

        info_box.pack_start(save_entry, False, False, 0)
        info_box.pack_start(players_entry, False, False, 0)
        info_box.pack_start(rumble_entry, False, False, 0)
        info_box.pack_start(cartridge_entry, False, False, 0)
        info_box.pack_start(manufacturer_entry, False, False, 0)

        return info_box

    #def cheats_page(self):
    #    label = Gtk.Label("Not yet implemented, please come back later.")
    #    tab_area = Gtk.VBox()
    #    tab_area.add(label)

    #    return tab_area

    def custom_settings(self):
        label = Gtk.Label("Not yet implemented, please come back later.")
        tab_area = Gtk.VBox()
        tab_area.add(label)

        return tab_area

    def scan_element(self, rom):
        '''Method that opens and reads a ROM, and finally returns valuable
         informations that are in it'''
        self.parent.m64p_wrapper.rom_open(rom)
        self.header = self.parent.m64p_wrapper.rom_get_header()
        self.settings = self.parent.m64p_wrapper.rom_get_settings()
        self.parent.m64p_wrapper.rom_close()

    def insert_entry(self, text, field, case=None):
        box = Gtk.HBox()
        label = Gtk.Label(text)
        entry = Gtk.Entry()
        entry.set_hexpand(True)
        entry.set_editable(False)
        entry.set_property("can_focus", False)
        if case == "internal":
            entry.set_max_width_chars(20)
            entry.set_width_chars(20)
            entry.set_text(field)
        else:
            entry.set_text(str(field))

        box.pack_start(label, False, False, 0)
        box.pack_start(entry, False, False, 0)

        return box
