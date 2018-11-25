#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, Gdk, GObject
import sys, os, os.path, threading, ast, hashlib

import global_module as g

###############
## VARIABLES ##
###############

#############
## CLASSES ##
#############

class List:
    def __init__(self, parent):
        self.parent = parent
        self.selected_game = None
        self.rom_list = None
        self.cache_validated = False
        self.total_roms = None
        self.cache_validate()
        #print(self.cache_validated)
        if self.cache_validated == True:
            self.rom_list = ast.literal_eval(g.cache.generated_list)
        else:
            self.cache_generate()
        self.treeview_call()
        self.menu()

    def cache_generate(self):
        self.rom_list = self.scan()
        g.cache.generated_list = self.rom_list
        g.cache.total_roms = str(self.total_roms)
        g.cache.write_cache()

    def cache_validate(self):
        path_items = g.frontend_conf.config.items('GameDirs')
        self.total_roms = []
        #TODO: number of files and date?
        for key, path in path_items:
            if path != '' and os.path.isdir(path) == True:
                os.chdir(path)
                format_allowed = ('.n64', '.v64', '.z64')
                format64dd_allowed = ('.ndd')

                for onerom in os.listdir(path):
                    if os.path.isfile(onerom) and onerom.lower().endswith(format_allowed):
                        self.total_roms += [onerom]
        os.chdir(g.m64p_dir)

        self.total_roms = len(self.total_roms)
        #print(self.total_roms, int(g.cache.total_roms))
        if self.total_roms == int(g.cache.total_roms):
            self.cache_validated = True

    def cache_update(self):
        self.rom_list = self.scan()
        path_items = g.frontend_conf.config.items('GameDirs')
        self.total_roms = []
        #TODO: number of files and date?
        for key, path in path_items:
            if path != '' and os.path.isdir(path) == True:
                os.chdir(path)
                format_allowed = ('.n64', '.v64', '.z64')
                format64dd_allowed = ('.ndd')

                for onerom in os.listdir(path):
                    if os.path.isfile(onerom) and onerom.lower().endswith(format_allowed):
                        self.total_roms += [onerom]
        os.chdir(g.m64p_dir)

        self.total_roms = len(self.total_roms)
        #print(self.total_roms, int(g.cache.total_roms))

        g.cache.generated_list = self.rom_list
        g.cache.total_roms = str(self.total_roms)
        g.cache.write_cache()

    def scan(self):
        path_items = g.frontend_conf.config.items('GameDirs')
        totalfiles = []
        total64dd = []

        for key, path in path_items:
            if path != '' and os.path.isdir(path) == True:
                os.chdir(path)
                format_allowed = ('.n64', '.v64', '.z64')
                format64dd_allowed = ('.ndd')

                for onerom in os.listdir(path):
                    if os.path.isfile(onerom) and onerom.lower().endswith(format_allowed):
                        g.m64p_wrapper.rom_open(path + onerom)
                        header = g.m64p_wrapper.rom_get_header()
                        settings = g.m64p_wrapper.rom_get_settings()
                        g.m64p_wrapper.rom_close()

                        totalfiles += [(header['country'], settings['name'], settings['status'], path + onerom, settings['md5'])]
                    elif os.path.isfile(onerom) and onerom.lower().endswith(format64dd_allowed):
                        total64dd += [(path + onerom , str.upper(self.hashify(onerom)))]
        os.chdir(g.m64p_dir)
        return totalfiles

    def generate_liststore(self):
        for game in self.rom_list:
            self.romlist_store_model.append(list(game))

    def game_filter_func(self, model, iterator, data):
        #in the second brackets the value correspond to that of a column
        searchList = model[iterator][1]
        if self.game_search_current is "" or self.game_search_current == None:
            return True
        else:
            return self.game_search_current.lower() in searchList.lower()

    def treeview_call(self):
        ## ListStore model ##
        self.romlist_store_model = Gtk.ListStore(str, str, int, str, str)
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
            renderer_text = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer_text, text=i)
            column.set_min_width(20)
            column.set_sort_column_id(i)
            column.set_sort_indicator(True)
            column.set_reorderable(True)
            column.set_resizable(True)
            if i == 1:
                self.romlist_store_model.set_sort_column_id(1,0)
                #column.set_sort_order(1)
            self.treeview.append_column(column)
        #self.treeview.get_selection().connect('changed', self.on_row_select)
        self.treeview.connect('row-activated', self.on_row_activated)
        self.treeview.connect('button_press_event', self.mouse_click)

        self.treeview_win_scrollable = Gtk.ScrolledWindow()
        self.treeview_win_scrollable.add(self.treeview)
        self.treeview_win_scrollable.show_all()
        return self.treeview_win_scrollable

    def on_row_select(self, selection):
        #TODO: UNUSED, to be deleted in future
        model, treeiter = selection.get_selected()
        if treeiter != None:
            print("You selected", model[treeiter][0])

    def on_row_activated(self, treeview, treepath, column):
        model = treeview.get_model()
        treeiter = model.get_iter(treepath)
        self.rom = model.get_value(treeiter, 3)
        if self.rom != None and g.m64p_wrapper.compatible == True:
            thread = threading.Thread(name="Emulation",target=self.rom_startup)
            thread.daemon = True
            try:
                thread.start()
                return thread
            except:
                print("The emulation has encountered an unexpected error")
                threading.main_thread()

    def on_playitem_activated(self, widget):
        self.rom = self.selected_game
        if self.rom != None and g.m64p_wrapper.compatible == True:
            if g.m64p_wrapper.vext_override == False:
                thread = threading.Thread(name="Emulation", target=self.rom_startup)
                thread.daemon = True
                try:
                    thread.start()
                    return thread
                except:
                    print("The emulation has encountered an unexpected error")
                    threading.main_thread()
            else:
                self.rom_startup()

    def menu(self):
        # Context menu
        self.treeview_menu = Gtk.Menu()

        play_item = Gtk.MenuItem("Play this game")
        play_item.connect("activate", self.on_playitem_activated)
        self.treeview_menu.append(play_item)

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
                print("You selected", model[treeiter][3])
                self.selected_game = model[treeiter][3]

                self.treeview_menu.show_all()
                self.treeview_menu.popup_at_pointer(event)

    def rom_startup(self):
        GObject.idle_add(self.parent.add_video_tab)
        g.running = True
        if g.frontend_conf.get("vidext") == "True":
            g.m64p_wrapper.vext_override = True
        g.m64p_wrapper.run(self.rom)

    #UNUSED
    def hashify(self,file):
        hasher = hashlib.md5()
        #r = readable, b = in binary format
        with open(file, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def header(self,crc1,crc2):
        command = g.m64p_wrapper.CoreGetRomSettings(crc1,crc2)

