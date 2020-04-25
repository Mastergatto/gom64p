#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
import ctypes as c
from gi.repository import Gtk
import sys, time
import logging as log
import OpenGL as gl
import OpenGL.GL as ogl
import OpenGL.EGL as egl

#import sdl2 as sdl
import wrapper.datatypes as wrp_dt

###############
## VARIABLES ##
###############

# self.info = sdl.SDL_SysWMinfo()
# version = sdl.SDL_GetVersion(c.byref(self.info.version))
# self.window_info = sdl.SDL_GetWindowWMInfo(self.foreign_window, c.byref(self.info))
# if self.info.subsystem == sdl.SDL_SYSWM_X11:
#     log.debug("The OS is Linux, using X11")
    #TODO: How to get to info.x11.window?
#     log.debug(repr(self.info))
# elif self.info.subsystem == sdl.SDL_SYSWM_WAYLAND:
#     log.debug("The OS is Linux, using Wayland")
# elif self.info.subsystem == sdl.SDL_SYSWM_WINDOWS:
#     log.debug("The OS is Windows")
# elif self.info.subsystem == sdl.SDL_SYSWM_COCOA:
#     log.debug("The OS is Mac OS X")

#############
## CLASSES ##
#############

class Vidext():
    def __init__(self):
        self.window = None
        self.title = None
        self.height = None
        self.width = None

        self.modes = []
        self.former_size = None

    def reset(self):
        self.egl_attributes = None
        self.window_attributes = None
        
        self.egl_display = egl.EGL_NO_DISPLAY
        self.egl_config = None
        self.egl_context = egl.EGL_NO_CONTEXT
        self.egl_surface = egl.EGL_NO_SURFACE
        self.new_surface = True

        # OpenGL visual format
        self.double_buffer = egl.EGL_BACK_BUFFER
        self.buffer_size = egl.EGL_DONT_CARE
        self.depth_size = egl.EGL_DONT_CARE
        self.red_size = egl.EGL_DONT_CARE
        self.green_size = egl.EGL_DONT_CARE
        self.blue_size = egl.EGL_DONT_CARE
        self.alpha_size = egl.EGL_DONT_CARE
        self.swap_control = egl.EGL_DONT_CARE
        self.multisample_buffer = egl.EGL_DONT_CARE
        self.multisample_samples = egl.EGL_DONT_CARE

        self.context_major = 3
        self.context_minor = 0
        self.profile_mask = egl.EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT

    def set_window(self, window):
        self.window = window

    def video_init(self):
        log.debug("Vidext: video_init()")
        #sdl.SDL_InitSubSystem(sdl.SDL_INIT_VIDEO)
        #sdl.SDL_InitSubSystem(sdl.SDL_INIT_JOYSTICK) #TODO: Is it really necessary?

        #source: https://github.com/mupen64plus/mupen64plus-ui-python/blob/master/src/m64py/core/vidext.py#L34
        #display = sdl.SDL_DisplayMode()
        #for mode in range(sdl.SDL_GetNumDisplayModes(0)):
        #    ret = sdl.SDL_GetDisplayMode(0, mode, c.byref(display))
        #    if (display.w, display.h) not in self.modes:
        #        self.modes.append((display.w, display.h))

        #log.debug(self.modes)

        # Mandatory since we're doing the hack for embedding SDL into GTK+, otherwise gamepads won't work here since GTK+ doesn't handle those inputs.
        #sdl.SDL_SetHint(sdl.SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, b"1")
        
        
        if self.window.platform == 'Linux':
            from gi.repository import GdkX11
            # Hack to embed sdl window into the frontend.
            # XXX: It won't work on wayland without forcing GDK_BACKEND=x11, but I can live with that.
            self.window_handle = self.window.canvas.get_property('window').get_xid()
            # for wayland maybe use gdk_wayland_surface_get_window_geometry + gdk_surface_get_geometry?
        elif self.window.platform == 'Windows':
            # https://stackoverflow.com/questions/23021327/how-i-can-get-drawingarea-window-handle-in-gtk3/27236258#27236258
            # https://gitlab.gnome.org/GNOME/gtk/issues/510
            drawingareahwnd = self.window.canvas.get_property("window")
            # make sure to call ensure_native before e.g. on realize
            if not drawingareahwnd.has_native():
                log.warning("Vidext: Your window is gonna freeze as soon as you move or resize it...")
            c.pythonapi.PyCapsule_GetPointer.restype = c.c_void_p
            c.pythonapi.PyCapsule_GetPointer.argtypes = [c.py_object]
            drawingarea_gpointer = c.pythonapi.PyCapsule_GetPointer(drawingareahwnd.__gpointer__, None)
            # get the win32 handle
            libgdk = c.CDLL("gdk-3-vs16.dll")
            self.window_handle = libgdk.gdk_win32_window_get_handle(drawingarea_gpointer)
        elif self.window.platform == 'Darwin':
            # https://gitlab.gnome.org/GNOME/pygobject/issues/112
            drawingareahnd = self.window.canvas.get_property("window")
            # make sure to call ensure_native before e.g. on realize
            if not drawingareahnd.has_native():
                log.warning("Vidext: Your window is gonna freeze as soon as you move or resize it...")
            c.pythonapi.PyCapsule_GetPointer.restype = c.c_void_p
            c.pythonapi.PyCapsule_GetPointer.argtypes = [c.py_object]
            gpointer = c.pythonapi.PyCapsule_GetPointer(drawingareahnd.__gpointer__, None)
            libgdk = c.CDLL ("libgdk-3.0.dylib")
            #gdk_quartz_window_get_nswindow segfaults.
            libgdk.gdk_quartz_window_get_nsview.restype = c.c_void_p
            libgdk.gdk_quartz_window_get_nsview.argtypes = [c.c_void_p]
            self.window_handle = libgdk.gdk_quartz_window_get_nsview(gpointer)

        self.reset()
        
        self.egl_display = egl.eglGetDisplay(egl.EGL_DEFAULT_DISPLAY)
        if self.egl_display == egl.EGL_NO_DISPLAY:
            log.error(f"eglGetDisplay() returned error: {egl.eglGetError()}")
            return wrp_dt.m64p_error.M64ERR_INVALID_STATE.value
        
        retval = egl.eglInitialize(self.egl_display, c.c_int(0), c.c_int(0))
        #what about ES?
        egl.eglBindAPI(egl.EGL_OPENGL_API)
        
        if retval == egl.EGL_TRUE:
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            log.error(f"eglInitialize() returned error: {egl.eglGetError()}")
            return wrp_dt.m64p_error.M64ERR_INVALID_STATE.value

    def video_quit(self):
        log.debug("Vidext: video_quit()")

        if self.egl_context != egl.EGL_NO_CONTEXT:
            egl.eglDestroyContext(self.egl_display, self.egl_context)
            self.egl_context = egl.EGL_NO_CONTEXT

        egl.eglMakeCurrent(self.egl_display, egl.EGL_NO_SURFACE, egl.EGL_NO_SURFACE, egl.EGL_NO_CONTEXT)
        if self.egl_surface != egl.EGL_NO_SURFACE:
            egl.eglDestroySurface(self.egl_display, self.egl_surface)
            self.egl_surface = egl.EGL_NO_SURFACE

        if self.egl_display != egl.EGL_NO_DISPLAY:
            egl.eglTerminate(self.egl_display)
            self.egl_display = egl.EGL_NO_DISPLAY  
            
        self.new_surface = True     
        
        if self.title != None:
            self.window.set_title(self.title)
        self.window.set_resizable(True)
        self.window.canvas.set_size_request(1, 1) # First we must lift the restriction on the minimum size of the widget

        time.sleep(0.1) #XXX: Workaround because GTK is too slow
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
            log.info(f"Vidext: {mode}: {width}x{height}")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_list_rates(self, sizearray, numrates, rates):
        log.debug(f"Vidext: video_list_rates(sizearray: {sizearray}, {numrates}, {rates}")
        #numrates.contents.value = len(self.rates)
        #for num, rate in enumerate(self.rates):
        #    width, height = mode
        #    sizearray[num].uiWidth = width
        #    sizearray[num].uiHeight = height
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_set_mode(self, width, height, bits, screenmode, flags):
        log.debug(f"Vidext: video_set_mode(width: {str(width)}, height: {str(height)}, bits: {str(bits)}, screenmode: {wrp_dt.m64p_video_mode(screenmode).name}, flags:{wrp_dt.m64p_video_flags(flags).name}")

        self.width = width
        self.height = height

        self.former_size = self.window.get_size()
        # Needed for get_preferred_size() to work
        self.window.set_resizable(False)
        # It doesn't just get the preferred size, it DOES resize the window too
        self.window.canvas.get_preferred_size()
        # Necessary so that we tell the GUI to not shrink the window further than the size of the widget set by mupen64plus
        self.window.canvas.set_size_request(width, height)
        time.sleep(0.1) # XXX: Workaround because GTK is too slow.

        if wrp_dt.m64p_video_flags(flags).name == "M64VIDEOFLAG_SUPPORT_RESIZING":
            self.window.set_resizable(True)
        
        #print(self.double_buffer, self.buffer_size, self.depth_size, self.red_size, self.green_size, self.blue_size, self.alpha_size, self.swap_control, self.multisample_buffer, self.multisample_samples, self.context_major, self.context_minor, self.profile_mask)
        self.egl_attributes = gl.arrays.GLintArray.asArray([
            egl.EGL_BUFFER_SIZE, self.buffer_size,
            egl.EGL_DEPTH_SIZE, self.depth_size,
            egl.EGL_RED_SIZE, self.red_size,
            egl.EGL_GREEN_SIZE, self.green_size,
            egl.EGL_BLUE_SIZE, self.blue_size,
            egl.EGL_ALPHA_SIZE, self.alpha_size,
            egl.EGL_SAMPLE_BUFFERS, self.multisample_buffer,
            egl.EGL_SAMPLES, self.multisample_samples,
            egl.EGL_RENDERABLE_TYPE, self.profile_mask,
            egl.EGL_NONE        
            ])
        
        self.window_attributes = gl.arrays.GLintArray.asArray([
            egl.EGL_RENDER_BUFFER, self.double_buffer,
            egl.EGL_NONE
            ])
        
        self.opengl_version = gl.arrays.GLintArray.asArray([
            egl.EGL_CONTEXT_MAJOR_VERSION, self.context_major,
            egl.EGL_CONTEXT_MINOR_VERSION, self.context_minor,
            egl.EGL_CONTEXT_OPENGL_PROFILE_MASK, self.profile_mask,
            egl.EGL_NONE
        ])
        
        num_configs = c.c_long()
        self.egl_config = (egl.EGLConfig*2)()
        config_chosen = egl.eglChooseConfig(self.egl_display, self.egl_attributes, self.egl_config, 2, num_configs)
        if config_chosen == None:
            log.error(f"eglChooseConfig() returned error: {egl.eglGetError()}")
            return wrp_dt.m64p_error.M64ERR_INVALID_STATE.value
        
        if self.new_surface:
            log.info("VidExtFuncSetMode: Initializing surface")
            self.egl_surface = egl.eglCreateWindowSurface(self.egl_display, self.egl_config[0], self.window_handle, self.window_attributes)
            
            self.egl_context = egl.eglCreateContext(self.egl_display, self.egl_config[0], egl.EGL_NO_CONTEXT, self.opengl_version)
        
            if self.egl_context == egl.EGL_NO_CONTEXT:
                raise RuntimeError( 'Unable to create context' )
            try:
                egl.eglMakeCurrent(self.egl_display, self.egl_surface, self.egl_surface, self.egl_context)
                egl.eglSwapBuffers(self.egl_display, self.egl_surface)

            except:
                log.error(f"eglMakeCurrent() returned error: {egl.eglGetError()}")
            
            self.new_surface = False
        
        else:
            log.error("VidExtFuncSetMode called before surface has been set");

        retval = True

        #log.debug(f"video_set_mode context: {context}")
        if retval == True:
            log.debug(f"Vidext: video_set_mode() has reported M64ERR_SUCCESS")
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            log.error(f"Vidext: video_set_mode() has reported M64ERR_SYSTEM_FAIL")
            return wrp_dt.m64p_error.M64ERR_SYSTEM_FAIL.value


    def video_set_mode_rate(self, width, height, refreshrate, bits, screenmode, flags):
        log.debug(f"Vidext: video_set_mode_Rate(width: {str(width)}, height: {str(height)}, \
                    refresh rate: {str(refreshrate)}, bits: {str(bits)}, screenmode: \
                    {wrp_dt.m64p_video_mode(screenmode).name}, flags:{wrp_dt.m64p_video_flags(flags).name}")

        return wrp_dt.m64p_error.M64ERR_UNSUPPORTED


    def gl_get_proc(self, proc):
        address = egl.eglGetProcAddress(proc)
        if address is not None:
            return address
        else:
            log.error(f"Vidext: gl_get_proc({proc.decode()}) returns None")

    def gl_get_attr(self, attr, pvalue):
        attr = wrp_dt.m64p_GLattr(attr).name
        log.debug(f"Vidext: gl_get_attr(attr:{attr}, pvalue:{str(pvalue.contents.value)})")
        retval = 0

        if attr == 'M64P_GL_DOUBLEBUFFER':
            #self.double_buffer = pvalue.contents.value
            pass
        elif attr == 'M64P_GL_BUFFER_SIZE':
            egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_BUFFER_SIZE, pvalue)
        elif attr == 'M64P_GL_DEPTH_SIZE':
            egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_DEPTH_SIZE, pvalue)
        elif attr == 'M64P_GL_RED_SIZE':
            egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_RED_SIZE, pvalue)
        elif attr == 'M64P_GL_GREEN_SIZE':
            egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_GREEN_SIZE, pvalue)
        elif attr == 'M64P_GL_BLUE_SIZE':
            egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_BLUE_SIZE, pvalue)
        elif attr == 'M64P_GL_ALPHA_SIZE':
            egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_ALPHA_SIZE, pvalue)
        elif attr == 'M64P_GL_SWAP_CONTROL':
            #self.swap_control = pvalue.contents.value
            pass
        elif attr == 'M64P_GL_MULTISAMPLEBUFFERS':
            egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_SAMPLE_BUFFERS, pvalue)
        elif attr == 'M64P_GL_MULTISAMPLESAMPLES':
            egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_SAMPLES, pvalue)
        elif attr == 'M64P_GL_CONTEXT_MAJOR_VERSION':
            #self.context_major = pvalue.contents.value
            ogl.glGetIntegerv(ogl.GL_MAJOR_VERSION, pvalue)
        elif attr == 'M64P_GL_CONTEXT_MINOR_VERSION':
            #self.context_minor = pvalue.contents.value
            ogl.glGetIntegerv(ogl.GL_MINOR_VERSION, pvalue)
        elif attr == 'M64P_GL_CONTEXT_PROFILE_MASK':
            #self.profile_mask = pvalue.contents.value
            ogl.glGetIntegerv(ogl.GL_CONTEXT_PROFILE_MASK, pvalue)
        else:
            log.warning("gom64p doesn't know how to handle {attr}")

        if retval == 0:
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            log.error(f"Vidext: gl_get_attr() has reported M64ERR_SYSTEM_FAIL, tried to set {pvalue.contents.value} for {attr}, but it returned error")
            return wrp_dt.m64p_error.M64ERR_SYSTEM_FAIL.value

    def gl_set_attr(self, attr, value):
        attr = wrp_dt.m64p_GLattr(attr).name
        log.debug(f"Vidext.gl_set_attr(): attr '{str(attr)}'; value '{str(value)}'")
        retval = 0

        if attr == 'M64P_GL_DOUBLEBUFFER':
            if value == 0:
                self.double_buffer = egl.EGL_SINGLE_BUFFER
            elif value == 1:
                self.double_buffer = egl.EGL_BACK_BUFFER
        elif attr == 'M64P_GL_BUFFER_SIZE':
            self.buffer_size = value
        elif attr == 'M64P_GL_DEPTH_SIZE':
            self.depth_size = value
        elif attr == 'M64P_GL_RED_SIZE':
            self.red_size = value
        elif attr == 'M64P_GL_GREEN_SIZE':
            self.green_size = value
        elif attr == 'M64P_GL_BLUE_SIZE':
            self.blue_size = value
        elif attr == 'M64P_GL_ALPHA_SIZE':
            self.alpha_size = value
        elif attr == 'M64P_GL_SWAP_CONTROL':
            self.swap_control = value
        elif attr == 'M64P_GL_MULTISAMPLEBUFFERS':
            self.multisample_buffer = value
        elif attr == 'M64P_GL_MULTISAMPLESAMPLES':
            self.multisample_samples = value
        elif attr == 'M64P_GL_CONTEXT_MAJOR_VERSION':
            self.context_major = value
        elif attr == 'M64P_GL_CONTEXT_MINOR_VERSION':
            self.context_minor = value
        elif attr == 'M64P_GL_CONTEXT_PROFILE_MASK':
            if value == wrp_dt.m64p_GLContextType.M64P_GL_CONTEXT_PROFILE_CORE.value:
                egl.eglBindAPI(egl.EGL_OPENGL_API)
                #self.profile_mask = egl.EGL_OPENGL_BIT
                self.profile_mask = egl.EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT
            elif value == wrp_dt.m64p_GLContextType.M64P_GL_CONTEXT_PROFILE_COMPATIBILITY.value:
                egl.eglBindAPI(egl.EGL_OPENGL_API)
                #self.profile_mask = egl.EGL_OPENGL_BIT
                self.profile_mask = egl.EGL_CONTEXT_OPENGL_COMPATIBILITY_PROFILE_BIT
            elif value == wrp_dt.m64p_GLContextType.M64P_GL_CONTEXT_PROFILE_ES.value:
                egl.eglBindAPI(egl.EGL_OPENGL_ES_API)
                self.profile_mask = egl.EGL_OPENGL_ES2_BIT   
        else:
            log.warning(f"Vidext: gom64p doesn't know how to handle {attr}")

        if retval == 0:
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            log.error(f"Vidext: gl_set_attr() has reported M64ERR_SYSTEM_FAIL, tried to set {value} for {attr}, but it returned error")
            return wrp_dt.m64p_error.M64ERR_SYSTEM_FAIL.value

    def gl_swap_buffer(self):
        #XXX: It can spam this message in the output, better turn off it.
        #log.debug("Vidext: gl_swap_buffer()")
        if self.new_surface:
            log.info("VidExtFuncGLSwapBuf: New surface has been detected")
            self.egl_surface = egl.eglCreateWindowSurface(self.egl_display, self.egl_config[0], self.window_handle, self.window_attributes)
            
            try:
                egl.eglMakeCurrent(self.egl_display, self.egl_surface, self.egl_surface, self.egl_context)
                #egl.eglSwapBuffers(self.egl_display, self.egl_surface)
            except:
                log.error(f"eglMakeCurrent() returned error: {egl.eglGetError()}")
            
            self.new_surface = False
        else:
            if self.window.running == True:
                egl.eglSwapBuffers(self.egl_display, self.egl_surface)

        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_set_caption(self, title):
        log.debug(f"Vidext: video_set_caption({title.decode('utf-8')})")
        self.title = self.window.get_title()
        self.window.set_title(title.decode("utf-8"))
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_toggle_fs(self):
        retval = 0      
        if self.window.isfullscreen == True:
            log.debug("Vidext: video_toggle_fs() set to fullscreen")

        else:
            log.debug("Vidext: video_toggle_fs() set to windowed")

        if retval == 0:
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            log.error(f"Vidext: video_toggle_fs() has reported M64ERR_SYSTEM_FAIL: \n > {egl.eglGetError()}")
            return wrp_dt.m64p_error.M64ERR_SYSTEM_FAIL.value

    def video_resize_window(self, width, height):
        #This reacts to the resizing of the window with the cursor
        log.debug(f"Vidext: video_resize_window(width: {str(width)}, height: {str(height)})")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_get_fb_name(self):
        log.debug("Vidext: video_get_fb_name() returns 0 as name")
        return 0
    

m64p_video = Vidext()
vidext_struct = wrp_dt.m64p_video_extension_functions()
vidext_struct.Functions = 14

def enable_vidext():
    vidext_struct.VidExtFuncInit = wrp_dt.vext_init(m64p_video.video_init)
    vidext_struct.VidExtFuncQuit = wrp_dt.vext_quit(m64p_video.video_quit)
    vidext_struct.VidExtFuncListModes = wrp_dt.vext_list_modes(m64p_video.video_list_modes)
    vidext_struct.VidExtFuncListRates = wrp_dt.vext_list_rates(m64p_video.video_list_rates)
    vidext_struct.VidExtFuncSetMode = wrp_dt.vext_set_mode(m64p_video.video_set_mode)
    vidext_struct.VidExtFuncSetModeWithRate = wrp_dt.vext_set_mode_rate(m64p_video.video_set_mode_rate)
    vidext_struct.VidExtFuncGLGetProc = wrp_dt.vext_gl_getproc(m64p_video.gl_get_proc)
    vidext_struct.VidExtFuncGLSetAttr = wrp_dt.vext_gl_setattr(m64p_video.gl_set_attr)
    vidext_struct.VidExtFuncGLGetAttr = wrp_dt.vext_gl_getattr(m64p_video.gl_get_attr)
    vidext_struct.VidExtFuncGLSwapBuf = wrp_dt.vext_gl_swapbuf(m64p_video.gl_swap_buffer)
    vidext_struct.VidExtFuncSetCaption = wrp_dt.vext_set_caption(m64p_video.video_set_caption)
    vidext_struct.VidExtFuncToggleFS = wrp_dt.vext_toggle_fs(m64p_video.video_toggle_fs)
    vidext_struct.VidExtFuncResizeWindow = wrp_dt.vext_resize_window(m64p_video.video_resize_window)
    vidext_struct.VidExtFuncGLGetDefaultFramebuffer = wrp_dt.vext_get_default_fb(m64p_video.video_get_fb_name)

def disable_vidext():
    vidext_struct.Functions = 14
    vidext_struct.VidExtFuncInit = wrp_dt.vext_init(0)
    vidext_struct.VidExtFuncQuit = wrp_dt.vext_quit(0)
    vidext_struct.VidExtFuncListModes = wrp_dt.vext_list_modes(0)
    vidext_struct.VidExtFuncListRates = wrp_dt.vext_list_rates(0)
    vidext_struct.VidExtFuncSetMode = wrp_dt.vext_set_mode(0)
    vidext_struct.VidExtFuncSetModeWithRate = wrp_dt.vext_set_mode_rate(0)
    vidext_struct.VidExtFuncGLGetProc = wrp_dt.vext_gl_getproc(0)
    vidext_struct.VidExtFuncGLSetAttr = wrp_dt.vext_gl_setattr(0)
    vidext_struct.VidExtFuncGLGetAttr = wrp_dt.vext_gl_getattr(0)
    vidext_struct.VidExtFuncGLSwapBuf = wrp_dt.vext_gl_swapbuf(0)
    vidext_struct.VidExtFuncSetCaption = wrp_dt.vext_set_caption(0)
    vidext_struct.VidExtFuncToggleFS = wrp_dt.vext_toggle_fs(0)
    vidext_struct.VidExtFuncResizeWindow = wrp_dt.vext_resize_window(0)
    vidext_struct.VidExtFuncGLGetDefaultFramebuffer = wrp_dt.vext_get_default_fb(0)
    
