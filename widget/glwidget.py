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
import widget.dialog as w_dialog
import widget.plugin as w_plugin

#if 'WAYLAND_DISPLAY' in os.environ and 'PYOPENGL_PLATFORM' not in os.environ:
#    os.environ['PYOPENGL_PLATFORM'] = 'egl'

from OpenGL.GL import glClearColor, glClear, GL_COLOR_BUFFER_BIT, glFlush, GL_DEPTH_BUFFER_BIT

#############
## CLASSES ##
#############

class GL_Area(Gtk.GLArea):
    def __init__(self):
        Gtk.GLArea.__init__(self)
        self.context = None
        self.set_hexpand(True)
        self.set_has_depth_buffer(True)



        #self.connect("realize", self.on_realize)
        self.connect('render', self.render)
        self.connect('create-context', self.area_context)

    def on_realize(self, gl_area):
        err = gl_area.get_error()
        if err:
            print("The error is {}".format(err))

    def render(self, gl_area, gl_ctx):
        print(gl_area, gl_ctx)
        self.context = gl_ctx
        print(self.context)
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        return True

    def area_context(self, gl_area):
        print(self.context , "context")
        return self.context

drawing_area = GL_Area()
