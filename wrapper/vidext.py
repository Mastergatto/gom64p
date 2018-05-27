#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
import ctypes as c

import wrapper.datatypes as wrp_dt

###############
## VARIABLES ##
###############

#############
## CLASSES ##
#############

class Vidext():
    def __init__(self):
        self.gl_context = None
        self.window = None

    def render(self, area, context):
        self.gl_context = context
        self.window.canvas = area
        self.window.canvas.do_render(self.gl_context)

    def set_window(self, window):
        self.window = window

    def video_init(self):
        print("Vidext: video_init()")
        self.gl_context = self.window.canvas.get_context()
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_quit(self):
        print("Vidext: video_quit()")
        self.gl_context.clear_current()
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_list_modes(self, sizearray, numsizes):
        print("Vidext: video_list_modes(sizearray:", sizearray, "numsizes", numsizes,")")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_set_mode(self, width, height, bits, screenmode, flags):
        print("Vidext: video_set_mode(width:", width, "height:", height, "bits:", bits, "screenmode:", wrp_dt.m64p_video_mode(screenmode).name, "flags:", wrp_dt.m64p_video_flags(flags).name, ")")
        if self.gl_context != None:
            self.window.canvas.do_resize(self.window.canvas, int(width), int(height))
            return wrp_dt.m64p_error.M64ERR_SUCCESS.value
        else:
            print("video set mode(): Failure")
            return wrp_dt.m64p_error.M64ERR_SYSTEM_FAIL.value

    def gl_get_proc(self, proc):
        print("Vidext: gl_get_proc(", proc.decode(), ")")

    def gl_get_attr(self, attr, pvalue):
        print("Vidext: gl_get_attr(attr:", wrp_dt.m64p_GLattr(attr).name, "pvalue:", pvalue.contents, ")")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def gl_set_attr(self, attr, value):
        print("Vidext: gl_set_attr(attr:", wrp_dt.m64p_GLattr(attr).name, "value:", value, ")")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def gl_swap_buffer(self):
        print("Vidext: gl_swap_buffer()")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_set_caption(self, title):
        print("Vidext: video_set_caption(", title.decode(), ")")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_toggle_fs(self):
        print("Vidext: video_toggle_fs()")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_resize_window(self, width, height):
        print("Vidext: video_resize_window(width:", width, "height:", height, ")")
        self.window.canvas.do_resize(width, height)
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_get_fb_name(self):
        print("Vidext: video_get_fb_name()")
        self.window.canvas.do_render()
        return 0



#TODO: choose better names
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
    
