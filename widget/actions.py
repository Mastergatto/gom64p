#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, GLib
import threading

import widget.dialog as w_dialog

#############
## CLASSES ##
#############

class Actions:
    def __init__(self, parent):
        self.frontend = parent
        
    ## General ##
    
    def status_push(self, message):
        self.frontend.statusbar.push(self.frontend.statusbar_context, message)

    ## ROM startup ##
    
    def thread_rom(self):
        if self.frontend.rom != None and self.frontend.m64p_wrapper.compatible == True:
            thread = threading.Thread(name="Emulation", target=self.rom_startup)
            try:
                thread.start()
                return thread
            except:
                log.error("The emulation thread has encountered an unexpected error")
                threading.main_thread()
            #except (KeyboardInterrupt, SystemExit):
            #    #https://docs.python.org/3/library/signal.html
            #    thread.stop()
            #    sys.exit()
    
    def rom_startup(self):
        GLib.idle_add(self.frontend.add_video_tab)
        self.frontend.running = True
        #self.frontend.frontend_conf.open_section("Frontend")
        if self.frontend.frontend_conf.get_bool("Frontend", "Vidext") == True:
            self.frontend.m64p_wrapper.vext_override = True
        else:
            self.frontend.m64p_wrapper.vext_override = False
        self.frontend.m64p_wrapper.run(self.frontend.rom)

        # Clean everything
        GLib.idle_add(self.frontend.remove_video_tab)
        self.frontend.running = False
        
    ## Other ##

    def on_stop(self, *args):
        self.frontend.m64p_wrapper.stop()
        self.frontend.running = False

    def on_pause(self, *args):
        self.frontend.m64p_wrapper.pause()
        self.status_push("*** Emulation PAUSED ***")

    def on_resume(self, *args):
        self.frontend.m64p_wrapper.resume()
        self.status_push("*** Emulation RESUMED ***")

    def on_sreset(self, *args):
        self.frontend.m64p_wrapper.reset(0)
        self.status_push("*** Emulation RESETTED ***")

    def on_hreset(self, *args):
        self.frontend.m64p_wrapper.reset(1)
        self.status_push("*** Emulation RESETTED ***")

    def on_savestate(self, widget, path=False, *args):
        if path == True:
            dialog = w_dialog.FileChooserDialog(self.frontend, "snapshot", 1) # Gtk.FileChooserAction for save
            file = dialog.path
            self.frontend.m64p_wrapper.state_save(file) #TODO:Currently hardcoded to always create a m64+ save state.
        else:
            self.frontend.m64p_wrapper.state_save()
        self.status_push("Saved")

    def on_loadstate(self, widget, path=False, *args):
        if path == True:
            dialog = w_dialog.FileChooserDialog(self.frontend, "snapshot", 0) #Gtk.FileChooserAction for load
            file = dialog.path
            self.frontend.m64p_wrapper.state_load(file)
        else:
            self.frontend.m64p_wrapper.state_load()
        self.status_push("Loaded")

    def on_slot_select(self, widget, slot):
        if self.active_slot != slot:
            self.active_slot = slot
            self.frontend.m64p_wrapper.state_set_slot(slot)

    def on_fullscreen(self, widget):
        self.frontend.m64p_wrapper.core_state_set(wrp_dt.m64p_core_param.M64CORE_VIDEO_MODE.value, wrp_dt.m64p_video_mode.M64VIDEO_FULLSCREEN.value)

    def on_screenshot(self, widget):
        self.frontend.m64p_wrapper.take_next_screenshot()

    def on_advance(self, widget):
        self.frontend.m64p_wrapper.advance_frame()
        
    ## Window ##
    
    def on_filter_toggle(self, *args):
        filter_checkbox = self.frontend.view_menu_filter
        n64list_filter = self.frontend.filter_box
        if filter_checkbox.get_active() == 1:
            n64list_filter.show_all()
            self.frontend.frontend_conf.set("Frontend", "FilterConfig", "True")
        else:
            n64list_filter.hide()
            self.frontend.frontend_conf.set("Frontend", "FilterConfig", "False")

    def on_statusbar_toggle(self, *args):
        statusbar_checkbox = self.frontend.view_menu_status
        m64p_statusbar = self.frontend.statusbar
        if statusbar_checkbox.get_active() == 1:
            m64p_statusbar.show()
            self.frontend.frontend_conf.set("Frontend", "StatusConfig", "True")
        else:
            m64p_statusbar.hide()
            self.frontend.frontend_conf.set("Frontend", "StatusConfig", "False")
            
    def on_toolbar_toggle(self, *args):
        if self.frontend.main_menu.view_menu_toolbar.get_active() == True:
            self.frontend.toolbar.show_all()
            self.frontend.frontend_conf.set("Frontend", "ToolbarConfig", "True")
        else:
            self.frontend.toolbar.hide()
            self.frontend.frontend_conf.set("Frontend", "ToolbarConfig", "False")

    def return_state_lock(self):
        if self.frontend.lock == True or self.frontend.m64p_wrapper.compatible == False:
            return False
        else:
            return True
        
    ## Rombrowser ##

    def scan_element(self, rom, option=None):
        '''Method that opens and reads a ROM, and finally returns valuable
         informations that are in it'''
        self.frontend.m64p_wrapper.rom_open(rom)
        header = self.frontend.m64p_wrapper.rom_get_header()
        settings = self.frontend.m64p_wrapper.rom_get_settings()
        self.frontend.m64p_wrapper.rom_close()
        
        if option == 'browser':
            return [(header['country'], settings['goodname'], settings['status'], rom, settings['md5'])]
        else:
            return {"header": header, "settings": settings}
        
