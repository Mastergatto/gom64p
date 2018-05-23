#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk,Gdk,GLib,Gio,GdkPixbuf,GObject
import os.path

import global_module as g
import wrapper.datatypes as wrp_dt
import wrapper.vidext as wrp_vext

if 'WAYLAND_DISPLAY' in os.environ and 'PYOPENGL_PLATFORM' not in os.environ:
    os.environ['PYOPENGL_PLATFORM'] = 'egl'

#############
## CLASSES ##
#############

class GL_Area(Gtk.GLArea):
    def __init__(self, parent):
        Gtk.GLArea.__init__(self)
        self.parent = parent
        self.context = None
        #self.gl_context.set_debug_enabled(True)
        self.set_hexpand(True)
        #self.set_has_depth_buffer(False)
        #self.set_has_stencil_buffer(False)

        #self.connect("realize", self.area_realize)
        #self.connect('render', self.area_render)
        #self.connect('create-context', self.area_context)

    def area_realize(self, gl_area):
        gl_area.make_current()
        err = gl_area.get_error()
        if err:
            print("The error is {}".format(err))
        else:
            self.context = gl_area.get_context()
            print("realizing... fine so far")
        return True

    def area_render(self, gl_area, gl_ctx):
        #print(gl_area, gl_ctx)
        gl_area.make_current()
        #gl_area.queue_render()
        #gl_area.attach_buffers()
        print("rendering...")
        return True

    def area_context(self, gl_area):
        err = gl_area.get_error()
        if err:
            print("The error is {}".format(err))
            return None
        else:
            self.context = gl_area.get_context()
            print("context:", self.context)
            return self.context
