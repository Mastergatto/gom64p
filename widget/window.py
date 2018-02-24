#!/usr/bin/python3
# coding=utf-8
# © 2017 Master
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk,Gdk,Gio
import ctypes as c

import global_module as g
import utils.cache as u_cache
import widget.menu as w_m
import widget.rombrowser as w_brw
import widget.tpak as w_tpak
#import widget.glwidget as w_gl
import wrapper.datatypes as wrp_dt

###############
## VARIABLES ##
###############

#############
## CLASSES ##
#############

class GoodOldM64pWindow(Gtk.ApplicationWindow):
    def __repr__(self):
        return '<gom64pwindow>'

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app)
        self.m64p_window = self

        ### Frontend
        self.application = app
        #self.running = 0

        args_debug = self.application.args.debug
        args_csd = self.application.args.enable_csd
        args_m64p_lib = self.application.args.lib
        args_m64p_config = self.application.args.configdir
        args_m64p_plugins = self.application.args.plugindir
        args_m64p_data = self.application.args.datadir

        #TODO: Something isn't right, check this better. Also need to write in the conf.
        if not args_m64p_lib:
            g.parameters['m64plib'] = args_m64p_lib
        if not args_m64p_config:
            g.parameters['configdir'] = args_m64p_config
        if not args_m64p_plugins:
            g.parameters['pluginsdir'] = args_m64p_plugins
        if not args_m64p_data:
            g.parameters['datadir'] = args_m64p_data

        #self.set_application_name("mupen64plus")
        self.set_position(1)
        self.set_default_size(800, 640)
        self.set_default_icon_from_file("ui/mupen64plus.svg")

        ##If detected, it will close the application ##
        #self.connect("delete-event", self.quit_cb)

        # NOTE: This callback code has to be declared before launching the wrapper
        STATEPROTO = c.CFUNCTYPE(None, c.POINTER(c.c_void_p), c.c_int, c.c_int)
        g.CB_STATE = STATEPROTO(self.state_callback)

        try:
            g.m64p_wrapper.preload()

        except:
            print('mupen64plus library not found')
            g.lock = True

        if g.m64p_wrapper.compatible == True:
            #self.lock?
            g.m64p_wrapper.initialise()

            g.cache = u_cache.Cache(g.m64p_wrapper.ConfigGetUserCachePath())


        # LAYOUT main window: csd,menubar,toolbar,box filter(label,entry),box((treeview,scroll),videoext),statusbar

        self.main_box = Gtk.VBox()
        self.switch_box = Gtk.VBox()
        self.browser_box = Gtk.VBox()
        self.video_box = Gtk.Box()
        self.filter_box = Gtk.HBox()

        self.browser_box.set_size_request(320,240)

        if args_debug == True:
            print("Debug mode: Enabled")
            DebugBox = Gtk.HBox()
            self.FakeEmulation = Gtk.ToggleButton(label="Fake emulation")
            self.FakeEmulation.connect("toggled", self.on_FakeEmulation_toggled)
            DebugBox.pack_start(self.FakeEmulation, False, False, 0)
            self.main_box.pack_start(DebugBox, False, False,0)
            DebugBox.show_all()

        if args_csd == 1:
            self.csd()
            print("CSD enabled")

        ## Statusbar ##
        self.Statusbar = Gtk.Statusbar()
        self.StatusbarContext = self.Statusbar.get_context_id("m64p_status")
        self.Statusbar.push(self.StatusbarContext,"Welcome to Good Old M64+!")

        self.main_menu = w_m.Menu(self)

        ## Menubar ##
        self.menubar = self.main_menu.menubar_call()
        self.file_menu_quit = self.main_menu.file_menu_quit
        self.file_menu_quit.connect("activate", self.quit_cb)
        self.file_menu_reload = self.main_menu.file_menu_reload
        self.file_menu_reload.connect('activate', self.on_reload)
        self.view_menu_filter = self.main_menu.view_menu_filter
        self.view_menu_filter.connect("toggled", self.on_EnableFilter_toggle)
        self.view_menu_status = self.main_menu.view_menu_status
        self.view_menu_status.connect("toggled", self.on_EnableStatusBar_toggle)

        ## Toolbar ##
        self.toolbar = self.main_menu.toolbar_call()

        ## Filter entry ##
        if g.lock == False:
            self.filter_label = Gtk.Label(label="Filter:")
            self.filter_entry = Gtk.SearchEntry()
            self.filter_entry.set_placeholder_text("Type to filter...")
            self.filter_entry.connect('changed', self.on_text_change)
            self.filter_box.pack_start(self.filter_label, False, True, 5)
            self.filter_box.pack_start(self.filter_entry, True, True, 5)
            self.browser_box.pack_start(self.filter_box, False, False, 5)

            self.browser_list = w_brw.List()
            treeview = self.browser_list.treeview_call()

            self.browser_box.add(treeview)
        else:
            #self.browser_list = None
            warning = Gtk.Label(label="Mupen64Plus's core library hasn't been found. \n Please check it in Options > Configure")
            self.browser_box.add(warning)
            self.browser_box.show_all()

        self.switch_box.add(self.browser_box)

        ## VideoBox ##
        #self.drawing_area = w_gl.drawing_area
        #self.video_box.set_size_request(640,480)

        #self.video_box.add(self.drawing_area)
        self.switch_box.add(self.video_box)

        ## Alright, let's add the box ##
        self.main_box.pack_start(self.menubar, False, False, 0)
        self.main_box.pack_start(self.toolbar, False, False, 0)
        self.main_box.pack_start(self.switch_box, True, True, 0)
        self.main_box.pack_end(self.Statusbar, False, False, 0)

        self.m64p_window.add(self.main_box)

        ## Configurations InsertMenu

        if g.frontend_conf.get_bool('ToolbarConfig') == True:
            self.main_menu.view_menu_toolbar.set_active(True)
        if g.frontend_conf.get_bool('FilterConfig') == True:
            self.main_menu.view_menu_filter.set_active(True)
        if g.frontend_conf.get_bool('StatusConfig') == True:
            self.main_menu.view_menu_status.set_active(True)

        ##Now load the instance with all the widgets and boxes ##

        self.main_box.show()
        self.menubar.show_all()
        #self.toolbar.hide()
        #self.filter_box.hide()

        self.browser_box.show()
        #self.video_box.hide()
        self.switch_box.show()
        #self.Statusbar.hide()
        self.m64p_window.show()

    def csd(self):
        # HeaderBar (Client Side Decoration, only for GNOME)
        self.headerbar = Gtk.HeaderBar(title="mupen64plus CSD",has_subtitle="False")
        self.headerbar.set_show_close_button(True)
        #self.headerbar.set_subtitle("LOL")
        self.m64p_window.set_titlebar(self.headerbar)

        #TODO: Some example here. Replace it with real code.
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="mail-send-receive-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)

        self.headerbar.pack_end(button)
        self.headerbar.show_all()


    ### SIGNALS (clicked for button, activate for menu)

    def quit_cb(self, *args):
        self.application.quit()

    def on_text_change(self, entry):
        self.browser_list.game_search_current = entry.get_text()
        self.browser_list.game_search_filter.refilter()

    def on_EnableFilter_toggle(self, *args):
        filter_checkbox = self.view_menu_filter
        n64list_filter = self.filter_box
        if filter_checkbox.get_active() == 1:
            n64list_filter.show_all()
            g.frontend_conf.set('FilterConfig', 'True')
        else:
            n64list_filter.hide()
            g.frontend_conf.set('FilterConfig', 'False')

    def on_EnableStatusBar_toggle(self, *args):
        statusbar_checkbox = self.view_menu_status
        m64p_statusbar = self.Statusbar
        if statusbar_checkbox.get_active() == 1:
            m64p_statusbar.show()
            g.frontend_conf.set('StatusConfig', 'True')
        else:
            m64p_statusbar.hide()
            g.frontend_conf.set('StatusConfig', 'False')


    def on_FakeEmulation_toggled(self, *args):
        if self.FakeEmulation.get_active() == 1:
            print("DEBUG: Fake emulation has now started!")
            self.browser_box.hide()
            self.video_box.show_all()
            #window_size = self.m64p_window.get_size()
            #print(window_size)
            self.m64p_window.resize(640,480)
            self.m64p_window.set_resizable(False)
            self.Statusbar.push(self.StatusbarContext,"Emulation STARTED")
        else:
            print("DEBUG: Fake emulation has stopped!")
            self.video_box.hide()
            self.browser_box.show()
            #print(window_size)
            #self.m64p_window.resize(window_size[0],window_size[1])
            self.m64p_window.set_resizable(True)
            self.Statusbar.push(self.StatusbarContext,"Emulation STOPPED")

    def on_reload(self, widget):
        self.Statusbar.push(self.StatusbarContext,"Refreshing the list...")
        self.browser_list.romlist_store_model.clear()
        self.browser_list.cache_update()
        self.browser_list.generate_liststore()
        self.Statusbar.push(self.StatusbarContext,"Refreshing the list...DONE")


    def state_callback(self, context, param, value):
        if param == wrp_dt.m64p_core_param.M64CORE_EMU_STATE.value:
            print(wrp_dt.m64p_core_param(param).name, wrp_dt.m64p_emu_state(value).name)
            if wrp_dt.m64p_emu_state(value).name == 'M64EMU_STOPPED':
                self.m64p_window.video_box.hide()
                self.m64p_window.browser_box.show()
                self.m64p_window.set_resizable(True)
                self.main_menu.sensitive_menu_stop()
                self.Statusbar.push(self.StatusbarContext, "Emulation STOPPED")
            elif wrp_dt.m64p_emu_state(value).name == 'M64EMU_RUNNING':
                self.m64p_window.browser_box.hide()
                self.m64p_window.video_box.show_all()
                self.m64p_window.resize(640,480)
                self.m64p_window.set_resizable(False)
                self.main_menu.sensitive_menu_run()
                self.Statusbar.push(self.StatusbarContext, "Emulation STARTED")
            elif wrp_dt.m64p_emu_state(value).name == 'M64EMU_PAUSED':
                self.main_menu.sensitive_menu_pause()
                self.Statusbar.push(self.StatusbarContext, "Emulation PAUSED")

        elif param == wrp_dt.m64p_core_param.M64CORE_VIDEO_MODE.value:
            print(context.contents, wrp_dt.m64p_core_param(param).name, wrp_dt.m64p_video_mode(value).name)
        elif param == wrp_dt.m64p_core_param.M64CORE_SAVESTATE_SLOT.value:
            if self.main_menu.active_slot != value:
                self.main_menu.active_slot = value
                self.main_menu.save_slot_items[value].set_active(True)
            print(context.contents, wrp_dt.m64p_core_param(param).name, "SLOT:", value)
            #self.Statusbar.push(self.StatusbarContext, "Slot selected: " + str(value))
        elif param == wrp_dt.m64p_core_param.M64CORE_SPEED_FACTOR.value:
            print(context.contents, wrp_dt.m64p_core_param(param).name, value, "%")
            self.Statusbar.push(self.StatusbarContext, "Emulation speed: " + str(value) + "%")
        elif param == wrp_dt.m64p_core_param.M64CORE_SPEED_LIMITER.value:
            print(context.contents, wrp_dt.m64p_core_param(param).name, value)
            self.Statusbar.push(self.StatusbarContext, "Speed limit: " + str(value))
        elif param == wrp_dt.m64p_core_param.M64CORE_VIDEO_SIZE.value: #TODO:Not implemented
            #print(context.contents, wrp_dt.m64p_core_param(param), str(value).encode("utf-8"))
            pass
        elif param == wrp_dt.m64p_core_param.M64CORE_AUDIO_VOLUME.value:
            print(context.contents, wrp_dt.m64p_core_param(param).name, value, "%")
            self.Statusbar.push(self.StatusbarContext, "Audio volume: " + str(value) + "%")
        elif param == wrp_dt.m64p_core_param.M64CORE_AUDIO_MUTE.value:
            print(context.contents, wrp_dt.m64p_core_param(param).name, value)
        elif param == wrp_dt.m64p_core_param.M64CORE_INPUT_GAMESHARK.value:
            print(context.contents, wrp_dt.m64p_core_param(param).name, value)
        elif param == wrp_dt.m64p_core_param.M64CORE_STATE_LOADCOMPLETE.value:
            print(context.contents, wrp_dt.m64p_core_param(param).name, value)
            if value == 1:
                self.Statusbar.push(self.StatusbarContext, "Save state is loaded successfully")
        elif param == wrp_dt.m64p_core_param.M64CORE_STATE_SAVECOMPLETE.value:
            print(context.contents, wrp_dt.m64p_core_param(param).name, value)
            if value == 1:
                self.Statusbar.push(self.StatusbarContext, "Save state is done successfully")
        else:
            # Unmapped params go here.
            print(context.contents, param, value)
