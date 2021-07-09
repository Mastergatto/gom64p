#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, GLib
import logging as log

#############
## CLASSES ##
#############
class FileChooserDialog(Gtk.FileChooserDialog):
    def __init__(self, parent, category, options=None):
        self.frontend = parent
        title = "Dialog"
        self.path = None
        accept = "_Select"
        cancel = "_Cancel"
        
        self.dialog = Gtk.FileChooserNative.new(title, parent, Gtk.FileChooserAction.OPEN, accept, cancel)
        self.dialog.set_modal(True)
        self.dialog.connect("response", self.file_chooser)
        
        if category == "directory":
            self.dialog.set_title("Please select the directory")
            self.dialog.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
            self.dialog.connect("response", self.directory_chooser)
        elif category == "rom":
            self.dialog.set_title("Please select a N64 game image")

            filter_extension = Gtk.FileFilter()
            filter_extension.set_name("N64 image (.n64, .v64, .z64)")
            #filter_extension.add_mime_type("application/x-n64-rom")
            filter_extension.add_pattern("*.n64")
            filter_extension.add_pattern("*.v64")
            filter_extension.add_pattern("*.z64")
            self.dialog.add_filter(filter_extension)

            filter_any = Gtk.FileFilter()
            filter_any.set_name("Any files")
            filter_any.add_pattern("*")
            self.dialog.add_filter(filter_any)

        elif category == "gameboy":
            self.dialog.set_title("Please select the SAV/GB file")

            filter_text = Gtk.FileFilter()
            if options == "rom":
                filter_text.set_name("Gameboy image file (.gb)")
                filter_text.add_pattern("*.gb")
            elif options == "ram":
                filter_text.set_name("Gameboy save file (.sav)")
                filter_text.add_pattern("*.sav")
            self.dialog.add_filter(filter_text)

            filter_any = Gtk.FileFilter()
            filter_any.set_name("Any files")
            filter_any.add_pattern("*")
            self.dialog.add_filter(filter_any)

        elif category == "64dd":
            self.dialog.set_title("Please select the IPL/Disk ROM binary")

            filter_text = Gtk.FileFilter()
            if options == "ipl":
                filter_text.set_name("IPL ROM (*.bin, *.rom)")
                filter_text.add_pattern("*.bin")
                filter_text.add_pattern("*.rom")
            elif options == "disk":
                filter_text.set_name("Disk image game (*.ndd)")
                filter_text.add_pattern("*.ndd")
            self.dialog.add_filter(filter_text)

            filter_any = Gtk.FileFilter()
            filter_any.set_name("Any files")
            filter_any.add_pattern("*")
            self.dialog.add_filter(filter_any)

        elif category == "snapshot":
            if options == 0:
                #Load Snapshot
                self.dialog.set_title("Please select the snapshot file")

                filter_snapshot = Gtk.FileFilter()
                filter_snapshot.set_name("Mupen64plus/Project64 save state (.st*, .pj*)")
                filter_snapshot.add_pattern("*.st*")
                filter_snapshot.add_pattern("*.zip")
                filter_snapshot.add_pattern("*.pj*")
                self.dialog.add_filter(filter_snapshot)

                filter_any = Gtk.FileFilter()
                filter_any.set_name("Any files")
                filter_any.add_pattern("*")
                self.dialog.add_filter(filter_any)
            elif options == 1:
                #Save snapshot
                #TODO: too many things like setting automatically extension name or returning the format
                self.dialog.set_title("Please select a name for file to save")
                self.dialog.set_action(Gtk.FileChooserAction.SAVE)
                self.dialog.set_current_name("Untitled.st0")
                self.dialog.set_do_overwrite_confirmation(True)

                filter_m64p = Gtk.FileFilter()
                filter_m64p.set_name("Mupen64plus save state (.st*)")
                filter_m64p.add_pattern("*.st")
                self.dialog.add_filter(filter_m64p)

                #filter_pjc = Gtk.FileFilter()
                #filter_pjc.set_name("Compressed PJ64 save state")
                #filter_pjc.add_pattern("*.pj.zip")
                #self.dialog.add_filter(filter_pjc)

                #filter_pj64 = Gtk.FileFilter()
                #filter_pj64.set_name("Project64 save state")
                #filter_pj64.add_pattern("*.pj")
                #self.dialog.add_filter(filter_pj64)

        elif category == "library":
            self.dialog.set_title("Please select the Mupen64plus library")

            filter_text = Gtk.FileFilter()
            filter_text.set_name("Mupen64plus library (.so, .dll)")
            #filter_text.add_mime_type("application/x-n64-rom")
            filter_text.add_pattern("libmupen64plus.so*")
            filter_text.add_pattern("mupen64plus.dll")
            self.dialog.add_filter(filter_text)

            filter_any = Gtk.FileFilter()
            filter_any.set_name("Any files")
            filter_any.add_pattern("*")
            self.dialog.add_filter(filter_any)

        elif category == "pif":
            self.dialog.set_title("Please select the PIF ROM image")

            filter_extension = Gtk.FileFilter()
            filter_extension.set_name("N64 PIF ROM image (.bin, .rom)")
            #filter_extension.add_mime_type("application/x-n64-rom")
            filter_extension.add_pattern("*.bin")
            filter_extension.add_pattern("*.rom")
            self.dialog.add_filter(filter_extension)

            filter_any = Gtk.FileFilter()
            filter_any.set_name("Any files")
            filter_any.add_pattern("*")
            self.dialog.add_filter(filter_any)

        self.dialog.show()

    def directory_chooser(self, widget, response_id):
        if response_id == Gtk.ResponseType.ACCEPT:
            if self.frontend.environment.platform["system"] == "Windows":
                self.path = self.dialog.get_file().get_path() + "\\"
            else:
                self.path = self.dialog.get_file().get_path() + "/"
            log.debug(f"Directory selected: {self.path}")
        widget.destroy()

    def file_chooser(self, widget, response_id):
        if response_id == Gtk.ResponseType.ACCEPT:
            self.path = self.dialog.get_file().get_path()
            log.debug(f"File selected: {self.path}")
        elif response_id == Gtk.ResponseType.CANCEL:
            pass
        widget.destroy()

class DialogAbout(Gtk.Dialog):
    def __init__(self, parent, window, whichtype):
        if whichtype == 'core':
            self.on_core_clicked(window)
        elif whichtype == 'frontend':
            self.on_frontend_clicked(window)

    def on_core_clicked(self, window):
        about_core = Gtk.AboutDialog()
        about_core.set_authors(["Richard Goedeken (Richard42)","John Chadwick (NMN)",
                              "James Hood (Ebenblues)","Scott Gorman (okaygo)",
                              "Scott Knauert (Tillin9)","Jesse Dean (DarkJezter)",
                              "Louai Al-Khanji (slougi)","Bob Forder (orbitaldecay)",
                              "Jason Espinosa (hasone)","Dylan Wagstaff (Pyromanik)",
                              "HyperHacker","Hacktarux","Dave2001","Zilmar",
                              "Gregor Anich (Blight)","Juha Luotio (JttL)",
                              "and many more..."])
        about_core.set_license_type(Gtk.License(2)) #GPL2
        about_core.set_program_name("mupen64plus")
        about_core.set_comments("Mupen64plus is an open source Nintendo 64 emulator.")
        about_core.set_version("version 2.6")
        about_core.set_copyright("© The Mupen64Plus Team")
        about_core.set_website("http://www.mupen64plus.org/")
        about_core.set_website_label("Mupen64plus website")
        #about_core.set_documenters("")
        #about_core.set_logo(GdkPixbuf.Pixbuf.new_from_file("ui/mupen64plus.svg"))
        about_core.set_transient_for(window)
        about_core.set_modal(True)
        about_core.show()

    def on_frontend_clicked(self, window):
        about_frontend = Gtk.AboutDialog()
        about_frontend.set_authors(["Mastergatto"])
        about_frontend.set_license_type(Gtk.License(2)) #GPL2
        about_frontend.set_program_name("Good Old M64+")
        about_frontend.set_version("0.1")
        about_frontend.set_copyright("©2021 Mastergatto")
        about_frontend.set_artists(["Freepik (The flags are designed by Freepik from Flaticon (www.flaticon.com))", "Google (Noto Emoji Travel &amp; Places Icons set)"])
        about_frontend.set_website("https://github.com/Mastergatto/gom64p")
        about_frontend.set_website_label("Github repository")
        about_frontend.set_transient_for(window)
        about_frontend.set_modal(True)

        about_frontend.show()

class PopupDialog(Gtk.MessageDialog):
    def __init__(self, parent, text, context):
        self.frontend = parent
        self.response = None

        dialog = Gtk.MessageDialog(
            transient_for=parent,
            #flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=str(text))
        #dialog.set_markup(str(text))
        dialog.set_modal(True)
        dialog.connect("response", self.on_response, context)
        dialog.show()

        # This is not recommended, but it's still needed under special circumstances.
        self.dialog_loop = GLib.MainLoop.new(None,True)
        GLib.MainLoop.run(self.dialog_loop)

    def on_response(self, widget, response_id, context):
        #log.debug(widget, response_id)

        if response_id == Gtk.ResponseType.YES:
            if context == "running":
                log.debug("Detected quit signal while game is running, decided to stop it.")
                self.frontend.action.on_stop()
            elif context == "dummy":
                log.debug("Decided to run anyways a game even with dummy plugin.")
                self.response = True
        #elif response_id == Gtk.ResponseType.NO:
        else:
            if context == "running":
                log.debug("Detected quit signal while game is running. Not stopping it.")
            elif context == "dummy":
                log.debug("Decided to not run a game with dummy plugin.")
                self.response = False
        widget.destroy()
        GLib.MainLoop.quit(self.dialog_loop)
