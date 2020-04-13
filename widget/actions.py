#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, GLib

#############
## CLASSES ##
#############

class Actions:
    def __init__(self, parent):
        self.frontend = parent
        
    ## General ##
    
    def status_push(self, message):
        self.frontend.Statusbar.push(self.frontend.StatusbarContext, message)

    ## Other ##
    
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

    def on_ChoosingRom(self, *args):
        dialog = w_dialog.FileChooserDialog(self.frontend, "rom")
        self.status_push("Selecting the ROM...")
        self.rom = dialog.path
        if dialog.path != None:
            rom_uri = GLib.filename_to_uri(self.rom, None)
            if self.recent_manager.has_item(rom_uri) == False:
                self.recent_manager.add_item(rom_uri)

            if self.rom != None and self.frontend.m64p_wrapper.compatible == True:
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

    def on_stop(self, *args):
        self.frontend.m64p_wrapper.stop()
        self.frontend.running = False

    def on_pause(self, *args):
        self.frontend.m64p_wrapper.pause()
        #self.status_push("*** Emulation PAUSED ***")

    def on_resume(self, *args):
        self.frontend.m64p_wrapper.resume()
        #self.status_push("*** Emulation RESUMED ***")

    def on_sreset(self, *args):
        self.frontend.m64p_wrapper.reset(0)
        self.status_push("*** Emulation RESETTED ***")

    def on_hreset(self, *args):
        self.frontend.m64p_wrapper.reset(1)
        self.status_push("*** Emulation RESETTED ***")

    def on_SaveStateAction(self, widget, path=False, *args):
        if path == True:
            dialog = w_dialog.FileChooserDialog(self.frontend, "snapshot", 1) # Gtk.FileChooserAction for save
            file = dialog.path
            self.frontend.m64p_wrapper.state_save(file) #TODO:Currently hardcoded to always create a m64+ save state.
        else:
            self.frontend.m64p_wrapper.state_save()
        self.status_push("Saved")

    def on_LoadStateAction(self, widget, path=False, *args):
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

    def on_fullscreen_action(self, widget):
        self.frontend.m64p_wrapper.core_state_set(wrp_dt.m64p_core_param.M64CORE_VIDEO_MODE.value, wrp_dt.m64p_video_mode.M64VIDEO_FULLSCREEN.value)

    def on_screenshot_action(self, widget):
        self.frontend.m64p_wrapper.take_next_screenshot()

    def on_advance_action(self, widget):
        self.frontend.m64p_wrapper.advance_frame()

    def return_state_lock(self):
        if self.frontend.lock == True or self.frontend.m64p_wrapper.compatible == False:
            return False
        else:
            return True
        
    ## Rombrowser ##    

    def on_recent_activated(self, widget):
        rom_uri = widget.get_current_uri()
        raw_path = GLib.filename_from_uri(rom_uri)
        self.rom = raw_path[0]

        if self.rom != None and self.frontend.m64p_wrapper.compatible == True:
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
        
