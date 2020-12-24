#!/usr/bin/env python3
# coding=utf-8
# © 2020 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, Gdk
import logging as log

import widget.keysym as w_key
import wrapper.datatypes as wrp_dt

#############
## CLASSES ##
#############

class Canvas(Gtk.DrawingArea):
    def __init__(self, parent):
        self.window = parent
        self.width = None
        self.height = None
        self.canvas = None
        
        self.call()
        
    def call(self):
        Gtk.DrawingArea.__init__(self)
        self.set_can_focus(True)
        #self.canvas.add_device_events()
        #self.canvas.add_events(1024) #KEY_PRESS_MASK, seems already enabled by default
        self.connect("key-press-event", self.on_key_events)
        #self.canvas.add_events(2048) #KEY_RELEASE_MASK, seems already enabled by default
        self.connect("key-release-event", self.on_key_events)
        #self.canvas.add_events(4) #POINTER_MOTION_MASK
        #self.canvas.add_events(16) #BUTTON_MOTION_MASK
        # Mouse related events
        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK | Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("enter-notify-event", self.on_mouse_events)
        self.connect("leave-notify-event", self.on_mouse_events)
        self.connect("button-press-event", self.on_mouse_events)
        
        return self
    
    def register_size(self):
        self.height = self.get_allocated_height()
        self.width = self.get_allocated_width()
    
    def resize(self):
        # (ScreenWidth << 16) + ScreenHeight
        self.window.m64p_wrapper.core_state_set(wrp_dt.m64p_core_param.M64CORE_VIDEO_SIZE.value, (self.width << 16 ) + self.height)
        
    def on_key_events(self, widget, event):
        #https://lazka.github.io/pgi-docs/Gdk-3.0/mapping.html
        #print(event.hardware_keycode)
        if event.get_event_type() == Gdk.EventType.KEY_PRESS:
            if self.window.get_focus_visible() == True:
                if event.hardware_keycode == 9:
                    if self.window.isfullscreen == True:
                        self.window.action.on_fullscreen(self, True)
                    else:
                        self.window.trigger_popup(context="running")
                else:                    
                    self.window.m64p_wrapper.send_sdl_keydown(w_key.keysym2sdl(event.hardware_keycode).value)
        elif event.get_event_type() == Gdk.EventType.KEY_RELEASE:
            if self.window.get_focus_visible() == True:
                if event.hardware_keycode == 9:
                    pass
                else:
                    self.window.m64p_wrapper.send_sdl_keyup(w_key.keysym2sdl(event.hardware_keycode).value)

        return True

    def on_mouse_events(self, widget, event):
        #https://stackoverflow.com/questions/44453139/how-to-hide-mouse-pointer-in-gtk-c
        # In case of Enter/leave notify we make sure that the cursor stays invisibile but only inside the canvas.
        display = self.window.get_display()
        if event.get_event_type() == Gdk.EventType.ENTER_NOTIFY:
            pass
        elif event.get_event_type() == Gdk.EventType.LEAVE_NOTIFY:
            #display.get_default_seat().ungrab()
            pass
        elif event.get_event_type() == Gdk.EventType.BUTTON_PRESS:
            cursor = Gdk.Cursor.new_for_display(display, Gdk.CursorType.BLANK_CURSOR)
            #display.get_default_seat().grab(self.window.canvas.get_property('window'), Gdk.SeatCapabilities.ALL, True, cursor)
            log.debug("mouse has clicked on the canvas")
        else:
            log.debug(event.get_event_type())
