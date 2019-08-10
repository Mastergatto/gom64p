#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk
import global_module as g
import logging as log

#############
## CLASSES ##
#############
class FileChooserDialog(Gtk.FileChooserDialog):
    def __init__(self, parent, category, options=None):
        self.path = None
        if category == "directory":
            self.directory_chooser(parent)
        elif category == "rom":
            self.rom_chooser(parent)
        elif category == "gameboy":
            self.gb_chooser(parent, options)
        elif category == "64dd":
            self.n64dd_chooser(parent, options)
        elif category == "snapshot":
            if options == 0:
                self.snapshot_loader(parent)
            elif options == 1:
                self.snapshot_saver(parent)
        elif category == "library":
            self.library_chooser(parent)

    def directory_chooser(self, parent):
        dialog = Gtk.FileChooserDialog(title="Please select the directory",transient_for=parent,action=2,add_buttons=0)
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_Select", Gtk.ResponseType.ACCEPT)
        #dialog.set_default_size(800, 400)
        dialog.set_type_hint(1) #=Dialog
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            import platform
            system = platform.system()
            if system == "Windows":
                self.path = dialog.get_filename() + "\\" #Untested
            else:
                self.path = dialog.get_filename() + "/"
            log.debug(f"Directory selected: {self.path}")
        dialog.destroy()

    def rom_chooser(self, parent):
        dialog = Gtk.FileChooserDialog(title="Please choose a N64 game image",transient_for=parent,action=0,add_buttons=0)
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_Open", Gtk.ResponseType.ACCEPT)
        #dialog.set_default_size(800, 400)
        dialog.set_type_hint(1) #=Dialog
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        filter_text = Gtk.FileFilter()
        filter_text.set_name("N64 image (.n64, .v64, .z64)")
        #filter_text.add_mime_type("application/x-n64-rom")
        filter_text.add_pattern("*.n64")
        filter_text.add_pattern("*.v64")
        filter_text.add_pattern("*.z64")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.path = dialog.get_filename()
            log.debug(f"File selected: {self.path}")
            #return self.path
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.response(response)
        dialog.destroy()

    def gb_chooser(self, parent, file):
        dialog = Gtk.FileChooserDialog(title="Please select the SAV/GB file", transient_for=parent, action=0, add_buttons=0)
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_Select", Gtk.ResponseType.ACCEPT)
        #dialog.set_default_size(800, 400)
        dialog.set_type_hint(1) #=Dialog
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        filter_text = Gtk.FileFilter()
        if file == "rom":
            filter_text.set_name("Gameboy image file (.gb)")
            filter_text.add_pattern("*.gb")
        elif file == "ram":
            filter_text.set_name("Gameboy save file (.sav)")
            filter_text.add_pattern("*.sav")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.path = dialog.get_filename()
            log.debug(f"File selected: {self.path}")
            #return self.path
        dialog.destroy()

    def n64dd_chooser(self, parent, file):
        dialog = Gtk.FileChooserDialog(title="Please select the IPL/Disk ROM binary", transient_for=parent, action=0, add_buttons=0)
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_Select", Gtk.ResponseType.ACCEPT)
        #dialog.set_default_size(800, 400)
        dialog.set_type_hint(1) #=Dialog
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        filter_text = Gtk.FileFilter()
        if file == "ipl":
            filter_text.set_name("IPL ROM (*.bin, *.rom)")
            filter_text.add_pattern("*.bin")
            filter_text.add_pattern("*.rom")
        elif file == "disk":
            filter_text.set_name("Disk image game (*.ndd)")
            filter_text.add_pattern("*.ndd")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.path = dialog.get_filename()
            log.debug(f"File selected: {self.path}")
            #return self.path
        dialog.destroy()

    def snapshot_loader(self, parent):
        dialog = Gtk.FileChooserDialog(title="Please select the stX/pjX file", transient_for=parent, action=0, add_buttons=0)
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_Select", Gtk.ResponseType.ACCEPT)
        #dialog.set_default_size(800, 400)
        dialog.set_type_hint(1) #=Dialog
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        filter_snapshot = Gtk.FileFilter()
        filter_snapshot.set_name("Mupen64plus/Project64 save state (.st*, .pj*")
        filter_snapshot.add_pattern("*.st*")
        filter_snapshot.add_pattern("*.zip")
        filter_snapshot.add_pattern("*.pj*")
        dialog.add_filter(filter_snapshot)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.path = dialog.get_filename()
            log.debug(f"File selected: {self.path}")
            #return self.path
        dialog.destroy()

    def snapshot_saver(self, parent):
        #TODO: too many things like setting automatically extension name or returning the format
        dialog = Gtk.FileChooserDialog(title="Please choose a name for file to save", transient_for=parent, action=1, add_buttons=0)
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_Select", Gtk.ResponseType.ACCEPT)
        #dialog.set_default_size(800, 400)
        dialog.set_type_hint(1) #=Dialog
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        dialog.set_current_name("Untitled.st0")
        dialog.set_do_overwrite_confirmation(True)


        filter_m64p = Gtk.FileFilter()
        filter_m64p.set_name("Mupen64plus save state (.st*)")
        filter_m64p.add_pattern("*.st")
        dialog.add_filter(filter_m64p)

        #filter_pjc = Gtk.FileFilter()
        #filter_pjc.set_name("Compressed PJ64 save state")
        #filter_pjc.add_pattern("*.pj.zip")
        #dialog.add_filter(filter_pjc)

        #filter_pj64 = Gtk.FileFilter()
        #filter_pj64.set_name("Project64 save state")
        #filter_pj64.add_pattern("*.pj")
        #dialog.add_filter(filter_pj64)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.path = dialog.get_filename()
            #self.ret_type =
            log.debug(f"File selected: {self.path}")
            #return self.path
        dialog.destroy()

    def library_chooser(self, parent):
        dialog = Gtk.FileChooserDialog(title="Please find the Mupen64plus library",transient_for=parent,action=0,add_buttons=0)
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_Select", Gtk.ResponseType.ACCEPT)
        #dialog.set_default_size(800, 400)
        dialog.set_type_hint(1) #=Dialog
        dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        filter_text = Gtk.FileFilter()
        filter_text.set_name("Mupen64plus library (.so, .dll)")
        #filter_text.add_mime_type("application/x-n64-rom")
        filter_text.add_pattern("libmupen64plus.so*")
        filter_text.add_pattern("mupen64plus.dll")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.path = dialog.get_filename()
            log.debug(f"File selected: {self.path}")
            #return self.path
        dialog.destroy()

class DialogAbout(Gtk.Dialog):
    def __init__(self,parent,whichtype):
        if whichtype == 'core':
            self.on_core_clicked(parent)
        elif whichtype == 'frontend':
            self.on_frontend_clicked(parent)

    def on_core_clicked(self, parent):
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
        about_core.set_transient_for(parent)

        response = about_core.run()
        if response == Gtk.ResponseType.OK:
            pass
        elif response == Gtk.ResponseType.CANCEL:
            pass

        about_core.destroy()

    def on_frontend_clicked(self, parent):
        about_frontend = Gtk.AboutDialog()
        about_frontend.set_authors(["Mastergatto"])
        about_frontend.set_license_type(Gtk.License(2)) #GPL2
        about_frontend.set_program_name("Good Old M64+")
        about_frontend.set_version("0.1")
        about_frontend.set_copyright("©2019 Mastergatto")
        about_frontend.set_artists(["Freepik (The flags are designed by Freepik from Flaticon (www.flaticon.com))", "Google (Noto Emoji Travel & Places Icons set)"])
        about_frontend.set_website("https://github.com/Mastergatto/gom64p")
        about_frontend.set_website_label("Github repository")
        about_frontend.set_transient_for(parent)

        response = about_frontend.run()
        if response == Gtk.ResponseType.OK:
            pass
        elif response == Gtk.ResponseType.CANCEL:
            pass

        about_frontend.destroy()
