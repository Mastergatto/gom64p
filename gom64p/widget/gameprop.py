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

import widget.cheats as w_cht

#############
## CLASSES ##
#############

class PropertiesDialog(Gtk.Dialog):
    def __init__(self, parent, path, tab):
        self.parent = parent
        self.game = path
        info = parent.action.scan_element(path)
        self.header = info['header']
        self.settings = info['settings']

        self.cheats = w_cht.Cheats(self.parent)

        self.former_values = None
        #self.former_update()
        self.is_changed = False
        #self.map_controls = {}
        self.scale_factor = parent.get_scale_factor()

        title = f"Configuration for {self.game}"
        self.prop_window = Gtk.Dialog()
        self.prop_window.set_properties(self, title=title)
        #self.prop_window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.prop_window.set_transient_for(parent)
        self.prop_window.set_modal(True)

        #self.apply_button = self.prop_window.add_button("Apply",Gtk.ResponseType.APPLY)
        #self.apply_button.set_sensitive(False)
        self.prop_window.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.prop_window.add_button("OK", Gtk.ResponseType.OK)
        self.prop_window.connect("response", self.on_response)

        if self.parent.lock == False and self.parent.m64p_wrapper.compatible == True:

            notebook = Gtk.Notebook()
            notebook.set_vexpand(True)
            #notebook.connect("switch-page", self.on_change_page)

            info_tab = self.info_handler()
            info_label = Gtk.Label(label="Informations")

            cheats_tab = self.cheats.page(self.header["crc1"], self.header["crc2"], self.header["country"])
            cheats_label = Gtk.Label(label="Cheats")

            custom_tab = self.custom_settings()
            custom_label = Gtk.Label(label="Custom settings")

            notebook.append_page(info_tab, info_label)
            notebook.append_page(cheats_tab, cheats_label)
            notebook.append_page(custom_tab, custom_label)

            dialog_box = self.prop_window.get_content_area()
            dialog_box.append(notebook)

            self.prop_window.show()

            if tab == "info":
                notebook.set_current_page(0)
            elif tab == "cheats":
                notebook.set_current_page(1)
            elif tab == "custom":
                notebook.set_current_page(2)

        else:
            label = Gtk.Label("Mupen64plus' core library is incompatible, please upgrade it.")
            dialog_box = self.prop_window.get_content_area()
            dialog_box.add(label)
            self.prop_window.show()

    def info_handler(self):
        # Tab ROM handler#
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        file_entry = self.insert_entry("File name:", os.path.basename(self.game))
        path_entry = self.insert_entry("Path:", self.game)
        name_entry = self.insert_entry("Name:", self.settings["goodname"])
        md5_entry = self.insert_entry("MD5 checksum:", self.settings["md5"])
        save_entry = self.insert_entry("Save type:", self.settings["savetype"])
        status_entry = self.insert_entry("Status:", self.settings["status"])
        players_entry = self.insert_entry("Players:", self.settings["players"])
        rumble_entry = self.insert_entry("Rumble support:", self.settings["rumble"])
        tpak_entry = self.insert_entry("Transfer pak support:", self.settings["transferpak"])
        mempak_entry = self.insert_entry("Memory pak support:", self.settings["mempak"])
        biopak_entry = self.insert_entry("Biopak support:", self.settings["biopak"])

        country_entry = self.insert_entry("Country:", self.header["country"])
        crc_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        crc1_entry = self.insert_entry("CRC1:", self.header["crc1"])
        crc2_entry = self.insert_entry("CRC2:", self.header["crc2"])

        internal_entry = self.insert_entry("Internal name:", self.header["internalname"], "internal")
        manufacturer_entry = self.insert_entry("Media format:", self.header["manufacturer"])
        cartridge_entry = self.insert_entry("Cartridge:", self.header["cartridge"])
        release_entry = self.insert_entry("Release:", self.header["release"])
        clockrate_entry = self.insert_entry("Clock rate:", self.header["clockrate"])
        cic_entry = self.insert_entry("CIC Chip:", self.header["cic"])

        # TODO: Yet to be decoded
        lat_entry = self.insert_entry("lat:", self.header["lat"])
        pgs1_entry = self.insert_entry("pgs1:", self.header["pgs1"])
        pgs2_entry = self.insert_entry("pgs2:", self.header["pgs2"])
        pwd_entry = self.insert_entry("pwd:", self.header["pwd"])
        pc_entry = self.insert_entry("pc:", self.header["pc"])


        info_box.append(name_entry)
        info_box.append(country_entry)
        info_box.append(file_entry)
        info_box.append(status_entry)
        info_box.append(cartridge_entry)
        info_box.append(players_entry)
        info_box.append(manufacturer_entry)

        # Group all the info on the pak accessories
        pak_frame = Gtk.Frame(label="Accessories support")
        self.set_margin(pak_frame, 5, 5, 5, 5)
        pak_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        pak_box.append(rumble_entry)
        pak_box.append(tpak_entry)
        pak_box.append(mempak_entry)
        pak_box.append(biopak_entry)

        pak_frame.set_child(pak_box)
        info_box.append(pak_frame)

        # Group all the technical details
        tech_frame = Gtk.Frame(label="Technical details")
        self.set_margin(tech_frame, 5, 5, 5, 5)
        tech_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        tech_box.append(path_entry)
        tech_box.append(internal_entry)
        tech_box.append(md5_entry)

        crc_box.append(crc1_entry)
        crc_box.append(crc2_entry)
        tech_box.append(crc_box)

        tech_box.append(cic_entry)
        tech_box.append(save_entry)

        tech_frame.set_child(tech_box)
        info_box.append(tech_frame)

        return info_box

    def custom_settings(self):
        label = Gtk.Label(label="Not yet implemented, please come back later.")
        tab_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        tab_area.append(label)

        return tab_area

    def insert_entry(self, text, field, case=None):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label(label=text)
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

        box.append(label)
        box.append(entry)

        return box

    def set_margin(self, widget, left, right, top, bottom):
        widget.set_margin_start(left)
        widget.set_margin_end(right)
        widget.set_margin_top(top)
        widget.set_margin_bottom(bottom)

    def on_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            self.parent.cheats.write()
            self.prop_window.destroy()
        elif response_id == Gtk.ResponseType.APPLY:
            pass
        else:
            self.prop_window.destroy()
