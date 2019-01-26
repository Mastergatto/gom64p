#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, Gdk
import ctypes as c

import global_module as g
import utils.cache as u_cache
import widget.menu as w_m
import widget.rombrowser as w_brw
import widget.keysym as w_key
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
        self.canvas = None

        args_debug = self.application.args.debug
        args_csd = self.application.args.enable_csd
        args_m64p_lib = self.application.args.lib
        args_m64p_config = self.application.args.configdir
        args_m64p_plugins = self.application.args.plugindir
        args_m64p_data = self.application.args.datadir

        #TODO: I feel something isn't right here, check this better later. Also need to write in the conf.
        if not args_m64p_lib:
            g.parameters['m64plib'] = args_m64p_lib
        if not args_m64p_config:
            g.parameters['configdir'] = args_m64p_config
        if not args_m64p_plugins:
            g.parameters['pluginsdir'] = args_m64p_plugins
        if not args_m64p_data:
            g.parameters['datadir'] = args_m64p_data

        #self.set_application_name("mupen64plus")
        self.set_title("Good Old Mupen64+")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(800, 640)
        self.set_size_request(640, 560) # TODO: What's the good looking minimum size for the main window?
        self.set_default_icon_from_file("ui/mupen64plus.svg")

        ##If detected, it will close the application ##
        self.connect("delete-event", self.quit_cb)

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
        self.browser_box = Gtk.VBox()
        self.video_box = Gtk.VBox()
        self.filter_box = Gtk.HBox()

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

        # Notebook #
        self.notebook = Gtk.Notebook()
        self.notebook.set_vexpand(True)
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.notebook.set_margin_start(1)
        self.notebook.set_margin_end(1)

        browser_tab = Gtk.Label(label="browser")

        ## Filter entry ##
        if g.lock == False and g.m64p_wrapper.compatible == True:
            self.filter_label = Gtk.Label(label="Filter:")
            self.filter_entry = Gtk.SearchEntry()
            self.filter_entry.set_placeholder_text("Type to filter...")
            self.filter_entry.connect('changed', self.on_text_change)
            self.filter_box.pack_start(self.filter_label, False, True, 5)
            self.filter_box.pack_start(self.filter_entry, True, True, 5)
            self.browser_box.pack_start(self.filter_box, False, False, 5)

            self.browser_list = w_brw.List(self.m64p_window)
            treeview = self.browser_list.treeview_call()

            self.browser_box.add(treeview)
        else:
            if g.lock == True:
                warning = Gtk.Label(label="Mupen64Plus's core library hasn't been found. \n Please check it in Options > Configure")
                self.browser_box.add(warning)
                self.browser_box.show_all()

            else:
                warning = Gtk.Label(label="Mupen64Plus's core library version is incompatible. Please upgrade it.")
                self.browser_box.add(warning)
                self.browser_box.show_all()

        self.notebook.append_page(self.browser_box, browser_tab)

        ## Alright, let's add the box ##
        self.main_box.pack_start(self.menubar, False, False, 0)
        self.main_box.pack_start(self.toolbar, False, False, 0)
        self.main_box.pack_start(self.notebook, True, True, 0)
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

        self.notebook.show_all()
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

    def add_video_tab(self):
        ## VideoBox ##
        vidext_tab = Gtk.Label(label="vidext")
        n_pages = self.notebook.get_n_pages()
        if n_pages == 1:
            g.frontend_conf.open_section("Frontend")
            if g.frontend_conf.get_bool("Vidext") == True:
                self.canvas = Gtk.DrawingArea()
                self.canvas.set_can_focus(True)
                #self.canvas.grab_add()
                #self.canvas.add_device_events()
                #self.canvas.add_events(1024) #KEY_PRESS_MASK, seems already enabled by default
                self.canvas.connect("key-press-event", self.on_key_events)
                #self.canvas.add_events(2048) #KEY_RELEASE_MASK, seems already enabled by default
                self.canvas.connect("key-release-event", self.on_key_events)
                #self.canvas.add_events(4) #POINTER_MOTION_MASK
                #self.canvas.add_events(16) #BUTTON_MOTION_MASK
                # Mouse related events
                self.canvas.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK | Gdk.EventMask.BUTTON_PRESS_MASK)
                self.canvas.connect("enter-notify-event", self.on_mouse_events)
                self.canvas.connect("leave-notify-event", self.on_mouse_events)
                self.canvas.connect("button-press-event", self.on_mouse_events)
                import wrapper.vidext as wrp_vext
                wrp_vext.m64p_video.set_window(self.m64p_window)
                self.video_box.add(self.canvas)
            else:
                self.running_label = Gtk.Label(label="Emulator is running.")
                self.video_box.add(self.running_label)

            self.notebook.append_page(self.video_box, vidext_tab)
            self.notebook.show_all()
        self.notebook.set_current_page(1)

    def remove_video_tab(self):
        self.notebook.remove_page(1)
        self.notebook.set_current_page(0)
        g.frontend_conf.open_section("Frontend")
        if g.frontend_conf.get_bool("Vidext") == True:
            self.video_box.remove(self.canvas)
        else:
            self.video_box.remove(self.running_label)

    ### SIGNALS (clicked for button, activate for menu)

    def quit_cb(self, *args):
        if g.running == True:
            #TODO: There should be a dialog asking if the user wants to stop emulation first
            self.main_menu.on_action_stop()
            return True
        else:
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

    def on_reload(self, widget):
        self.Statusbar.push(self.StatusbarContext,"Refreshing the list...")
        self.browser_list.romlist_store_model.clear()
        self.browser_list.cache_update()
        self.browser_list.generate_liststore()
        self.Statusbar.push(self.StatusbarContext,"Refreshing the list...DONE")

    def on_key_events(self, widget, event):
        #https://lazka.github.io/pgi-docs/Gdk-3.0/mapping.html
        #print(event.hardware_keycode)
        if event.get_event_type() == Gdk.EventType.KEY_PRESS:
            g.m64p_wrapper.send_sdl_keydown(w_key.keysym2sdl(event.hardware_keycode).value)
        elif event.get_event_type() == Gdk.EventType.KEY_RELEASE:
            g.m64p_wrapper.send_sdl_keyup(w_key.keysym2sdl(event.hardware_keycode).value)

        return True

    def on_mouse_events(self, widget, event):
        #https://stackoverflow.com/questions/44453139/how-to-hide-mouse-pointer-in-gtk-c
        # In case of Enter/leave notify we make sure that the cursor stays invisibile but only inside the canvas.
        if event.get_event_type() == Gdk.EventType.ENTER_NOTIFY:
            display = self.m64p_window.get_display()
            cursor = Gdk.Cursor.new_for_display(display, Gdk.CursorType.BLANK_CURSOR)
            display.get_default_seat().grab(self.m64p_window.canvas.get_property('window'), Gdk.SeatCapabilities.ALL, True, cursor)
        elif event.get_event_type() == Gdk.EventType.LEAVE_NOTIFY:
            self.m64p_window.get_display().get_default_seat().ungrab()
        elif event.get_event_type() == Gdk.EventType.BUTTON_PRESS:
            print("mouse has clicked")
        else:
            print(event.get_event_type())

    def state_callback(self, context, param, value):
        context_dec = c.cast(context, c.c_char_p).value.decode("utf-8")
        if param == wrp_dt.m64p_core_param.M64CORE_EMU_STATE.value:
            print(wrp_dt.m64p_core_param(param).name, wrp_dt.m64p_emu_state(value).name)
            if wrp_dt.m64p_emu_state(value).name == 'M64EMU_STOPPED':
                self.main_menu.sensitive_menu_stop()
                self.Statusbar.push(self.StatusbarContext, "*** Emulation STOPPED ***")
            elif wrp_dt.m64p_emu_state(value).name == 'M64EMU_RUNNING':
                self.main_menu.sensitive_menu_run()
                self.Statusbar.push(self.StatusbarContext, "*** Emulation STARTED ***")
            elif wrp_dt.m64p_emu_state(value).name == 'M64EMU_PAUSED':
                self.main_menu.sensitive_menu_pause()
                self.Statusbar.push(self.StatusbarContext, "*** Emulation PAUSED ***")

        elif param == wrp_dt.m64p_core_param.M64CORE_VIDEO_MODE.value:
            print(context_dec, wrp_dt.m64p_core_param(param).name, wrp_dt.m64p_video_mode(value).name)
        elif param == wrp_dt.m64p_core_param.M64CORE_SAVESTATE_SLOT.value:
            if g.m64p_wrapper.current_slot != value:
                g.m64p_wrapper.current_slot = value
                self.main_menu.save_slot_items[value].set_active(True)
            print(context_dec, wrp_dt.m64p_core_param(param).name, "SLOT:", value)
            self.Statusbar.push(self.StatusbarContext, "Slot selected: " + str(value))
        elif param == wrp_dt.m64p_core_param.M64CORE_SPEED_FACTOR.value:
            print(context_dec, wrp_dt.m64p_core_param(param).name, value, "%")
            self.Statusbar.push(self.StatusbarContext, "Emulation speed: " + str(value) + "%")
        elif param == wrp_dt.m64p_core_param.M64CORE_SPEED_LIMITER.value:
            print(context_dec, wrp_dt.m64p_core_param(param).name, value)
            self.Statusbar.push(self.StatusbarContext, "Speed limit: " + str(value))
        elif param == wrp_dt.m64p_core_param.M64CORE_VIDEO_SIZE.value:
            #TODO:Not yet mapped
            print(context_dec, wrp_dt.m64p_core_param(param), str(value).encode("utf-8"))
        elif param == wrp_dt.m64p_core_param.M64CORE_AUDIO_VOLUME.value:
            print(context_dec, wrp_dt.m64p_core_param(param).name, value, "%")
            self.Statusbar.push(self.StatusbarContext, "Audio volume: " + str(value) + "%")
        elif param == wrp_dt.m64p_core_param.M64CORE_AUDIO_MUTE.value:
            print(context_dec, wrp_dt.m64p_core_param(param).name, value)
            if value == 1:
                self.Statusbar.push(self.StatusbarContext, "Audio has been muted!")
            else:
                self.Statusbar.push(self.StatusbarContext, "Audio has been unmuted.")
        elif param == wrp_dt.m64p_core_param.M64CORE_INPUT_GAMESHARK.value:
            print(context_dec, wrp_dt.m64p_core_param(param).name, value)
            if value == 1:
                self.Statusbar.push(self.StatusbarContext, "Gameshark button has been pressed!")
        elif param == wrp_dt.m64p_core_param.M64CORE_STATE_LOADCOMPLETE.value:
            print(context_dec, wrp_dt.m64p_core_param(param).name, value)
            if value == 1:
                self.Statusbar.push(self.StatusbarContext, "Save state is loaded successfully.")
            else:
                self.Statusbar.push(self.StatusbarContext, "WARNING: Save state has failed to load!")
        elif param == wrp_dt.m64p_core_param.M64CORE_STATE_SAVECOMPLETE.value:
            print(context_dec, wrp_dt.m64p_core_param(param).name, value)
            if value == 1:
                self.Statusbar.push(self.StatusbarContext, "Save state is done successfully.")
            else:
                self.Statusbar.push(self.StatusbarContext, "WARNING: Unable to create a save state!")
        else:
            # Unmapped params go here.
            print(context_dec, param, value)
