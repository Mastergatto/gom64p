#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
import ctypes as c
from gi.repository import Gtk, GdkX11
import sys
from OpenGL.GL import *

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
        self.sdl_window = None
        self.title = None

        self.modes = []
        self.renderer = None
        self.framebuffer = 0
        self.fullscreen = 0
        self.former_size = None
        self.profile_mask = None

    def set_window(self, window):
        self.window = window

    def video_init(self):
        print("Vidext: video_init()")
        #source: https://github.com/mupen64plus/mupen64plus-ui-python/blob/master/src/m64py/core/vidext.py#L34
        sdl.SDL_InitSubSystem(sdl.SDL_INIT_VIDEO)
        sdl.SDL_InitSubSystem(sdl.SDL_INIT_JOYSTICK) #TODO: Is it really necessary?
        display = sdl.SDL_DisplayMode()
        for mode in range(sdl.SDL_GetNumDisplayModes(0)):
            ret = sdl.SDL_GetDisplayMode(0, mode, c.byref(display))
            if (display.w, display.h) not in self.modes:
                self.modes.append((display.w, display.h))

        print(self.modes)
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_quit(self):
        print("Vidext: video_quit()")
        sdl.SDL_GL_DeleteContext(self.sdl_context)
        sdl.SDL_DestroyWindow(self.foreign_window)
        sdl.SDL_Quit()
        if self.title != None:
            self.window.set_title(self.title)
        self.window.set_resizable(True)
        self.window.canvas.set_size_request(1, 1) # First we must lift the restriction on the minimum size of the widget
        self.window.resize(self.former_size[0], self.former_size[1])
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_list_modes(self, sizearray, numsizes):
        print("Vidext: video_list_modes(sizearray:", sizearray, "numsizes", numsizes,")")
        # source: https://github.com/mupen64plus/mupen64plus-ui-python/blob/master/src/m64py/core/vidext.py#L80
        numsizes.contents.value = len(self.modes)
        for num, mode in enumerate(self.modes):
            width, height = mode
            sizearray[num].uiWidth = width
            sizearray[num].uiHeight = height
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_set_mode(self, width, height, bits, screenmode, flags):
        print("Vidext: video_set_mode(width:" + str(width) + ", height:" + str(height) + ", bits:" + str(bits) +
               ", screenmode:" + wrp_dt.m64p_video_mode(screenmode).name + ", flags:" + wrp_dt.m64p_video_flags(flags).name + ")")

        self.former_size = self.window.get_size()
        self.window.set_resizable(False) # Needed for get_preferred_size() to work
        self.window.canvas.set_size_request(width, height) # Necessary so that we tell the GUI to not shrink the window further than the size of the widget set by mupen64plus
        self.window.canvas.get_preferred_size() # It doesn't just get the preferred size, it DOES resize the window too

        if sys.platform.startswith('linux') or sys.platform.startswith('freebsd') :
            # Hack to embed sdl window into the frontend. It won't work on wayland without forcing GDK_BACKEND=x11, but I can live with that.
            self.foreign_window = sdl.SDL_CreateWindowFrom(self.window.canvas.get_property('window').get_xid())
        elif sys.platform == 'cygwin':
            #sdl.SDL_HINT_VIDEO_WINDOW_SHARE_PIXEL_FORMAT(x)
            #self.foreign_window = sdl.SDL_CreateWindowFrom(self.window.canvas.get_property('window').get_xid())
            pass
        elif sys.platform == 'darwin':
            pass

        self.sdl_context = sdl.SDL_GL_CreateContext(self.foreign_window)
        #print(sdl.SDL_GetError())
        sdl.SDL_GL_MakeCurrent(self.foreign_window, self.sdl_context)

        print("video_set_mode context:", self.sdl_context)
        if self.sdl_context != None:
            self.sdl_context2 = sdl.SDL_GL_GetCurrentContext()
            print("Context SDL:", self.sdl_context, self.sdl_context2)

            self.info = sdl.SDL_SysWMinfo()
            #version = sdl.SDL_VERSION(c.byref(info.version))
            version = sdl.SDL_GetVersion(c.byref(self.info.version))
            self.window_info = sdl.SDL_GetWindowWMInfo(self.sdl_window, c.byref(self.info))
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
            print("Vidext: video_set_mode() has reported M64ERR_SYSTEM_FAIL")
            return wrp_dt.m64p_error.M64ERR_SYSTEM_FAIL.value

    def gl_get_proc(self, proc):
        address = sdl.SDL_GL_GetProcAddress(proc)
        if address is not None:
            return address
        else:
            print("Vidext: gl_get_proc(" + proc.decode() + ") returns None")

    def gl_get_attr(self, attr, pvalue):
        attr = wrp_dt.m64p_GLattr(attr).name
        print("Vidext: gl_get_attr(attr:" + attr + ", pvalue:" + str(pvalue.contents.value) + ")")
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
            self.profile_mask = pvalue.contents.value
            value = sdl.SDL_GL_GetAttribute(sdl.SDL_GL_CONTEXT_PROFILE_MASK, pvalue)
        else:
            pass

        if value == pvalue.contents.value:
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            print("Vidext: gl_get_attr() has reported M64ERR_SYSTEM_FAIL, value is", value)
            return wrp_dt.m64p_error.M64ERR_SYSTEM_FAIL.value

    def gl_set_attr(self, attr, value):
        attr = wrp_dt.m64p_GLattr(attr).name
        print("Vidext: gl_set_attr(attr: "+ str(attr) + ", value:" + str(value) + ")")

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
        #print("Vidext: gl_swap_buffer()")
        sdl.SDL_GL_SwapWindow(self.foreign_window)

        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_set_caption(self, title):
        print("Vidext: video_set_caption(" + title.decode("utf-8") + ")")
        self.title = self.window.get_title()
        self.window.set_title(title.decode("utf-8"))
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_toggle_fs(self):
        print("Vidext: video_toggle_fs()")
        if self.fullscreen == 0:
            self.fullscreen = 1
            # XXX: SDL_WINDOW_FULLSCREEN is a bit overkill, because it changes the desktop's resolution too.
            sdl.SDL_SetWindowFullscreen(self.sdl_window, sdl.SDL_WINDOW_FULLSCREEN_DESKTOP)
        else:
            self.fullscreen = 0
            sdl.SDL_SetWindowFullscreen(self.sdl_window, 0)

        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_resize_window(self, width, height):
        #This reacts to the resizing of the window with the cursor
        print("Vidext: video_resize_window(width:" + str(width) + "height:" + str(height) + ")")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_get_fb_name(self):
        print("Vidext: video_get_fb_name()")
        self.framebuffer = glGetIntegerv(GL_FRAMEBUFFER_BINDING)
        print("SDL framebuffer is:", self.framebuffer)
        return self.framebuffer


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
    
