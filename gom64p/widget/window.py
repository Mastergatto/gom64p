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
import widget.dialog as w_dlg
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
    #def __repr__(self):
    #    return '<gom64p_window>'

    def __init__(self, app):
        super().__init__(application=app)
        self.window = self
        w_dlg.parent = self

        ### Frontend
        self.application = app
        self.args = self.application.args
        #args_debug = self.application.args.debug
        #args_csd = self.application.args.enable_csd

        if self.application.args.debug:
            self.application.logger.set_level(log.DEBUG)
            log.debug("Debug is enabled!")

        self.lock = True
        self.canvas = None
        self.parameters = {}
        self.cache = None
        self.m64p_dir = None
        self.rom = None

        self.isfullscreen = False
        self.width = None
        self.height = None
        self.pos_x = None
        self.pos_y = None

        # Environment
        self.environment = u_env.Environment(self.window)
        self.environment.query()
        self.environment.set_directories()
        self.m64p_dir = self.environment.get_current_path()
        self.platform = self.environment.platform["system"]
        self.parameters['platform'] = self.platform

        # Options
        self.frontend_conf = u_conf.FrontendConf(self.environment.frontend_config_dir)
        self.application.frontend_conf = self.frontend_conf

        self.environment.set(self.window)


        # Create an instance of the wrapper
        self.m64p_wrapper = wrp.API(self.window, self.parameters)
        self.m64p_wrapper.vidext_override = self.frontend_conf.get_bool("Frontend", "Vidext")
        self.m64p_wrapper.pif_loading = self.frontend_conf.get_bool("Frontend", "PifLoad")
        self.lock = self.m64p_wrapper.lock

        self.cheats = u_conf.CheatsCfg(self.window)
        self.action = w_act.Actions(self.window)

        #self.set_application_name("mupen64plus")
        self.set_title("Good Old Mupen64+")
        self.set_default_size(800, 640)
        self.set_size_request(640, 560) # TODO: What's the good looking minimum size for the main window?
        #self.set_default_icon_from_file(str(pathlib.Path(self.m64p_dir + "/icons/mupen64plus.svg")))

        ##If detected, it will close the application ##
        self.window.connect("close-request", self.quit_cb)

        # If the window lose the focus, stops the emulation and calls a dialog
        #self.window.connect("focus-in-event", self.focus_cb)
        #self.window.connect("focus-out-event", self.focus_cb)

        # LAYOUT main window: csd,menubar,toolbar,box filter(label,entry),box((treeview,scroll),videoext),statusbar

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.browser_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.video_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        if self.application.args.enable_csd == 1:
            self.csd()
            log.debug("CSD enabled")

        ## Statusbar ##
        self.statusbar = Gtk.Statusbar()
        self.statusbar_context = self.statusbar.get_context_id("m64p_status")
        self.action.status_push("Welcome to Good Old M64+!")

        self.main_menu = w_m.Menu(self)

        ## Menubar ##
        self.menubar = self.main_menu.menubar_init()

        ## Toolbar ##
        self.toolbar = self.main_menu.toolbar_init()

        # Notebook #
        self.notebook = Gtk.Notebook()
        self.notebook.set_vexpand(True)
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.notebook.set_margin_start(1)
        self.notebook.set_margin_end(1)

        browser_tab = Gtk.Label(label="browser")

        self.notebook.append_page(self.browser_box, browser_tab)

        ## Alright, let's add the box ##
        self.main_box.append(self.menubar)
        self.main_box.append(self.toolbar)
        self.main_box.append(self.notebook)
        self.main_box.append(self.statusbar)

        self.window.set_child(self.main_box)

        # Set whether the following are visible or not, by user config
        if self.frontend_conf.get("Frontend", "StatusConfig") == "False":
            self.statusbar.hide()

        if self.frontend_conf.get("Frontend", "FilterConfig") == "False":
            self.filter_box.hide()

        self.window.show()

        # Now that the window is shown, let's get its size.
        self.height = self.get_allocated_height()
        self.width = self.get_allocated_width()
        self.environment.get_current_mode()

        self.wrapper_init()

    def wrapper_init(self):
        # NOTE: This callback code has to be declared before launching the wrapper
        STATEPROTO = c.CFUNCTYPE(None, c.POINTER(c.c_void_p), c.c_int, c.c_int)
        self.CB_STATE = STATEPROTO(self.m64p_state_callback)

        try:
            self.m64p_wrapper.preload()

        except:
            log.error('mupen64plus library not found')
            self.lock = True

        if self.m64p_wrapper.compatible == True:
            #self.lock?
            self.m64p_wrapper.plugins_validate()
            self.m64p_wrapper.initialise()

            self.cache = u_cache.CacheData(self.environment.cache_dir)

        ## Filter entry ##
        # TODO: Move to rombrowser
        if self.lock == False and self.m64p_wrapper.compatible == True:
            self.filter_label = Gtk.Label(label="Filter:")
            self.filter_entry = Gtk.SearchEntry()
            self.filter_entry.set_property("placeholder_text", "Type to filter...")
            self.filter_entry.set_hexpand(True)
            self.filter_entry.connect('changed', self.on_text_change)
            self.filter_box.append(self.filter_label)
            self.filter_box.append(self.filter_entry)
            self.browser_box.append(self.filter_box)

            self.browser_list = w_brw.List(self.window)
            treeview = self.browser_list.treeview_call()

            self.browser_box.append(treeview)
        else:
            if self.lock == True:
                if self.platform == "Windows":
                    warning = Gtk.Label(label="Mupen64Plus's core library hasn't been found. \n Please check it in Options > Configure \n You may also need to check the path for the plugins' directory.")
                else:
                    warning = Gtk.Label(label="Mupen64Plus's core library hasn't been found. \n Please check it in Options > Configure")
                self.browser_box.append(warning)

            else:
                if self.platform == "Windows":
                    warning = Gtk.Label(label="Mupen64Plus's core library version is incompatible. Please upgrade it. \n You may also need to check the path for the plugins' directory.")
                else:
                    warning = Gtk.Label(label="Mupen64Plus's core library version is incompatible. Please upgrade it.")
                self.browser_box.append(warning)

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
        self.headerbar.show()

    def add_video_tab(self):
        ## VideoBox ##
        vidext_tab = Gtk.Label(label="vidext")
        n_pages = self.notebook.get_n_pages()
        if n_pages == 1:
            #self.frontend_conf.open_section("Frontend")
            if self.m64p_wrapper.vidext_override == True:
                self.canvas = w_cvs.Canvas(self.window)
                wrp_vext.m64p_video.set_window(self.window)
                self.video_box.append(self.canvas)
            else:
                self.emulating_label = Gtk.Label(label="Emulator is running.")
                self.video_box.append(self.emulating_label)

            self.notebook.append_page(self.video_box, vidext_tab)
            self.notebook.show()
        self.notebook.set_current_page(1)
        self.canvas.grab_focus()

    def remove_video_tab(self):
        self.notebook.remove_page(1)
        self.notebook.set_current_page(0)
        if self.m64p_wrapper.vidext_override == True:
            self.video_box.remove(self.canvas)
        else:
            self.video_box.remove(self.emulating_label)

    def trigger_popup(self, text, context=None):
        dialog = w_dlg.PopupDialog(self.window, text, context)
        return dialog.response

    def headsup(self, which_type, text, context=None):
        self.info_bar = Gtk.InfoBar()
        self.info_bar.set_show_close_button(True)
        self.main_box.prepend(self.info_bar)
        label = f"{which_type}: {text}"
        message_label = Gtk.Label(label=label)
        self.info_bar.add_child(message_label)
        self.info_bar.connect("response", self.on_info_close)
        #label.ellipsize_labels_recursively(content_area)

    ### SIGNALS (clicked for button, activate for menu)

    def quit_cb(self, *args):
        if self.m64p_wrapper.emulating == True:
            self.trigger_popup("A game is currently running. Do you want to stop it?", "running")
            # Don't close the window yet!
            return True
        else:
            self.application.quit()

    def focus_cb(self, widget, event):
        # Let's insert some checks, to make sure it doesn't trigger accidentally the pause action
        if self.m64p_wrapper.emulating == True:
            if self.m64p_wrapper.running == True:
                if self.m64p_wrapper.vidext_override == True:
                    self.action.on_pause()
                    log.debug("The window has lost the focus! Stopping the emulation.")
            else:
                height = self.get_allocated_height()
                width = self.get_allocated_width()
                if (self.window.width != width) or (self.window.height != height):
                    log.debug(f"The window has changed! Now it's height:{height} and width:{width}")
                    self.window.width = width
                    self.window.height = height
                    self.window.canvas.register_size()
                    self.window.canvas.resize()
                if self.m64p_wrapper.vidext_override == True:
                    self.action.on_resume()

    def on_info_close(self, widget, response_id):
        widget.hide()

    # TODO: move to rombrowser
    def on_text_change(self, entry):
        self.browser_list.game_search_current = entry.get_text()
        self.browser_list.game_search_filter.refilter()

    # TODO: move to rombrowser
    def on_refresh(self, widget, x):
        self.action.status_push("Refreshing the list...")
        self.browser_list.cache.generate()
        self.action.status_push("Refreshing the list...DONE")

    def m64p_state_callback(self, context, param, value):
        context_dec = c.cast(context, c.c_char_p).value.decode("utf-8")
        if param == wrp_dt.m64p_core_param.M64CORE_EMU_STATE.value:
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}: {wrp_dt.m64p_emu_state(value).name}")
            if wrp_dt.m64p_emu_state(value).name == 'M64EMU_STOPPED':
                if self.window.isfullscreen == True:
                    self.window.action.on_fullscreen(self, False)
                self.main_menu.sensitive_menu_stop()
                self.action.status_push( "*** Emulation STOPPED ***")
            elif wrp_dt.m64p_emu_state(value).name == 'M64EMU_RUNNING':
                if self.m64p_wrapper.emulating == False:
                    # Update window size when the canvas is being shown
                    self.height = self.get_allocated_height()
                    self.width = self.get_allocated_width()
                self.main_menu.sensitive_menu_run()
                self.action.status_push( "*** Emulation STARTED ***")
                if self.m64p_wrapper.vidext_override == True:
                    if (self.window.canvas.width != wrp_vext.m64p_video.width) or (self.window.canvas.height != wrp_vext.m64p_video.height):
                        self.window.canvas.register_size()
                        self.window.canvas.resize()
            elif wrp_dt.m64p_emu_state(value).name == 'M64EMU_PAUSED':
                self.main_menu.sensitive_menu_pause()
                self.action.status_push( "*** Emulation PAUSED ***")
        elif param == wrp_dt.m64p_core_param.M64CORE_VIDEO_MODE.value:
            log.info(f"({context_dec}) {wrp_dt.m64p_core_param(param).name}: {wrp_dt.m64p_video_mode(value).name}")
        elif param == wrp_dt.m64p_core_param.M64CORE_SAVESTATE_SLOT.value:
            if self.m64p_wrapper.current_slot != value:
                self.m64p_wrapper.current_slot = value
                #self.main_menu.save_slot_items[value].set_active(True) #FIXME
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
