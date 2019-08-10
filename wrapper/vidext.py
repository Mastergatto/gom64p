#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
import ctypes as c
from gi.repository import Gtk
import sys, time
import logging as log

import external.sdl2 as sdl
import wrapper.datatypes as wrp_dt

###############
## VARIABLES ##
###############

#############
## CLASSES ##
#############

class Vidext():
    def __init__(self):
        self.sdl_context = None
        self.window = None
        self.foreign_window = None
        self.title = None
        self.fullscreen_window = None

        self.modes = []
        self.fullscreen = 0
        self.width = 0
        self.height = 0
        self.former_size = None

    def set_window(self, window):
        self.window = window

    def video_init(self):
        log.debug("Vidext: video_init()")
        #source: https://github.com/mupen64plus/mupen64plus-ui-python/blob/master/src/m64py/core/vidext.py#L34
        sdl.SDL_InitSubSystem(sdl.SDL_INIT_VIDEO)
        sdl.SDL_InitSubSystem(sdl.SDL_INIT_JOYSTICK) #TODO: Is it really necessary?
        display = sdl.SDL_DisplayMode()
        for mode in range(sdl.SDL_GetNumDisplayModes(0)):
            ret = sdl.SDL_GetDisplayMode(0, mode, c.byref(display))
            if (display.w, display.h) not in self.modes:
                self.modes.append((display.w, display.h))

        log.debug(self.modes)
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_quit(self):
        log.debug("Vidext: video_quit()")
        sdl.SDL_GL_DeleteContext(self.sdl_context)
        sdl.SDL_DestroyWindow(self.foreign_window)
        sdl.SDL_Quit()
        if self.title != None:
            self.window.set_title(self.title)
        self.window.set_resizable(True)
        self.window.canvas.set_size_request(1, 1) # First we must lift the restriction on the minimum size of the widget
        time.sleep(0.1) #Workaround?
        self.window.resize(self.former_size[0], self.former_size[1])
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_list_modes(self, sizearray, numsizes):
        log.debug(f"Vidext: video_list_modes(sizearray: {sizearray}, {numsizes}, {numsizes}")
        # source: https://github.com/mupen64plus/mupen64plus-ui-python/blob/master/src/m64py/core/vidext.py#L80
        numsizes.contents.value = len(self.modes)
        for num, mode in enumerate(self.modes):
            width, height = mode
            sizearray[num].uiWidth = width
            sizearray[num].uiHeight = height
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_set_mode(self, width, height, bits, screenmode, flags):
        log.debug(f"Vidext: video_set_mode(width: {str(width)}, height: {str(height)}, bits: {str(bits)}, screenmode: {wrp_dt.m64p_video_mode(screenmode).name}, flags:{wrp_dt.m64p_video_flags(flags).name}")

        self.width = width
        self.height = height
        self.former_size = self.window.get_size()
        # Needed for get_preferred_size() to work
        self.window.set_resizable(False)
        # Necessary so that we tell the GUI to not shrink the window further than the size of the widget set by mupen64plus
        self.window.canvas.set_size_request(width, height)
        # It doesn't just get the preferred size, it DOES resize the window too
        self.window.canvas.get_preferred_size()
        # Mandatory since we're doing the hack for embedding SDL into GTK+, otherwise gamepads won't work here since GTK+ doesn't handle those inputs.
        sdl.SDL_SetHint(sdl.SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, b"1")

        if sys.platform.startswith('linux') or sys.platform.startswith('freebsd') :
            from gi.repository import GdkX11
            # Hack to embed sdl window into the frontend.
            # XXX: It won't work on wayland without forcing GDK_BACKEND=x11, but I can live with that.
            self.foreign_window = sdl.SDL_CreateWindowFrom(self.window.canvas.get_property('window').get_xid())
        elif sys.platform == 'cygwin':
            #sdl.SDL_SetHint(sdl.SDL_HINT_VIDEO_WINDOW_SHARE_PIXEL_FORMAT, x)
            sdl.SDL_SetHint(sdl.SDL_HINT_RENDER_DRIVER, b"opengl")

            # https://stackoverflow.com/questions/23021327/how-i-can-get-drawingarea-window-handle-in-gtk3/27236258#27236258
            # https://gitlab.gnome.org/GNOME/gtk/issues/510
            drawingareawnd = self.window.canvas.get_property("window")
            # make sure to call ensure_native before e.g. on realize
            if not drawingareawnd.has_native():
                log.warning("Vidext: Your window is gonna freeze as soon as you move or resize it...")
            c.pythonapi.PyCapsule_GetPointer.restype = c.c_void_p
            c.pythonapi.PyCapsule_GetPointer.argtypes = [c.py_object]
            drawingarea_gpointer = c.pythonapi.PyCapsule_GetPointer(drawingareawnd.__gpointer__, None)
            # get the win32 handle
            libgdk = ctypes.CDLL("libgdk-3-0.dll")
            handle = libgdk.gdk_win32_window_get_handle(drawingarea_gpointer)
            self.foreign_window = sdl.SDL_CreateWindowFrom(handle)
        elif sys.platform == 'darwin':
            # https://gitlab.gnome.org/GNOME/pygobject/issues/112
            drawingareawnd = self.window.canvas.get_property("window")
            # make sure to call ensure_native before e.g. on realize
            if not drawingareawnd.has_native():
                log.warning("Vidext: Your window is gonna freeze as soon as you move or resize it...")
            ctypes.pythonapi.PyCapsule_GetPointer.restype = ctypes.c_void_p
            ctypes.pythonapi.PyCapsule_GetPointer.argtypes = [ctypes.py_object]
            gpointer = ctypes.pythonapi.PyCapsule_GetPointer(window.__gpointer__, None)
            libgdk = ctypes.CDLL ("libgdk-3.dylib")
            libgdk.gdk_quartz_window_get_nsview.restype = ctypes.c_void_p
            libgdk.gdk_quartz_window_get_nsview.argtypes = [ctypes.c_void_p]
            handle = libgdk.gdk_quartz_window_get_nsview(gpointer)

            self.foreign_window = sdl.SDL_CreateWindowFrom(handle)

        # XXX: since SDL_window is a pointer, we can't set flags normally with Python, so we use the special function pointer() so that we can modify directly it.
        ### HACK: we have to wrapper SDL_Window struct so that we can make it expose its fields to be modified. Thus we add the SDL_WINDOW_OPENGL flag to it.
        # Lastly, we unload GL library. Why? WILD GUESS: without SDL_WINDOW_OPENGL flag, SDL creates the window with only OpenGL 1.x, which isn't what we need to render anything,
        # we need at least OpenGL 3.x. So by unloading GL library, it forces SDL to reload, but this time with the right version of OpenGL. ###
        old_flags = c.pointer(self.foreign_window)[0] # Dereference it
        self.foreign_window.contents.flags = sdl.SDL_WINDOW_FOREIGN | sdl.SDL_WINDOW_OPENGL # It should return 2054 instead of 2050, but regardless it works.
        new_flags = c.pointer(self.foreign_window) # Re-reference it
        sdl.SDL_GL_LoadLibrary(None) #XXX Necessary to make the hack work.
        ### End hack ###

        self.sdl_context = sdl.SDL_GL_CreateContext(self.foreign_window)
        sdl.SDL_GL_MakeCurrent(self.foreign_window, self.sdl_context)
        #print(sdl.SDL_GetError())

        log.debug(f"video_set_mode context: {self.sdl_context}")
        if self.sdl_context != None:
            self.sdl_context2 = sdl.SDL_GL_GetCurrentContext()
            log.debug(f"Context SDL: {self.sdl_context}, {self.sdl_context2}")

            self.info = sdl.SDL_SysWMinfo()
            #version = sdl.SDL_VERSION(c.byref(info.version))
            version = sdl.SDL_GetVersion(c.byref(self.info.version))
            self.window_info = sdl.SDL_GetWindowWMInfo(self.foreign_window, c.byref(self.info))
            #print(self.info.subsystem)
            if self.info.subsystem == sdl.SDL_SYSWM_X11:
                print("The OS is Linux, using X11")
            #TODO: How to get to info.x11.window?
                print(repr(self.info))
            elif self.info.subsystem == sdl.SDL_SYSWM_WAYLAND:
                print("The OS is Linux, using Wayland")
            elif self.info.subsystem == sdl.SDL_SYSWM_WINDOWS:
                print("The OS is Windows")
            elif self.info.subsystem == sdl.SDL_SYSWM_COCOA:
                print("The OS is Mac OS X")

            #print(sdl.SDL_GetError())
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            log.error("Vidext: video_set_mode() has reported M64ERR_SYSTEM_FAIL")
            return wrp_dt.m64p_error.M64ERR_SYSTEM_FAIL.value

    def gl_get_proc(self, proc):
        address = sdl.SDL_GL_GetProcAddress(proc)
        if address is not None:
            return address
        else:
            log.error(f"Vidext: gl_get_proc({proc.decode()}) returns None")

    def gl_get_attr(self, attr, pvalue):
        attr = wrp_dt.m64p_GLattr(attr).name
        log.info(f"Vidext: gl_get_attr(attr:{attr}, pvalue:{str(pvalue.contents.value)})")
        value = None

        if attr == 'M64P_GL_DOUBLEBUFFER':
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_DOUBLEBUFFER, pvalue)
        elif attr == 'M64P_GL_BUFFER_SIZE':
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_BUFFER_SIZE, pvalue)
        elif attr == 'M64P_GL_DEPTH_SIZE':
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_DEPTH_SIZE, pvalue)
        elif attr == 'M64P_GL_RED_SIZE':
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_RED_SIZE, pvalue)
        elif attr == 'M64P_GL_GREEN_SIZE':
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_GREEN_SIZE, pvalue)
        elif attr == 'M64P_GL_BLUE_SIZE':
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_BLUE_SIZE, pvalue)
        elif attr == 'M64P_GL_ALPHA_SIZE':
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_ALPHA_SIZE, pvalue)
        elif attr == 'M64P_GL_SWAP_CONTROL':
            value = sdl.SDL_GL_GetSwapInterval()
        elif attr == 'M64P_GL_MULTISAMPLEBUFFERS':
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_MULTISAMPLEBUFFERS, pvalue)
        elif attr == 'M64P_GL_MULTISAMPLESAMPLES':
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_MULTISAMPLESAMPLES, pvalue)
        elif attr == 'M64P_GL_CONTEXT_MAJOR_VERSION':
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_CONTEXT_MAJOR_VERSION, pvalue)
        elif attr == 'M64P_GL_CONTEXT_MINOR_VERSION':
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_CONTEXT_MINOR_VERSION, pvalue)
        elif attr == 'M64P_GL_CONTEXT_PROFILE_MASK':
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_CONTEXT_PROFILE_MASK, pvalue)
        else:
            pass

        if value == pvalue.contents.value:
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            log.error(f"Vidext: gl_get_attr() has reported M64ERR_SYSTEM_FAIL, value is: {value}")
            return wrp_dt.m64p_error.M64ERR_SYSTEM_FAIL.value

    def gl_set_attr(self, attr, value):
        attr = wrp_dt.m64p_GLattr(attr).name
        log.info(f"INFO - Vidext.gl_set_attr(): attr '{str(attr)}'; value '{str(value)}'")

        if attr == 'M64P_GL_DOUBLEBUFFER':
            sdl.SDL_GL_SetAttribute(sdl.SDL_GL_DOUBLEBUFFER, value)
        elif attr == 'M64P_GL_BUFFER_SIZE':
            sdl.SDL_GL_SetAttribute(sdl.SDL_GL_BUFFER_SIZE, value)
        elif attr == 'M64P_GL_DEPTH_SIZE':
            sdl.SDL_GL_SetAttribute(sdl.SDL_GL_DEPTH_SIZE, value)
        elif attr == 'M64P_GL_RED_SIZE':
            sdl.SDL_GL_SetAttribute(sdl.SDL_GL_RED_SIZE, value)
        elif attr == 'M64P_GL_GREEN_SIZE':
            sdl.SDL_GL_SetAttribute(sdl.SDL_GL_GREEN_SIZE, value)
        elif attr == 'M64P_GL_BLUE_SIZE':
            sdl.SDL_GL_SetAttribute(sdl.SDL_GL_BLUE_SIZE, value)
        elif attr == 'M64P_GL_ALPHA_SIZE':
            sdl.SDL_GL_SetAttribute(sdl.SDL_GL_ALPHA_SIZE, value)
        elif attr == 'M64P_GL_SWAP_CONTROL':
            sdl.SDL_GL_SetSwapInterval(value)
        elif attr == 'M64P_GL_MULTISAMPLEBUFFERS':
            sdl.SDL_GL_SetAttribute(sdl.SDL_GL_MULTISAMPLEBUFFERS, value)
        elif attr == 'M64P_GL_MULTISAMPLESAMPLES':
            sdl.SDL_GL_SetAttribute(sdl.SDL_GL_MULTISAMPLESAMPLES, value)
        elif attr == 'M64P_GL_CONTEXT_MAJOR_VERSION':
            sdl.SDL_GL_SetAttribute(sdl.SDL_GL_CONTEXT_MAJOR_VERSION, value)
        elif attr == 'M64P_GL_CONTEXT_MINOR_VERSION':
            sdl.SDL_GL_SetAttribute(sdl.SDL_GL_CONTEXT_MINOR_VERSION, value)
        elif attr == 'M64P_GL_CONTEXT_PROFILE_MASK':
            sdl.SDL_GL_SetAttribute(sdl.SDL_GL_CONTEXT_PROFILE_MASK, value)
        else:
            pass

        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def gl_swap_buffer(self):
        #XXX: It can spam this message in the output, better turn off it.
        #log.debug("Vidext: gl_swap_buffer()")
        if self.fullscreen == 1:
            sdl.SDL_GL_SwapWindow(self.fullscreen_window)
        else:
            sdl.SDL_GL_SwapWindow(self.foreign_window)

        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_set_caption(self, title):
        log.debug(f"Vidext: video_set_caption({title.decode('utf-8')})")
        self.title = self.window.get_title()
        self.window.set_title(title.decode("utf-8"))
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_toggle_fs(self):
        log.debug("Vidext: video_toggle_fs()")
        if self.fullscreen == 0:
            # Makes it fullscreen
            self.fullscreen = 1
            # XXX: SDL_WINDOW_FULLSCREEN is a bit overkill, because it changes the desktop's resolution too.
            #self.fullscreen_window = sdl.SDL_CreateWindow(b"Fullscreen", sdl.SDL_WINDOWPOS_UNDEFINED, sdl.SDL_WINDOWPOS_UNDEFINED, 1920, 1080, sdl.SDL_WINDOW_OPENGL)
            self.fullscreen_window = sdl.SDL_CreateWindow(b"Fullscreen", sdl.SDL_WINDOWPOS_UNDEFINED, sdl.SDL_WINDOWPOS_UNDEFINED, self.width, self.height, sdl.SDL_WINDOW_OPENGL)
            sdl.SDL_SetWindowFullscreen(self.fullscreen_window, sdl.SDL_WINDOW_FULLSCREEN_DESKTOP)
            sdl.SDL_GL_MakeCurrent(self.fullscreen_window, self.sdl_context)
        else:
            # Makes the screen back to normal size.
            # FIXME: Investigate why it doesn't set back the resolution
            self.fullscreen = 0
            #sdl.SDL_SetWindowSize(self.fullscreen_window, 1920, 1080)
            sdl.SDL_SetWindowFullscreen(self.fullscreen_window, 0)
            sdl.SDL_GL_MakeCurrent(self.foreign_window, self.sdl_context)
            sdl.SDL_DestroyWindow(self.fullscreen_window)
            #sdl.SDL_SetWindowSize(self.foreign_window, 400, 200)

        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_resize_window(self, width, height):
        #This reacts to the resizing of the window with the cursor
        log.debug("Vidext: video_resize_window(width: {str(width)}, height: {str(height)})")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_get_fb_name(self):
        log.debug("Vidext: video_get_fb_name()")
        return 0


m64p_video = Vidext()
vidext_struct = wrp_dt.m64p_video_extension_functions()
vidext_struct.Functions = 12
vidext_struct.VidExtFuncInit = wrp_dt.vext_init(m64p_video.video_init)
vidext_struct.VidExtFuncQuit = wrp_dt.vext_quit(m64p_video.video_quit)
vidext_struct.VidExtFuncListModes = wrp_dt.vext_list_modes(m64p_video.video_list_modes)
vidext_struct.VidExtFuncSetMode = wrp_dt.vext_set_mode(m64p_video.video_set_mode)
vidext_struct.VidExtFuncGLGetProc = wrp_dt.vext_gl_getproc(m64p_video.gl_get_proc)
vidext_struct.VidExtFuncGLSetAttr = wrp_dt.vext_gl_setattr(m64p_video.gl_set_attr)
vidext_struct.VidExtFuncGLGetAttr = wrp_dt.vext_gl_getattr(m64p_video.gl_get_attr)
vidext_struct.VidExtFuncGLSwapBuf = wrp_dt.vext_gl_swapbuf(m64p_video.gl_swap_buffer)
vidext_struct.VidExtFuncSetCaption = wrp_dt.vext_set_caption(m64p_video.video_set_caption)
vidext_struct.VidExtFuncToggleFS = wrp_dt.vext_toggle_fs(m64p_video.video_toggle_fs)
vidext_struct.VidExtFuncResizeWindow = wrp_dt.vext_resize_window(m64p_video.video_resize_window)
vidext_struct.VidExtFuncGLGetDefaultFramebuffer = wrp_dt.vext_get_default_fb(m64p_video.video_get_fb_name)
    
