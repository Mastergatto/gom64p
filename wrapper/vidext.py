#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
import ctypes as c

#import external.sdl2 as sdl2
import widget.glwidget as w_gl
import wrapper.datatypes as wrp_dt

###############
## VARIABLES ##
###############

#############
## CLASSES ##
#############

class Vidext():
    def __init__(self):
        self.context = None

    def video_init(self):
        print("vidext init")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_quit(self):
        print("vidext quit")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_list_modes(self, sizearray, numsizes):
        print("sizearray:", sizearray, "numsizes", numsizes)
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_set_mode(self, width, height, bits, screenmode, flags):
        print("width:", width, "height:", height, "bits:", bits, "screenmode:", wrp_dt.m64p_video_mode(screenmode).name, "flags:", wrp_dt.m64p_video_flags(flags).name)
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def gl_get_proc(self, proc):
        print("proc:", proc)
        return None

    def gl_get_attr(self, attr, pvalue):
        print("attr:", wrp_dt.m64p_GLattr(attr).name, "pvalue:", pvalue)
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def gl_set_attr(self, attr, value):
        print(wrp_dt.m64p_GLattr(attr).name, value)
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def gl_swap_buffer(self):
        print("buffer swapped")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_set_caption(self, title):
        print("title:", title)
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_toggle_fs(self):
        print("fullscreen toggled")
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value

    def video_resize_window(self, width, height):
        print("width:", width, "height:", height)
        return wrp_dt.m64p_error.M64ERR_SUCCESS.value


m64p_video = Vidext()
vidext_struct = wrp_dt.m64p_video_extension_functions()
vidext_struct.Functions = 0
vidext_struct.VidExtFuncInit = wrp_dt.vext_init(m64p_video.video_init)
vidext_struct.VidExtFuncQuit = wrp_dt.vext_quit(m64p_video.video_quit)
vidext_struct.VidExtFuncListModes = wrp_dt.vext_list_modes(m64p_video.video_list_modes)
vidext_struct.VidExtFuncSetMode = wrp_dt.vext_set_mode(m64p_video.video_set_mode)
vidext_struct.VidExtFuncGLGetProc = wrp_dt.vext_gl_getproc(m64p_video.gl_get_proc)
vidext_struct.VidExtFuncGLSetAttr = wrp_dt.vext_gl_setattr(m64p_video.gl_get_attr)
vidext_struct.VidExtFuncGLGetAttr = wrp_dt.vext_gl_getattr(m64p_video.gl_set_attr)
vidext_struct.VidExtFuncGLSwapBuf = wrp_dt.vext_gl_swapbuf(m64p_video.gl_swap_buffer)
vidext_struct.VidExtFuncSetCaption = wrp_dt.vext_set_caption(m64p_video.video_set_caption)
vidext_struct.VidExtFuncToggleFS = wrp_dt.vext_toggle_fs(m64p_video.video_toggle_fs)
vidext_struct.VidExtFuncResizeWindow = wrp_dt.vext_resize_window(m64p_video.video_resize_window)
    
