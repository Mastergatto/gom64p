#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, Gdk, GObject, GLib, GdkPixbuf
import sys, os, os.path, threading, ast, hashlib, time, pathlib

import logging as log
import widget.gameprop as w_gprop

###############
## VARIABLES ##
###############

#############
## CLASSES ##
#############

class List:
    def __init__(self, parent):
        self.parent = parent
        self.recent_manager = Gtk.RecentManager.get_default()
        self.selected_game = None
        self.rom_list = None
        self.parsed_list = None

        self.cache = Cache(self.parent)
        self.rom_list = ast.literal_eval(self.parent.cache.generated_list)
        self.is_cache_validated = self.cache.validate()

        self.menu()

    def convert(self):
        size_flag = 24 * self.parent.get_scale_factor()
        size_rating = 76 * self.parent.get_scale_factor()
        new_list = []

        usa = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/united-states.svg")), size_flag, -1, True)
        japan = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/japan.svg")), size_flag, -1, True)
        jpn_usa = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/us-jp.svg")), size_flag, -1, True)
        europe = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/european-union.svg")), size_flag, -1, True)
        australia = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/australia.svg")), size_flag, -1, True)
        france = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/france.svg")), size_flag, -1, True)
        germany = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/germany.svg")), size_flag, -1, True)
        italy = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/italy.svg")), size_flag, -1, True)
        spain = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/spain.svg")), size_flag, -1, True)
        #brazil = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/brazil.svg")), size_flag, -1, True)
        #china = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/china.svg")), size_flag, -1, True)
        unknown = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/unknown.svg")), size_flag, -1, True)

        zero = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/rating0.svg")), size_rating, -1, True)
        one = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/rating1.svg")), size_rating, -1, True)
        two = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/rating2.svg")), size_rating, -1, True)
        three = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/rating3.svg")), size_rating, -1, True)
        four = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/rating4.svg")), size_rating, -1, True)
        five = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(pathlib.Path(self.parent.m64p_dir + "/ui/icons/rating5.svg")), size_rating, -1, True)

        for i in self.rom_list:
            flag = i[0]
            j = list(i)
            if flag == "U":
                j[0] = usa
            elif flag == "J":
                j[0] = japan
            elif flag == "JU":
                j[0] = jpn_usa
            elif flag == "E":
                j[0] = europe
            elif flag == "A":
                j[0] = australia
            elif flag == "F":
                j[0] = france
            elif flag == "G":
                j[0] = germany
            elif flag == "I":
                j[0] = italy
            elif flag == "S":
                j[0] = spain
            #elif flag == "B":
            #    j[0] = brazil
            #elif flag == "C":
            #    j[0] = china
            else:
                j[0] = unknown

            stars = i[2]
            if stars == 0:
                j[2] = zero
            elif stars == 1:
                j[2] = one
            elif stars == 2:
                j[2] = two
            elif stars == 3:
                j[2] = three
            elif stars == 4:
                j[2] = four
            elif stars == 5:
                j[2] = five

            i = tuple(j)
            new_list += [i]
        self.parsed_list = new_list

    def generate_liststore(self):
        if self.rom_list != None:
            self.romlist_store_model.clear()
            self.convert()
            for game in self.parsed_list:
                self.romlist_store_model.append(list(game))
        else:
            log.warning("Rombrowser:The list is empty!")

    def game_filter_func(self, model, iterator, data):
        #in the second brackets the value correspond to that of a column
        searchList = model[iterator][1]
        if self.game_search_current is "" or self.game_search_current == None:
            return True
        else:
            return self.game_search_current.lower() in searchList.lower()

    def treeview_call(self):
        ## ListStore model ##
        self.romlist_store_model = Gtk.ListStore(GdkPixbuf.Pixbuf, str, GdkPixbuf.Pixbuf, str, str)

        if self.is_cache_validated == False:
            log.warning("The cache is NOT validated! Checking the list...")
            if self.rom_list != []:
                log.info("Rom list is not empty! Updating...")
                self.cache.update()
            else:
                log.info("Rom list is empty! Generating....")
                self.cache.generate()
        else:
            log.info("The cache is validated!")

        self.generate_liststore()
        self.game_search_current = ""

        #-Creating the filter, feeding it with the liststore model
        self.game_search_filter = self.romlist_store_model.filter_new()
        self.game_search_filter.set_visible_func(self.game_filter_func)
        self.game_search_filter_sorted = Gtk.TreeModelSort(model=self.game_search_filter)

        #-creating the treeview, making it use the filter as a model, and adding the columns
        self.treeview = Gtk.TreeView.new_with_model(self.game_search_filter_sorted)
        self.treeview.set_activate_on_single_click(False)
        for i, column_title in enumerate(["Country", "Game", "Status", "Filename", "MD5 hash"]):
            if i == 0: # Country
                renderer_pixbuf = Gtk.CellRendererPixbuf()
                column = Gtk.TreeViewColumn("", renderer_pixbuf, pixbuf=i)
            elif i == 2: # Status
                renderer_pixbuf = Gtk.CellRendererPixbuf()
                column = Gtk.TreeViewColumn("Status", renderer_pixbuf, pixbuf=i)

            else:
                renderer_text = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer_text, text=i)
                column.set_sort_column_id(i)
                column.set_sort_indicator(True)
                column.set_resizable(True)
            column.set_reorderable(True)
            column.set_min_width(24)
            if i == 1: # "Game"
                self.romlist_store_model.set_sort_column_id(1,0)
                #column.set_sort_order(1)
            self.treeview.append_column(column)
        self.treeview.get_selection().connect('changed', self.on_row_select)
        self.treeview.connect('row-activated', self.on_row_activated)
        self.treeview.connect('button_press_event', self.mouse_click)

        self.treeview_win_scrollable = Gtk.ScrolledWindow()
        self.treeview_win_scrollable.add(self.treeview)
        self.treeview_win_scrollable.show_all()
        return self.treeview_win_scrollable

    def on_row_select(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            log.debug(f'You selected {model[treeiter][3]}')

    def on_row_activated(self, treeview, treepath, column):
        model = treeview.get_model()
        treeiter = model.get_iter(treepath)
        self.rom = model.get_value(treeiter, 3)
        rom_uri = GLib.filename_to_uri(self.rom, None)
        if self.recent_manager.has_item(rom_uri) == False:
            self.recent_manager.add_item(rom_uri)

        if self.rom != None and self.parent.m64p_wrapper.compatible == True:
            thread = threading.Thread(name="Emulation", target=self.rom_startup)
            try:
                thread.start()
                return thread
            except:
                log.error("The emulation thread has encountered an unexpected error")
                threading.main_thread()

    def on_playitem_activated(self, widget):
        self.rom = self.selected_game
        rom_uri = GLib.filename_to_uri(self.rom, None)
        if self.recent_manager.has_item(rom_uri) == False:
            self.recent_manager.add_item(rom_uri)

        if self.rom != None and self.parent.m64p_wrapper.compatible == True:
            thread = threading.Thread(name="Emulation", target=self.rom_startup)
            try:
                thread.start()
                return thread
            except:
                log.error("The emulation thread has encountered an unexpected error")
                threading.main_thread()

    def on_properties_activated(self, widget, tab):
        dialog = w_gprop.PropertiesDialog(self.parent, self.selected_game, tab)

    def menu(self):
        # Context menu
        self.treeview_menu = Gtk.Menu()

        play_item = Gtk.MenuItem("Play this game")
        play_item.connect("activate", self.on_playitem_activated)
        info_item = Gtk.MenuItem("Informations on this game")
        info_item.connect("activate", self.on_properties_activated, "info")
        cheats_item = Gtk.MenuItem("Cheats for this game")
        cheats_item.connect("activate", self.on_properties_activated, "cheats")
        custom_item = Gtk.MenuItem("Custom settings")
        custom_item.connect("activate", self.on_properties_activated, "custom")

        self.treeview_menu.append(play_item)
        self.treeview_menu.append(Gtk.SeparatorMenuItem())
        self.treeview_menu.append(info_item)
        self.treeview_menu.append(cheats_item)
        self.treeview_menu.append(custom_item)

    def mouse_click(self, tv, event):
        if event.button == 3:
            # right mouse button pressed popup the menu

            pthinfo = tv.get_path_at_pos(event.x, event.y)
            if pthinfo != None:
                path,col,cellx,celly = pthinfo
                tv.grab_focus()
                tv.set_cursor(path,col,0)

                selection = tv.get_selection()
                (model, treeiter) = selection.get_selected()
                log.debug(f"You selected {model[treeiter][3]}")
                self.selected_game = model[treeiter][3]

                self.treeview_menu.show_all()
                self.treeview_menu.popup_at_pointer(event)

    def rom_startup(self):
        GLib.idle_add(self.parent.add_video_tab)
        self.parent.running = True
        self.parent.frontend_conf.open_section("Frontend")
        #print("Rombrowser:", self.parent.frontend_conf.get_bool("Vidext"))
        if self.parent.frontend_conf.get_bool("Vidext") == True:
            self.parent.m64p_wrapper.vext_override = True
        else:
            self.parent.m64p_wrapper.vext_override = False
        self.parent.m64p_wrapper.run(self.rom)

        # Clean everything
        GLib.idle_add(self.parent.remove_video_tab)
        self.parent.running = False

    #UNUSED
    def header(self,crc1,crc2):
        command = self.parent.m64p_wrapper.CoreGetRomSettings(crc1,crc2)

class Cache:
    def __init__(self, parent):
        self.parent = parent
        self.progressbar = ProgressScanning(self.parent)
        self.thread = None

        # The list.
        self.rom_list = None
        # Number of roms in the list
        self.amount_roms = None

    def generate(self):
        ''' It calls the method scan in a thread '''
        self.thread = threading.Thread(name="scan", target=self.scan)
        try:
            self.thread.start()
            return self.thread
        except:
            log.error("Cache: The 'scan' thread has encountered an unexpected error.")
            threading.main_thread()

    def get_total_elements(self):
        '''Method that enlist and returns ROMs that are present in selected
         directories.'''
        path_items = self.parent.frontend_conf.config.items('GameDirs')
        self.total_paths, self.total64dd = [], []
        self.format_allowed = ('.n64', '.v64', '.z64')
        self.format64dd_allowed = ('.ndd')

        for key, path in path_items:
            if path != '' and os.path.isdir(path) == True:
                os.chdir(path)
                self.walk(path, self.parent.frontend_conf.get_bool("Recursive"))

        os.chdir(self.parent.m64p_dir)

        return self.total_paths

    def walk(self, path, recursion):
        directory = os.listdir(path)
        if len(directory) > 0:
            for item in directory:
                item_path = path + item
                if os.path.isdir(item_path):
                    if recursion == True:
                        self.walk(item_path + os.sep, recursion)
                else:
                    if os.path.isfile(item_path):
                        if item_path.lower().endswith(self.format_allowed):
                            self.total_paths += [(item_path)]
                        #elif item_path.lower().endswith(self.format64dd_allowed):
                        #    self.total64dd += [(item_path, str.upper(self.hashify(onerom[i])))]

    def scan_element(self, rom):
        '''Method that opens and reads a ROM, and finally returns valuable
         informations that are in it'''
        self.parent.m64p_wrapper.rom_open(rom)
        header = self.parent.m64p_wrapper.rom_get_header()
        settings = self.parent.m64p_wrapper.rom_get_settings()
        self.parent.m64p_wrapper.rom_close()

        element = [(header['country'], settings['goodname'], settings['status'], rom, settings['md5'])]
        return element

    def scan(self):
        '''Threaded method to scan those ROMs that are indicated.'''
        log.info(f'Start scanning the directories')
        self.rom_list = []
        GLib.idle_add(self.progressbar.start, "Generating the list...")
        total_paths = self.get_total_elements()
        self.amount_roms = len(total_paths)
        GLib.idle_add(self.progressbar.set_amount, self.amount_roms)

        for rom in total_paths:
            element = self.scan_element(rom)
            GLib.idle_add(self.progressbar.tick)
            self.rom_list += element

        GLib.idle_add(self.progressbar.end)
        self.write()
        log.info(f'Done scanning the directories')

        # Let's tell to the browser that the job is done here.
        self.parent.browser_list.rom_list = self.rom_list
        GLib.idle_add(self.parent.browser_list.generate_liststore)

    def compare_and_manage(self):
        '''Threaded method to compare the list stored in the cache with this new list,
        any ROM not present in both lists will be added or removed'''
        log.info(f'Starting to compare lists and eventually add or remove files')
        list_cache = []
        self.rom_list = self.parent.browser_list.rom_list
        for i in self.rom_list:
            list_cache += [(i[3])]

        total_paths = self.get_total_elements()
        self.amount_roms = len(total_paths)
        new_elements = list(set(sorted(total_paths)).difference(sorted(list_cache)))
        missing_elements = list(set(sorted(list_cache)).difference(sorted(total_paths)))
        changed_elements = len(new_elements) + len(missing_elements)

        log.info(f'Done comparing the lists')

        if changed_elements > 0:
            log.info(f'New elements! Updating the cache...')
            GLib.idle_add(self.progressbar.start, "Updating the list...")
            GLib.idle_add(self.progressbar.set_amount, changed_elements)

            if new_elements:
                for rom in new_elements:
                    element = self.scan_element(rom)
                    GLib.idle_add(self.progressbar.tick)
                    self.rom_list += element
            if missing_elements:
                #TODO: Should it still scan?
                for rom in missing_elements:
                    element = self.scan_element(rom)
                    GLib.idle_add(self.progressbar.tick)
                    self.rom_list.remove(element[0])

            GLib.idle_add(self.progressbar.end)
            self.write()

            # Let's tell to the browser that the job is done here.
            self.parent.browser_list.rom_list = self.rom_list
            GLib.idle_add(self.parent.browser_list.generate_liststore)
        else:
            log.info(f'No changes, there\'s no need to update the cache.')
            # There are no ROMs to be added or removed, but we pretend to update the list just to please the user.
            GLib.idle_add(self.progressbar.start, "Updating the list...")
            GLib.idle_add(self.progressbar.set_amount, 1)
            time.sleep(1)
            GLib.idle_add(self.progressbar.tick)
            GLib.idle_add(self.progressbar.end)


    def hashify(self, file):
        hasher = hashlib.md5()
        #r = readable, b = in binary format
        with open(file, 'rb') as afile:
            buffer = afile.read()
            hasher.update(buffer)
        return hasher.hexdigest()

    def update(self):
        ''' It calls the method compare_and_manage in a thread '''
        self.thread = threading.Thread(name="update", target=self.compare_and_manage)
        try:
            self.thread.start()
            return self.thread
        except:
            log.error("Cache: The 'update' thread has encountered an unexpected error")
            threading.main_thread()

    def validate(self):
        #TODO: what about creation or modified date of files? Discard the idea if it's too complex to implement
        list_rom = self.get_total_elements()

        #validation = {"version": False, "amount": False, "identical": False}
        validation = [False, False, False]
        cache_version = 1

        #TODO
        if cache_version == 1:
            validation[0] = True
            log.info(f'The version of the cache is validated.')

        self.amount_roms = len(list_rom)
        if self.amount_roms == int(self.parent.cache.total_roms):
            validation[1] = True
            log.info(f'The amount of games is validated.')
        else:
            log.warning(f'The amount of games is NOT validated.')

        self.rom_list = ast.literal_eval(self.parent.cache.generated_list)
        list_cache = []
        for i in self.rom_list:
            list_cache += [(i[3])]

        if sorted(list_rom) == sorted(list_cache):
            validation[2] = True
            log.info(f'The list in the cache is validated.')
        else:
            log.warning(f'The list in the cache is NOT validated.')

        if  validation.count(True) == len(validation):
            return True
        else:
            return False

    def write(self):
        self.parent.cache.generated_list = self.rom_list
        self.parent.cache.total_roms = str(self.amount_roms)
        log.info(f'Amount of games found: {self.amount_roms}')
        self.parent.cache.write_cache()

class ProgressScanning(Gtk.Dialog):
    def __init__(self, parent):
        self.parent = parent
        self.fraction = 0
        self.dialog = None
        self.progressbar = None

    def end(self):
        self.dialog.destroy()

    def message(self, text):
        if self.progressbar.get_show_text() == False:
            self.progressbar.set_show_text(True)
        self.progressbar.set_text(text)

    def start(self, text):
        self.dialog = Gtk.Dialog.new()
        self.dialog.set_transient_for(self.parent)
        content_area = self.dialog.get_content_area()

        self.progressbar = Gtk.ProgressBar()
        self.message(text)

        content_area.add(self.progressbar)

        self.dialog.show_all()
        self.dialog.run()

    def set_amount(self, amount):
        self.amount = amount
        if self.amount > 0:
            self.fraction = 1.0 / self.amount
        else:
            self.fraction = 1.0

    def tick(self):
        value = self.progressbar.get_fraction() + self.fraction
        if value > 1:
            value = 0

        self.progressbar.set_fraction(value)

