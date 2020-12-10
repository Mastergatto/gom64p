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

import wrapper.datatypes as wrp_dt

###############
## VARIABLES ##
###############


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

    def __reset_egl(self):
        # (re)set EGL to its initial state
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

        # XXX: OGL 2.0 and compatibility profile as common denominator please every known gfx plugin.
        self.context_major = 2
        self.context_minor = 0
        self.context_profile = 0 # TODO:Not currently used in EGL
        self.api_bit = egl.EGL_OPENGL_BIT
        self.profile_bit = egl.EGL_CONTEXT_OPENGL_COMPATIBILITY_PROFILE_BIT

    def set_window(self, window):
        self.window = window

    # Startup/Shutdown Functions
    def video_init(self):
        '''This function should be called from within the RomOpen() video plugin
        function call. The default SDL implementation of this function simply
        calls SDL_InitSubSystem(SDL_INIT_VIDEO). It does not open a rendering
        window or switch video modes.
        PROTOTYPE:
         m64p_error VidExt_Init(void)'''
        log.debug("Vidext: video_init()")
        
        if self.window.platform == 'Linux':
            #if self.window.environment.wm == 'X11':
            from gi.repository import GdkX11
            self.window_handle = self.window.canvas.get_property('window').get_xid()
            #elif self.window.environment.wm == 'Wayland':
            #    from gi.repository import GdkWayland # No bindings...?
            #    # XXX: It won't work on wayland without forcing GDK_BACKEND=x11, but I can live with that.
            #    self.window_handle = GdkWayland.window_get_wl_surface(self.parent.get_window())
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

        # Reset EGL
        self.__reset_egl()
        
        # Get EGL display
        self.egl_display = egl.eglGetDisplay(egl.EGL_DEFAULT_DISPLAY)
        if self.egl_display == egl.EGL_NO_DISPLAY:
            log.error(f"eglGetDisplay() returned error: {egl.eglGetError()}")
            return wrp_dt.m64p_error.M64ERR_INVALID_STATE.value
        
        # Initialize EGL
        retval = egl.eglInitialize(self.egl_display, c.c_int(0), c.c_int(0))

        # XXX: Required by glide64mk, make EGL know that we want pure OpenGL
        egl.eglBindAPI(egl.EGL_OPENGL_API)
        
        if retval == egl.EGL_TRUE:
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            log.error(f"eglInitialize() returned error: {egl.eglGetError()}")
            return wrp_dt.m64p_error.M64ERR_INVALID_STATE.value

    def video_quit(self):
        '''This function closes any open rendering window and shuts down the
        video system. The default SDL implementation of this function calls
        SDL_QuitSubSystem(SDL_INIT_VIDEO). This function should be called from
        within the RomClosed() video plugin function.
        PROTOTYPE:
         m64p_error VidExt_Quit(void)'''
        log.debug("Vidext: video_quit()")

        # Nullify those EGL variables
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
        
        ## GTK
        # Restore the good old name of the frontend
        if self.title != None:
            self.window.set_title(self.title)
        self.window.set_resizable(True)

        # First we must lift the restriction on the minimum size of the widget
        self.window.canvas.set_size_request(1, 1)

        #XXX: Workaround because GTK is too slow
        time.sleep(0.1)

        self.window.resize(self.former_size[0], self.former_size[1])
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    # Screen Handling Functions
    def video_list_modes(self, sizearray, numsizes):
        '''This function is used to enumerate the available resolutions for
        fullscreen video modes. An array SizeArray is passed into the function,
        which is then filled (up to *'NumSizes' objects) with resolution sizes.
        The number of sizes actually written is stored in the integer which is
        pointed to by NumSizes.
        PROTOTYPE:
         m64p_error VidExt_ListFullscreenModes(m64p_2d_size *SizeArray,
                        int *NumSizes)'''
        log.debug(f"Vidext: video_list_modes(sizearray: {sizearray}, {numsizes}, {numsizes}")

        # Retrieve current desktop resolution and refresh rate
        self.window.environment.get_current_mode()
        mode = self.window.environment.current_mode

        numsizes.contents.value = 1
        sizearray[0].uiWidth = mode.width
        sizearray[0].uiHeight = mode.height
        log.info(f"Vidext: Current mode: {mode.width}x{mode.height}")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_list_rates(self, sizearray, numrates, rates):
        '''This function is used to enumerate the available refresh rates for a
        given resolution. An m64p_2d_size object is passed into the function,
        which will contain the resolution of the refresh rates you want to
        retrieve, an array Rates is passed into the function, which is then
        filled (up to *'NumRates' objects) with resolution sizes.
        The number of sizes actually written is stored in the integer which
        is pointed to by NumSizes.
        PROTOTYPE:
         m64p_error VidExt_ListFullscreenRates(m64p_2d_size Size, int *NumRates,
                        int *Rates)'''
        log.debug(f"Vidext: video_list_rates(sizearray: {sizearray}, {numrates}, {rates}")
        #TODO: Unfinished

        #numrates.contents.value = len(self.rates)
        #for num, rate in enumerate(self.rates):
        #    width, height = mode
        #    sizearray[num].uiWidth = width
        #    sizearray[num].uiHeight = height

        self.window.environment.get_current_mode()
        mode = self.window.environment.current_mode
        numrates.contents.value = 1

        rates[0] = mode['refresh']
        log.info(f"Vidext: Current refresh rate: {rates}")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_set_mode(self, width, height, bits, screenmode, flags, refreshrate=None):
        '''This function creates a rendering window or switches into a
        fullscreen video mode. Any desired OpenGL attributes should be set
        before calling this function.
        PROTOTYPE:
         m64p_error VidExt_SetVideoMode(int Width, int Height, int BitsPerPixel,
                          m64p_video_mode ScreenMode, m64p_video_flags Flags)'''
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
        # XXX: Workaround because GTK is too slow.
        time.sleep(0.1)

        # The window is resizable if gfx plugin allows it
        if flags == wrp_dt.m64p_video_flags.M64VIDEOFLAG_SUPPORT_RESIZING.value:
            self.window.set_resizable(True)
        
        log.debug(f'Double buffer: {self.double_buffer}')
        log.debug(f'Buffer size: {self.buffer_size}')
        log.debug(f'Depth size: {self.depth_size}')
        log.debug(f'Red size: {self.red_size}')
        log.debug(f'Green size: {self.green_size}')
        log.debug(f'Blue size: {self.blue_size}')
        log.debug(f'Alpha size: {self.alpha_size}')
        log.debug(f'Swap control: {self.swap_control}')
        log.debug(f'Multisample buffer: {self.multisample_buffer}')
        log.debug(f'Multisample samples: {self.multisample_samples}')
        log.debug(f'OpenGL: {self.context_major}.{self.context_minor}')
        log.debug(f'Context profile: {self.profile_bit}')

        self.egl_attributes = gl.arrays.GLintArray.asArray([
            egl.EGL_BUFFER_SIZE, self.buffer_size,
            egl.EGL_DEPTH_SIZE, self.depth_size,
            egl.EGL_RED_SIZE, self.red_size,
            egl.EGL_GREEN_SIZE, self.green_size,
            egl.EGL_BLUE_SIZE, self.blue_size,
            egl.EGL_ALPHA_SIZE, self.alpha_size,
            egl.EGL_SAMPLE_BUFFERS, self.multisample_buffer,
            egl.EGL_SAMPLES, self.multisample_samples,
            egl.EGL_RENDERABLE_TYPE, self.api_bit,
            egl.EGL_NONE        
            ])
        
        self.window_attributes = gl.arrays.GLintArray.asArray([
            egl.EGL_RENDER_BUFFER, self.double_buffer,
            egl.EGL_NONE
            ])
        
        self.opengl_version = gl.arrays.GLintArray.asArray([
            egl.EGL_CONTEXT_MAJOR_VERSION, self.context_major,
            egl.EGL_CONTEXT_MINOR_VERSION, self.context_minor,
            egl.EGL_CONTEXT_OPENGL_PROFILE_MASK, self.profile_bit,
            egl.EGL_NONE
        ])
        
        # Return a list of EGL frame buffer configurations that match specified attributes
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
                egl.eglSwapInterval(self.egl_display, self.swap_control)
                egl.eglSwapBuffers(self.egl_display, self.egl_surface)
                retval = True

            except:
                log.error(f"eglMakeCurrent() returned error: {egl.eglGetError()}")
            
            self.new_surface = False
        
        else:
            log.error("VidExtFuncSetMode called before surface has been set");
            return wrp_dt.m64p_error.M64ERR_INVALID_STATE.value

        if retval == True:
            log.debug(f"Vidext: video_set_mode() has reported M64ERR_SUCCESS")
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            log.error(f"Vidext: video_set_mode() has reported M64ERR_SYSTEM_FAIL")
            return wrp_dt.m64p_error.M64ERR_SYSTEM_FAIL.value


    def video_set_mode_rate(self, width, height, refreshrate, bits, screenmode, flags):
        '''This function creates a rendering window or switches into a
        fullscreen video mode. Any desired OpenGL attributes should be set
        before calling this function.
        PROTOTYPE:
         m64p_error VidExt_SetVideoMode(int Width, int Height, int RefreshRate,
            int BitsPerPixel, m64p_video_mode ScreenMode, m64p_video_flags Flags)'''
        log.debug(f"Vidext: video_set_mode_rate(width: {str(width)}, height: {str(height)}, \
                    refresh rate: {str(refreshrate)}, bits: {str(bits)}, screenmode: \
                    {wrp_dt.m64p_video_mode(screenmode).name}, flags:{wrp_dt.m64p_video_flags(flags).name}")

        # TODO: at the moment, it is hardcoded to current display mode
        if (self.window.environment.current_mode.width != width) or (self.window.environment.current_mode.height != height) \
            or (self.window.environment.current_mode.refresh != refreshrate):
            return wrp_dt.m64p_error.M64ERR_UNSUPPORTED.value
        else:
            self.video_set_mode(self, width, height, bits, screenmode, flags, refreshrate)
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_set_caption(self, title):
        '''This function sets the caption text of the emulator rendering window.
        PROTOTYPE:
         m64p_error VidExt_SetCaption(const char *Title)'''
        log.debug(f"Vidext: video_set_caption({title.decode('utf-8')})")
        self.title = self.window.get_title()
        self.window.set_title(title.decode("utf-8"))
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_toggle_fs(self):
        '''This function toggles between fullscreen and windowed rendering modes.
        PROTOTYPE:
          m64p_error VidExt_ToggleFullScreen(void)'''
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
        '''This function is called when the video plugin has resized its OpenGL
        output viewport in response to a ResizeVideoOutput() call, and requests
        that the window manager update the OpenGL rendering window size to match.
        If a front-end application does not support resizable windows and never
        sets the M64CORE_VIDEO_SIZE core variable with the M64CMD_CORE_STATE_SET
        command, then this function should not be called.
        PROTOTYPE:
         m64p_error VidExt_ResizeWindow(int Width, int Height)'''
        # https://github.com/mupen64plus/mupen64plus-core/blob/master/doc/emuwiki-api-doc/Mupen64Plus-v2.0-Core-Video-Extension.mediawiki#window-resizing
        log.debug(f"Vidext: video_resize_window(width: {str(width)}, height: {str(height)})")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def gl_get_proc(self, proc):
        '''This function is used to get a pointer to an OpenGL extension
        function. This is only necessary on the Windows platform, because the
        OpenGL implementation shipped with Windows only supports OpenGL
        version 1.1.
        PROTOTYPE:
         void * VidExt_GL_GetProcAddress(const char* Proc)'''
        address = egl.eglGetProcAddress(proc)
        if address is not None:
            return address
        else:
            log.error(f"Vidext: gl_get_proc({proc.decode()}) returns None")

    def gl_get_attr(self, attr, pvalue):
        '''This function may be used to check that OpenGL attributes where
        successfully set to the rendering window after the VidExt_SetVideoMode
        function call.
        PROTOTYPE:
         m64p_error VidExt_GL_GetAttribute(m64p_GLattr Attr, int *pValue)'''
        log.debug(f"Vidext: gl_get_attr(attr:{wrp_dt.m64p_GLattr(attr).name}, pvalue:{str(pvalue.contents.value)})")

        pointer = c.pointer(c.c_int())
        if attr == wrp_dt.m64p_GLattr.M64P_GL_DOUBLEBUFFER.value:
            #value = ogl.glGetIntegerv(ogl.GL_DOUBLEBUFFER, pointer)
            value = egl.eglQueryContext(self.egl_display, self.egl_context, egl.EGL_RENDER_BUFFER, pointer)
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_BUFFER_SIZE.value:
            value = egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_BUFFER_SIZE, pointer)
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_DEPTH_SIZE.value:
            value = egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_DEPTH_SIZE, pointer)
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_RED_SIZE.value:
            value = egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_RED_SIZE, pointer)
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_GREEN_SIZE.value:
            value = egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_GREEN_SIZE, pointer)
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_BLUE_SIZE.value:
            value = egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_BLUE_SIZE, pointer)
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_ALPHA_SIZE.value:
            value = egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_ALPHA_SIZE, pointer)
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_SWAP_CONTROL.value:
            # TODO: Is this attribute the right one?
            value = egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_MIN_SWAP_INTERVAL, pointer)
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_MULTISAMPLEBUFFERS.value:
            value = egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_SAMPLE_BUFFERS, pointer)
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_MULTISAMPLESAMPLES.value:
            value = egl.eglGetConfigAttrib(self.egl_display, self.egl_config[0], egl.EGL_SAMPLES, pointer)
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_CONTEXT_MAJOR_VERSION.value:
            try:
                value = ogl.glGetIntegerv(ogl.GL_MAJOR_VERSION, pointer)
            except:
                # OGL 2.1 or less is not compatible with glGetIntegerv
                value = c.pointer(c.c_int(2))
            #egl.eglQueryContext(self.egl_display, self.egl_context, egl.EGL_CONTEXT_MAJOR_VERSION, pointer)
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_CONTEXT_MINOR_VERSION.value:
            try:
                value = ogl.glGetIntegerv(ogl.GL_MINOR_VERSION, pointer)
            except:
                # OGL 2.1 or less is not compatible with glGetIntegerv
                value = c.pointer(c.c_int(0))
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_CONTEXT_PROFILE_MASK.value:
            # OpenGL context profile is introduced in 3.2
            if self.context_major >= 3 and self.context_minor >= 2:
                # TODO: How to get the exact version of the context profile?
                value = ogl.glGetIntegerv(ogl.GL_CONTEXT_PROFILE_MASK, pointer)
                #egl.eglQueryContext(self.egl_display, self.egl_context, egl.EGL_CONTEXT_MAJOR_VERSION, pointer)
            else:
                # TODO: What's the value in case the gfx plugin doesn't support OGL 3.2+? Zero?
                value = pvalue.contents.value
        else:
            log.warning("gom64p doesn't know how to handle {attr}")

        query = pointer.contents.value
        if  query == pvalue.contents.value:
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            log.error(f"Vidext: gl_get_attr() has reported M64ERR_SYSTEM_FAIL, for {wrp_dt.m64p_GLattr(attr).name} was expected {pvalue.contents.value} but it returned {query}")
            return wrp_dt.m64p_error.M64ERR_INVALID_STATE.value

    def gl_set_attr(self, attr, value):
        '''This function is used to set certain OpenGL attributes which must be
        specified before creating the rendering window with VidExt_SetVideoMode.
        PROTOTYPE:
         m64p_error VidExt_GL_SetAttribute(m64p_GLattr Attr, int Value)'''
        log.debug(f"Vidext.gl_set_attr(): attr '{str(attr)}'; value '{str(value)}'")
        retval = 0

        if attr == wrp_dt.m64p_GLattr.M64P_GL_DOUBLEBUFFER.value:
            if value == 0:
                self.double_buffer = egl.EGL_SINGLE_BUFFER
            elif value == 1:
                self.double_buffer = egl.EGL_BACK_BUFFER
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_BUFFER_SIZE.value:
            self.buffer_size = value
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_DEPTH_SIZE.value:
            self.depth_size = value
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_RED_SIZE.value:
            self.red_size = value
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_GREEN_SIZE.value:
            self.green_size = value
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_BLUE_SIZE.value:
            self.blue_size = value
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_ALPHA_SIZE.value:
            self.alpha_size = value
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_SWAP_CONTROL.value:
            self.swap_control = value
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_MULTISAMPLEBUFFERS.value:
            self.multisample_buffer = value
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_MULTISAMPLESAMPLES.value:
            self.multisample_samples = value
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_CONTEXT_MAJOR_VERSION.value:
            self.context_major = value
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_CONTEXT_MINOR_VERSION.value:
            self.context_minor = value
        elif attr == wrp_dt.m64p_GLattr.M64P_GL_CONTEXT_PROFILE_MASK.value:
            if value == wrp_dt.m64p_GLContextType.M64P_GL_CONTEXT_PROFILE_CORE.value:
                egl.eglBindAPI(egl.EGL_OPENGL_API)
                self.api_bit = egl.EGL_OPENGL_BIT
                self.profile_bit = egl.EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT
                pointer = c.pointer(c.c_int())
                ogl.glGetIntegerv(ogl.GL_CONTEXT_PROFILE_MASK, pointer)
                self.context_profile = pointer.contents.value
            elif value == wrp_dt.m64p_GLContextType.M64P_GL_CONTEXT_PROFILE_COMPATIBILITY.value:
                egl.eglBindAPI(egl.EGL_OPENGL_API)
                self.api_bit = egl.EGL_OPENGL_BIT
                self.profile_bit = egl.EGL_CONTEXT_OPENGL_COMPATIBILITY_PROFILE_BIT
                self.context_profile = pointer.contents.value
            elif value == wrp_dt.m64p_GLContextType.M64P_GL_CONTEXT_PROFILE_ES.value:
                egl.eglBindAPI(egl.EGL_OPENGL_ES_API)
                self.api_bit = egl.EGL_OPENGL_ES2_BIT
                # TODO: Is this correct?
                self.profile_bit = egl.EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT
        else:
            log.warning(f"Vidext: gom64p doesn't know how to handle {attr}")

        if retval == 0:
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            log.error(f"Vidext: gl_set_attr() has reported M64ERR_SYSTEM_FAIL, tried to set {value} for {attr}, but it returned error")
            return wrp_dt.m64p_error.M64ERR_SYSTEM_FAIL.value

    def gl_swap_buffer(self):
        ''' This function is used to swap the front/back buffers after rendering
        an output video frame.
        PROTOTYPE:
          m64p_error VidExt_GL_SwapBuffers(void)'''
        # Note: It can spam the message in the logs, it's best to never turn it on.
        #log.debug("Vidext: gl_swap_buffer()")
        if self.new_surface:
            log.info("VidExtFuncGLSwapBuf: New surface has been detected")
            self.egl_surface = egl.eglCreateWindowSurface(self.egl_display, self.egl_config[0], self.window_handle, self.window_attributes)
            
            try:
                egl.eglMakeCurrent(self.egl_display, self.egl_surface, self.egl_surface, self.egl_context)
                egl.eglSwapBuffers(self.egl_display, self.egl_surface)
            except:
                log.error(f"eglMakeCurrent() returned error: {egl.eglGetError()}")
            
            self.new_surface = False
        else:
            if self.window.running == True:
                egl.eglSwapBuffers(self.egl_display, self.egl_surface)

        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_get_fb_name(self):
        '''On some platforms (for instance, iOS) the default framebuffer object
        depends on the surface being rendered to, and might be different from 0.
        This function should be called to retrieve the name of the default FBO.
        Calling this function may have performance implications and it should
        not be called every time the default FBO is bound.
        PROTOTYPE:
          uint32_t VidExt_GL_GetDefaultFramebuffer(void)'''
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
    
