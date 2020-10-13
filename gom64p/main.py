#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see COPYING
#####################

###############
## VARIABLES ##
###############
if __name__ == "__main__":
    import os, platform
    # Set the current directory to that of this file.
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Before importing or do anything, we must set those env variable so that this program can work correctly on Linux
    #Gdk.set_allowed_backends("x11, win32, quartz")
    system = platform.system()
    if system == 'Linux':
        #TODO: For now force x11 backend on linux, remove this later.
        os.environ['GDK_BACKEND'] = 'x11'
        if os.environ.get('GDK_BACKEND'):
            if os.environ['GDK_BACKEND'] == 'x11':
                try:
                    import ctypes
                    x11 = ctypes.cdll.LoadLibrary('libX11.so')
                    x11.XInitThreads()
                except:
                    print("Warning: failed to XInitThreads()")
        if not os.environ.get( 'PYOPENGL_PLATFORM' ):
            os.environ['PYOPENGL_PLATFORM'] = 'egl'
    elif system == 'Windows':
        os.environ["PYSDL2_DLL_PATH"] = f"{os.path.dirname(os.path.realpath(__file__))}\\"
    elif system == 'Darwin':
        pass

    #try:
    #    # Keep GTK+ from mixing languages
    #    #Locale.setlocale(Locale.LC_MESSAGES, "C")
    #    locale.setlocale(locale.LC_ALL, "")
    #except locale.Error:
    #    log.err("Unsupported locale setting. Fix your locales")

#############
## MODULES ##
#############
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Gio", "2.0")
gi.require_version("GLib", "2.0")

from gi.repository import Gtk, Gdk, Gio, GLib
from gettext import gettext as _
import argparse, sys

import logging as log
import utils.logging as u_log
import widget.window as w_main

###############
## FUNCTIONS ##
###############

##########
## MAIN ##
##########

class GoodOldM64pApp(Gtk.Application):

    def __init__(self, app_id):
        self.app_id = app_id
        super().__init__(application_id=self.app_id,
                                flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.connect('command-line', self.do_command_line)
        GLib.set_application_name(_("Good Old Mupen64+"))
        GLib.set_prgname('gom64p')
        #GLib.setenv("")
        #self.settings = Gio.Settings.new('org.mupen64plus.good-old-m64p')

        self.main = None
        self.args = None
        self.frontend_conf = None
        self.logger = u_log.Logger()

    def do_startup(self):
        '''
        Gtk.Application startup handler
        '''

        Gtk.Application.do_startup(self)
    def do_activate(self):
        '''
        Gtk.Application activate handler
        '''

        if not self.main:
            self.main = w_main.GoodOldM64pWindow(self)

    def do_shutdown(self):
        '''
        Gtk.Application shutdown handler
        Do clean up before the application is closed.
        this is triggered when self.quit() is called.
        '''

        log.debug("Closing...")
        if self.frontend_conf != None:
            self.frontend_conf.write()
        Gtk.Application.do_shutdown(self)

    def do_command_line(self, argc, argv):
        '''
        Gtk.Application command line handler
        called if Gio.ApplicationFlags.HANDLES_COMMAND_LINE is set.
        must call the self.do_activate() to get the application up and running.
        '''

        #https://docs.python.org/3/library/argparse.html
        command_parser = argparse.ArgumentParser(prog="Good Old Mupen64+",
                        usage=sys.argv[0] + " [OPTIONS]",
                        description="gom64p is a frontend (in Python \
                        and GTK+3) for mupen64plus, a free software and \
                        multi-platform Nintendo 64 emulator.")
        command_parser.add_argument('-d','--debug', action='store_true',
                      help='Enable debug mode (not related with mupen64plus\'s \
                      debugger!)')
        command_parser.add_argument('--enable-csd', action='store_true',
                      help='Enable Client Side Decorations (only on GNOME)')
        command_parser.add_argument('--lib', action='store',
                      help='path to libmupen64plus')
        command_parser.add_argument('--configdir', action='store',
                      help='path to mupen64plus\'s configs dir')
        command_parser.add_argument('--plugindir', action='store',
                      help='path to mupen64plus\'s plugin dir')
        command_parser.add_argument('--datadir', action='store',
                      help='path to mupen64plus\'s data dir')
        self.args = command_parser.parse_args(argv.get_arguments()[1:])
        self.do_activate()
        return 0


if __name__ == "__main__":
    try:
        application = GoodOldM64pApp('net.Mastergatto.gom64p')

        exit_status = application.run(sys.argv)
        sys.exit(exit_status)
    except KeyboardInterrupt:
        log.warning("Keyboard interrupt (Ctrl + C), shutting down...")
        sys.exit()



