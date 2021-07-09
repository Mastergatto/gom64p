#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, Gdk, GLib
import threading
import logging as log

import widget.dialog as w_dialog
import wrapper.datatypes as wrp_dt

#############
## CLASSES ##
#############

class Actions:
    def __init__(self, parent):
        self.frontend = parent
        self.response = None
        
    ## General ##
    
    def status_push(self, message):
        self.frontend.statusbar.push(self.frontend.statusbar_context, message)

    ## ROM startup ##
    
    def dummy_popup(self):
        if "dummy" in [self.frontend.m64p_wrapper.gfx_filename, self.frontend.m64p_wrapper.audio_filename, \
                        self.frontend.m64p_wrapper.input_filename, self.frontend.m64p_wrapper.rsp_filename]:
            dialog = w_dialog.PopupDialog(self.frontend, \
             f"One of the plugins is set on 'dummy', which means the game won't work properly. \nDo you still want to run it?", \
                                           "dummy")
            self.response = dialog.response

    def thread_rom(self):
        if self.frontend.rom != None and self.frontend.m64p_wrapper.compatible == True:
            self.dummy_popup()
            if self.response:
                self.thread = threading.Thread(name="Emulation", target=self.rom_startup)
                try:
                    self.thread.start()
                    return self.thread
                except:
                    log.error("The emulation thread has encountered an unexpected error")
                    threading.main_thread()
                #except (KeyboardInterrupt, SystemExit):
                #    #https://docs.python.org/3/library/signal.html
                #    thread.stop()
                #    sys.exit()

                # Make the main loop still running
                return True
    
    def rom_startup(self):
        GLib.idle_add(self.frontend.add_video_tab)
        #self.frontend.frontend_conf.open_section("Frontend")
        if self.frontend.frontend_conf.get_bool("Frontend", "Vidext") == True:
            self.frontend.m64p_wrapper.vext_override = True
        else:
            self.frontend.m64p_wrapper.vext_override = False

        if self.frontend.frontend_conf.get_bool("Frontend", "PifLoad") == True:
            self.frontend.m64p_wrapper.pif_loading = True
        else:
            self.frontend.m64p_wrapper.pif_loading = False

        try:
            self.frontend.m64p_wrapper.run(self.frontend.rom)
        except:
            log.error("An error occurred during emulation of a game.")

        # Clean everything
        GLib.idle_add(self.frontend.remove_video_tab)
        
    ## Other ##

    def on_stop(self, *args):
        self.frontend.m64p_wrapper.stop()

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

    def on_savestate(self, path=False, unused=None):
        if path == True:
            dialog = w_dialog.FileChooserDialog(self.frontend, "snapshot", 1) # Gtk.FileChooserAction for save
            file = dialog.path
            self.frontend.m64p_wrapper.state_save(file) #TODO:Currently hardcoded to always create a m64+ save state.
        else:
            self.frontend.m64p_wrapper.state_save()
        self.status_push("Saved")

    def on_loadstate(self, path=False, unused=None):
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

    def on_fullscreen(self, widget, emulating=False):
        if self.frontend.isfullscreen == False:
            #First of all, let's remember the size of the canvas before fullscreening
            self.frontend.canvas.register_size()
            self.frontend.isfullscreen = True
            self.frontend.fullscreen()
            self.frontend.notebook.set_margin_start(0)
            self.frontend.notebook.set_margin_end(0)
            self.frontend.menubar.hide()
            self.frontend.toolbar.hide()
            self.frontend.statusbar.hide()

            self.frontend.m64p_wrapper.core_state_set(wrp_dt.m64p_core_param.M64CORE_VIDEO_MODE.value, wrp_dt.m64p_video_mode.M64VIDEO_FULLSCREEN.value)
            desktop = Gdk.Monitor.get_geometry(Gdk.Display.get_default().get_primary_monitor())
            # (ScreenWidth << 16) + ScreenHeight
            canvas_size = (desktop.width << 16 ) + desktop.height
            self.frontend.m64p_wrapper.core_state_set(wrp_dt.m64p_core_param.M64CORE_VIDEO_SIZE.value, canvas_size)

        else:
            self.frontend.isfullscreen = False
            self.frontend.unfullscreen()
            self.frontend.notebook.set_margin_start(1)
            self.frontend.notebook.set_margin_end(1)
            self.frontend.menubar.show()
            self.frontend.toolbar.show()
            self.frontend.statusbar.show()

            if emulating == True:
                self.frontend.m64p_wrapper.core_state_set(wrp_dt.m64p_core_param.M64CORE_VIDEO_MODE.value, wrp_dt.m64p_video_mode.M64VIDEO_WINDOWED.value)
                #GLib.idle_add(self.frontend.canvas.resize)
                self.frontend.canvas.resize()
                self.frontend.canvas.set_size_request(self.frontend.canvas.width, self.frontend.canvas.height)

    def on_screenshot(self, widget):
        self.frontend.m64p_wrapper.take_next_screenshot()

    def on_advance(self, widget):
        self.frontend.m64p_wrapper.advance_frame()
        
    ## Window ##

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
        self.frontend.m64p_wrapper.rom_get_header()
        header = self.frontend.m64p_wrapper.game_header
        self.frontend.m64p_wrapper.rom_get_settings()
        settings = self.frontend.m64p_wrapper.game_settings
        cic_value = self.frontend.m64p_wrapper.get_cic(header["country"])
        header['cic'] = cic_value
        self.frontend.m64p_wrapper.rom_close()
        
        if option == 'browser':
            return [(header['country'], settings['goodname'], settings['status'], rom, settings['md5'])]
        else:
            return {"header": header, "settings": settings}
        
