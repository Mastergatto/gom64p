#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, Gdk, GLib
import ctypes as c
import logging as log
import pathlib

import utils.cache as u_cache
import utils.config as u_conf
#import utils.logging as u_log
import utils.environment as u_env
import widget.actions as w_act
import widget.canvas as w_cvs
import widget.menu as w_m
import widget.rombrowser as w_brw
import widget.keysym as w_key
import wrapper.datatypes as wrp_dt
import wrapper.functions as wrp
import wrapper.vidext as wrp_vext

###############
## VARIABLES ##
###############

#############
## CLASSES ##
#############

class GoodOldM64pWindow(Gtk.ApplicationWindow):
    def __repr__(self):
        return '<gom64p_window>'

    def __init__(self, app):
        super().__init__(application=app)
        self.window = self

        ### Frontend
        self.application = app
        self.emulating = False # This tells whether it's emulating a game or not
        self.running = False   # And this tell whether the game is running or it is paused
        self.lock = True
        self.canvas = None
        self.parameters = {}
        self.args = self.application.args
        self.cache = None
        self.m64p_dir = None
        self.rom = None

        self.isfullscreen = False
        self.changedfocus = True
        self.changedsize = False
        self.width = None
        self.height = None
        self.pos_x = None
        self.pos_y = None

        args_debug = self.application.args.debug
        args_csd = self.application.args.enable_csd

        # environment
        self.environment = u_env.Environment(self.window)
        self.environment.set_directories()
        self.environment.set_wm()
        self.m64p_dir = self.environment.get_current_path()
        self.platform = self.environment.query()
        self.parameters['platform'] = self.platform

        self.frontend_conf = u_conf.FrontendConf(self.environment.frontend_config_dir)
        self.application.frontend_conf = self.frontend_conf

        self.environment.set(self.window)

        self.m64p_wrapper = wrp.API(self.window, self.parameters)
        self.lock = self.m64p_wrapper.lock

        self.cheats = u_conf.CheatsCfg(self.window)
        self.action = w_act.Actions(self.window)

        if args_debug == True:
            self.application.logger.set_level(log.DEBUG)
            log.debug("Debug is enabled!")
            log.debug(f"GTK+ version: {Gtk.MAJOR_VERSION}.{Gtk.MINOR_VERSION}.{Gtk.MICRO_VERSION}")
        #else:
        #    logger = u_log.Logger(log.INFO)
        #self.set_application_name("mupen64plus")
        self.set_title("Good Old Mupen64+")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(800, 640)
        self.set_size_request(640, 560) # TODO: What's the good looking minimum size for the main window?
        self.set_default_icon_from_file(str(pathlib.Path(self.m64p_dir + "/icons/mupen64plus.svg")))

        ##If detected, it will close the application ##
        self.window.connect("delete-event", self.quit_cb)

        # If the window lose the focus, stops the emulation and calls a dialog
        self.window.connect("focus-in-event", self.focus_cb)
        self.window.connect("focus-out-event", self.focus_cb)

        # It detectes changes to resizes of window.
        self.window.connect("configure-event", self.resize_cb)

        # It tracks fullscreen/windowed state.
        self.window.connect("window-state-event", self.resize_cb)

        # NOTE: This callback code has to be declared before launching the wrapper
        STATEPROTO = c.CFUNCTYPE(None, c.POINTER(c.c_void_p), c.c_int, c.c_int)
        self.CB_STATE = STATEPROTO(self.state_callback)

        try:
            self.m64p_wrapper.preload()

        except:
            log.error('mupen64plus library not found')
            self.lock = True

        if self.m64p_wrapper.compatible == True:
            #self.lock?
            self.m64p_wrapper.initialise()

            self.cache = u_cache.CacheData(self.environment.cache_dir)

        # LAYOUT main window: csd,menubar,toolbar,box filter(label,entry),box((treeview,scroll),videoext),statusbar

        self.main_box = Gtk.VBox()
        self.browser_box = Gtk.VBox()
        self.video_box = Gtk.VBox()
        self.filter_box = Gtk.HBox()

        if args_csd == 1:
            self.csd()
            log.debug("CSD enabled")

        ## Statusbar ##
        self.statusbar = Gtk.Statusbar()
        self.statusbar_context = self.statusbar.get_context_id("m64p_status")
        self.action.status_push("Welcome to Good Old M64+!")

        self.main_menu = w_m.Menu(self)

        ## Menubar ##
        self.menubar = self.main_menu.menubar_call()
        self.file_menu_quit = self.main_menu.file_menu_quit
        self.file_menu_quit.connect("activate", self.quit_cb)
        self.file_menu_reload = self.main_menu.file_menu_reload
        self.file_menu_reload.connect('activate', self.on_reload)
        self.view_menu_filter = self.main_menu.view_menu_filter
        self.view_menu_filter.connect("toggled", self.action.on_filter_toggle)
        self.view_menu_status = self.main_menu.view_menu_status
        self.view_menu_status.connect("toggled", self.action.on_statusbar_toggle)

        ## Toolbar ##
        self.toolbar = self.main_menu.toolbar_call()

        # Notebook #
        self.notebook = Gtk.Notebook()
        self.notebook.set_vexpand(True)
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.notebook.set_margin_start(1)
        self.notebook.set_margin_end(1)

        browser_tab = Gtk.Label(label="browser")

        ## Filter entry ##
        if self.lock == False and self.m64p_wrapper.compatible == True:
            self.filter_label = Gtk.Label(label="Filter:")
            self.filter_entry = Gtk.SearchEntry()
            self.filter_entry.set_placeholder_text("Type to filter...")
            self.filter_entry.connect('changed', self.on_text_change)
            self.filter_box.pack_start(self.filter_label, False, True, 5)
            self.filter_box.pack_start(self.filter_entry, True, True, 5)
            self.browser_box.pack_start(self.filter_box, False, False, 5)

            self.browser_list = w_brw.List(self.window)
            treeview = self.browser_list.treeview_call()

            self.browser_box.add(treeview)
        else:
            if self.lock == True:
                if self.platform == "Windows":
                    warning = Gtk.Label(label="Mupen64Plus's core library hasn't been found. \n Please check it in Options > Configure \n You may also need to check the path for the plugins' directory.")
                else:
                    warning = Gtk.Label(label="Mupen64Plus's core library hasn't been found. \n Please check it in Options > Configure")
                self.browser_box.add(warning)
                self.browser_box.show_all()

            else:
                if self.platform == "Windows":
                    warning = Gtk.Label(label="Mupen64Plus's core library version is incompatible. Please upgrade it. \n You may also need to check the path for the plugins' directory.")
                else:
                    warning = Gtk.Label(label="Mupen64Plus's core library version is incompatible. Please upgrade it.")
                self.browser_box.add(warning)
                self.browser_box.show_all()

        self.notebook.append_page(self.browser_box, browser_tab)

        ## Alright, let's add the box ##
        self.main_box.pack_start(self.menubar, False, False, 0)
        self.main_box.pack_start(self.toolbar, False, False, 0)
        self.main_box.pack_start(self.notebook, True, True, 0)
        self.main_box.pack_end(self.statusbar, False, False, 0)

        self.window.add(self.main_box)

        ## Configurations InsertMenu

        if self.frontend_conf.get_bool("Frontend", "ToolbarConfig") == True:
            self.main_menu.view_menu_toolbar.set_active(True)
        if self.frontend_conf.get_bool("Frontend", "FilterConfig") == True:
            self.main_menu.view_menu_filter.set_active(True)
        if self.frontend_conf.get_bool("Frontend", "StatusConfig") == True:
            self.main_menu.view_menu_status.set_active(True)

        ##Now load the instance with all the widgets and boxes ##

        self.main_box.show()
        self.menubar.show_all()

        self.notebook.show_all()
        self.window.show()

        # Now that the window is shown, let's get its size.
        self.height = self.get_allocated_height()
        self.width = self.get_allocated_width()
        self.environment.get_current_mode()

    def csd(self):
        # HeaderBar (Client Side Decoration, only for GNOME)
        self.headerbar = Gtk.HeaderBar(title="mupen64plus CSD",has_subtitle="False")
        self.headerbar.set_show_close_button(True)
        #self.headerbar.set_subtitle("LOL")
        self.window.set_titlebar(self.headerbar)

        #TODO: Some example here. Replace it with real code.
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="mail-send-receive-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)

        self.headerbar.pack_end(button)
        self.headerbar.show_all()

    def add_video_tab(self):
        ## VideoBox ##
        vidext_tab = Gtk.Label(label="vidext")
        n_pages = self.notebook.get_n_pages()
        if n_pages == 1:
            #self.frontend_conf.open_section("Frontend")
            if self.frontend_conf.get_bool("Frontend", "Vidext") == True:
                self.canvas = w_cvs.Canvas(self.window)
                wrp_vext.m64p_video.set_window(self.window)
                self.video_box.add(self.canvas)
            else:
                self.emulating_label = Gtk.Label(label="Emulator is running.")
                self.video_box.add(self.emulating_label)

            self.notebook.append_page(self.video_box, vidext_tab)
            self.notebook.show_all()
        self.notebook.set_current_page(1)

    def remove_video_tab(self):
        self.notebook.remove_page(1)
        self.notebook.set_current_page(0)
        #self.frontend_conf.open_section("Frontend")
        if self.frontend_conf.get_bool("Frontend", "Vidext") == True:
            self.video_box.remove(self.canvas)
        else:
            self.video_box.remove(self.emulating_label)

    ### SIGNALS (clicked for button, activate for menu)

    def quit_cb(self, *args):
        if self.emulating == True:
            #TODO: There should be a dialog asking if the user wants to stop emulation first
            self.action.on_stop()
            return True
        else:
            self.application.quit()

    def focus_cb(self, widget, event):
        #Let's insert here like a milion of those checks, to make REALLY sure it doesn't trigger accidentally the call to the core
        if self.window.changedfocus == True:
            self.window.changedfocus = False
            if self.window.changedsize == True:
                height = self.get_allocated_height()
                width = self.get_allocated_width()
                if (self.window.width != width) or (self.window.height != height):
                    log.debug(f"The window has changed! Now it's height:{height} and width:{width}")
                    self.window.width = width
                    self.window.height = height
                    self.window.changedsize = False
                    if self.emulating == True:
                        self.window.canvas.register_size()
                        self.window.canvas.resize()
        else:
            self.window.changedfocus = True
        if self.emulating == True and self.running == True:
            if self.frontend_conf.get_bool("Frontend", "Vidext") == True:
                self.action.on_pause()
                log.debug("The window has lost the focus! Stopping the emulation.")

    def resize_cb(self, widget, event):
        #It detects window's size, position and stacking order changes
        if event.get_event_type() == Gdk.EventType.CONFIGURE:
            if self.window.changedfocus == True:
                self.window.changedsize = True

    def on_text_change(self, entry):
        self.browser_list.game_search_current = entry.get_text()
        self.browser_list.game_search_filter.refilter()

    def on_reload(self, widget):
        self.action.status_push("Refreshing the list...")
        self.browser_list.cache.generate()
        self.action.status_push("Refreshing the list...DONE")

    def state_callback(self, context, param, value):
        context_dec = c.cast(context, c.c_char_p).value.decode("utf-8")
        if param == wrp_dt.m64p_core_param.M64CORE_EMU_STATE.value:
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}: {wrp_dt.m64p_emu_state(value).name}")
            if wrp_dt.m64p_emu_state(value).name == 'M64EMU_STOPPED':
                self.running = False
                self.emulating = False
                if self.window.isfullscreen == True:
                    self.window.action.on_fullscreen(self, False)
                self.main_menu.sensitive_menu_stop()
                self.action.status_push( "*** Emulation STOPPED ***")
            elif wrp_dt.m64p_emu_state(value).name == 'M64EMU_RUNNING':
                self.main_menu.sensitive_menu_run()
                self.running = True
                self.emulating = True
                self.action.status_push( "*** Emulation STARTED ***")
                if self.frontend_conf.get_bool("Frontend", "Vidext") == True:
                    if (self.window.canvas.width != wrp_vext.m64p_video.width) or (self.window.canvas.height != wrp_vext.m64p_video.height):
                        self.window.canvas.register_size()
                        self.window.canvas.resize()
            elif wrp_dt.m64p_emu_state(value).name == 'M64EMU_PAUSED':
                self.main_menu.sensitive_menu_pause()
                self.running = False
                self.action.status_push( "*** Emulation PAUSED ***")

        elif param == wrp_dt.m64p_core_param.M64CORE_VIDEO_MODE.value:
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}: {wrp_dt.m64p_video_mode(value).name}")
        elif param == wrp_dt.m64p_core_param.M64CORE_SAVESTATE_SLOT.value:
            if self.m64p_wrapper.current_slot != value:
                self.m64p_wrapper.current_slot = value
                self.main_menu.save_slot_items[value].set_active(True)
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}, SLOT: {value}")
            self.action.status_push( "Slot selected: " + str(value))
        elif param == wrp_dt.m64p_core_param.M64CORE_SPEED_FACTOR.value:
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}: {value}%")
            self.action.status_push( "Emulation speed: " + str(value) + "%")
        elif param == wrp_dt.m64p_core_param.M64CORE_SPEED_LIMITER.value:
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}, {value}")
            self.action.status_push( "Speed limit: " + str(value))
        elif param == wrp_dt.m64p_core_param.M64CORE_VIDEO_SIZE.value:
            #TODO:Not yet mapped, (ScreenWidth << 16) + ScreenHeight
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param)}, {str(value).encode('utf-8')}")
        elif param == wrp_dt.m64p_core_param.M64CORE_AUDIO_VOLUME.value:
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}: {value}%")
            self.action.status_push( "Audio volume: " + str(value) + "%")
        elif param == wrp_dt.m64p_core_param.M64CORE_AUDIO_MUTE.value:
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}: {value}")
            if value == 1:
                self.action.status_push( "Audio has been muted!")
            else:
                self.action.status_push( "Audio has been unmuted.")
        elif param == wrp_dt.m64p_core_param.M64CORE_INPUT_GAMESHARK.value:
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}: {value}")
            if value == 1:
                self.action.status_push( "Gameshark button has been pressed!")
        elif param == wrp_dt.m64p_core_param.M64CORE_STATE_LOADCOMPLETE.value:
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}: {value}")
            if value == 1:
                self.action.status_push( "Save state is loaded successfully.")
            else:
                self.action.status_push( "WARNING: Save state has failed to load!")
        elif param == wrp_dt.m64p_core_param.M64CORE_STATE_SAVECOMPLETE.value:
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}: {value}")
            if value == 1:
                self.action.status_push( "Save state is done successfully.")
            else:
                self.action.status_push( "WARNING: Unable to create a save state!")
        else:
            # Unmapped params go here.
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}: {value}")
