#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

import sys, pathlib, binascii, platform
import ctypes as c

import wrapper.callback as wrp_cb
import wrapper.datatypes as wrp_dt
import wrapper.vidext as wrp_vext
import global_module as g

class API():
    """Wrapper for calling libmupen64plus.so's functions into python code"""
    def __init__(self, params):
        #Latest API version supported by this wrapper.
        self.core_version = 0x020509 # 2.5.9 BETA

        self.m64p_lib_core_path = params['m64plib']
        self.plugins_dir = params['pluginsdir']
        self.frontend_api_version = params['api_version']
        self.compatible = False
        self.vext_override = False
        self.current_slot = 0
        self.media_loader = wrp_cb.MEDIA_LOADER

        configpath = params['configdir'].encode('utf-8')
        if configpath != b'':
            self.config_dir = configpath
        else:
            self.config_dir = None

        datapath = params['datadir'].encode('utf-8')
        if datapath != b'':
            self.data_dir = datapath
        else:
            self.data_dir = None

        #self.core_filename = "libmupen64plus.so.2.0.0" #LINUX ONLY
        self.gfx_filename = params['gfx']
        self.audio_filename = params['audio']
        self.input_filename = params['input']
        self.rsp_filename = params['rsp']

        self.gfx_plugins = {}
        self.audio_plugins = {}
        self.input_plugins = {}
        self.rsp_plugins = {}

        # Initialize those empty structures
        self.rom_header = wrp_dt.m64p_rom_header()
        self.rom_settings = wrp_dt.m64p_rom_settings()

        # We must check first if plugins, all that are found, are compatible
        self.plugins_validate()

        self.config_handle = None
        self.config_ext_handle = None


        #CORE_API_VERSION = 0x20001
        #CONFIG_API_VERSION = 0x20000
        #MINIMUM_CORE_VERSION = 0x016300

        #MUPEN_CORE_NAME "Mupen64Plus Core"
        #MUPEN_CORE_VERSION 0x020501
        #FRONTEND_API_VERSION 0x020102
        #CONFIG_API_VERSION   0x020301
        #DEBUG_API_VERSION    0x020001
        #VIDEXT_API_VERSION   0x030100

        #RSP_API_VERSION   0x20000
        #GFX_API_VERSION   0x20200
        #AUDIO_API_VERSION 0x20000
        #INPUT_API_VERSION 0x20001

    ### Basic core functions
    def PluginGetVersion(self, plugin):
        #m64p_error PluginGetVersion(m64p_plugin_type *PluginType, int *PluginVersion, int *APIVersion, const char **PluginNamePtr, int *Capabilities)
        info = {}

        plugintype = c.c_int()
        pluginversion = c.c_int()
        apiversion = c.c_int()
        pluginpointer = c.c_char_p()
        capabilities = c.c_int()

        function = wrp_dt.cfunc("PluginGetVersion", plugin, wrp_dt.m64p_error,
                   ("PluginType", c.POINTER(c.c_int), 2, plugintype),
                   ("PluginVersion", c.POINTER(c.c_int), 2, pluginversion),
                   ("APIVersion", c.POINTER(c.c_int), 2, apiversion),
                   ("PluginNamePtr", c.POINTER(c.c_char_p), 2, pluginpointer),
                   ("Capabilities", c.POINTER(c.c_int), 2, capabilities))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            info = {"type": plugintype.value, "version": pluginversion.value,
                    "apiversion": apiversion.value, "name": pluginpointer.value.decode(),
                    "capabilities": capabilities.value}
            return info
        else:
            self.CoreErrorMessage(status, b"PluginGetVersion")

    def CoreGetAPIVersions(self):
        #m64p_error CoreGetAPIVersions(int *ConfigVersion, int *DebugVersion, int *VidextVersion, int *ExtraVersion)
        info = {}

        configversion = c.c_int()
        debugversion = c.c_int()
        vidextversion = c.c_int()
        extraversion = c.c_int()

        function = wrp_dt.cfunc("CoreGetAPIVersions", self.m64p_lib_core, wrp_dt.m64p_error,
                         ("ConfigVersion", c.POINTER(c.c_int), 2, configversion),
                         ("DebugVersion", c.POINTER(c.c_int), 2, debugversion),
                         ("VidextVersion", c.POINTER(c.c_int), 2, vidextversion),
                         ("ExtraVersion", c.POINTER(c.c_int), 2, extraversion))
        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            info = {"config": configversion.value, "debug": debugversion.value,
                    "vidext": vidextversion.value, "extra": extraversion.value}
            return info
        else:
            self.CoreErrorMessage(status, b"CoreGetAPIVersions")

    def CoreErrorMessage(self, ReturnCode, context=None):
        #const char * CoreErrorMessage(m64p_error ReturnCode)

        function = wrp_dt.cfunc("CoreErrorMessage", self.m64p_lib_core, c.c_char_p,
                        ("ReturnCode", c.c_int, 1, c.c_int(ReturnCode)))
        status = function()

        if context != None:
            print("ERROR(" + c.cast(context, c.c_char_p).value.decode("utf-8") + "):", status.decode("utf-8"))
        else:
            print("ERROR: ", status)

    ### Frontend functions
    ## Startup/Shutdown
    def CoreStartup(self, version):
        #m64p_error CoreStartup(int APIVersion, const char *ConfigPath, const char *DataPath, void *Context, void (*DebugCallback)(void *Context, int level, const char *message), void *Context2, void (*StateCallback)(void *Context2, m64p_core_param ParamChanged, int NewValue))

        function = wrp_dt.cfunc("CoreStartup", self.m64p_lib_core, wrp_dt.m64p_error,
                   ("APIVersion", c.c_int, 1, version),
                   ("ConfigPath", c.c_char_p, 1, c.c_char_p(self.config_dir)),
                   ("DataPath", c.c_char_p, 1, c.c_char_p(self.data_dir)),
                   ("Context", c.c_void_p, 1, c.cast(b"Debug", c.c_void_p)),
                   ("DebugCallback", c.c_void_p , 2, wrp_cb.CB_DEBUG),
                   ("Context2", c.c_void_p, 1, c.cast(b"State", c.c_void_p)),
                   ("StateCallback", c.c_void_p , 2, g.CB_STATE))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"CoreStartup")

    def CoreShutdown(self):
        #m64p_error CoreShutdown(void)
        function = wrp_dt.cfunc("CoreShutdown", self.m64p_lib_core, wrp_dt.m64p_error)

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"CoreShutdown")

    def CoreAttachPlugin(self, plugin, handle):
        #m64p_error CoreAttachPlugin(m64p_plugin_type PluginType, m64p_dynlib_handle PluginLibHandle)
        #Plugins must be attached in this order (Video, audio, input, rsp)
        function = wrp_dt.cfunc("CoreAttachPlugin", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("PluginType", c.c_int, 1, plugin),
                        ("PluginLibHandle", c.c_void_p, 1, wrp_dt.m64p_dynlib_handle(handle)))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, wrp_dt.m64p_plugin_type(plugin).name.encode("utf-8"))

    def CoreDetachPlugin(self, plugin):
        #m64p_error CoreDetachPlugin(m64p_plugin_type PluginType)
        function = wrp_dt.cfunc("CoreDetachPlugin", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("PluginType", c.c_int, 1, plugin))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, wrp_dt.m64p_plugin_type(plugin).name.encode("utf-8"))

    ## Command
    def CoreDoCommand(self, command, arg1=None, arg2=None):
        #m64p_error CoreDoCommand(m64p_command Command, int ParamInt, void *ParamPtr)
        print(wrp_dt.m64p_command(command).name)
        function = wrp_dt.cfunc("CoreDoCommand", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("Command", c.c_int, 1, command),
                        ("ParamInt", c.c_int, 1, arg1),
                        ("ParamPtr", c.c_void_p, 2, arg2))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, wrp_dt.m64p_command(command).name.encode("utf-8"))

    ## ROM Handling
    def CoreGetRomSettings(self, crc1, crc2):
        #m64p_error CoreGetRomSettings(m64p_rom_settings *RomSettings, int RomSettingsLength, int Crc1, int Crc2)
        #XXX: For the CRCs base 16 must be specified, with int(x, 16)
        #XXX: a pointer has been added to RomSettingsLength even though the prototype
        #     doesn't theoretically require it, because otherwise it will complain with INVALID_INPUT.
        rom_settings = wrp_dt.m64p_rom_settings()

        crc1b = int(crc1, 16)
        crc2b = int(crc2, 16)

        function = wrp_dt.cfunc("CoreGetRomSettings", self.m64p_lib_core, wrp_dt.m64p_error,
                   ("RomSettings", c.POINTER(wrp_dt.m64p_rom_settings), 2, c.byref(rom_settings)),
                   ("RomSettingsLength", c.POINTER(c.c_int), 2, c.pointer(c.c_int(c.sizeof(rom_settings)))),
                   ("Crc1", c.c_int, 1, c.c_int(crc1b)),
                   ("Crc2", c.c_int, 1, c.c_int(crc2b)))
        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return rom_settings
        else:
            self.CoreErrorMessage(status, b"CoreGetRomSettings")

    ## Video Extension
    def CoreOverrideVidExt(self):
        #m64p_error CoreOverrideVidExt(m64p_video_extension_functions *VideoFunctionStruct);
        function = wrp_dt.cfunc("CoreOverrideVidExt", self.m64p_lib_core, wrp_dt.m64p_error,
                       ("VideoFunctionStruct", c.POINTER(wrp_dt.m64p_video_extension_functions), 2, c.byref(wrp_vext.vidext_struct)))
        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"CoreOverrideVidExt")

    ## Cheat
    def CoreAddCheat(self, cheatname, codelist, numcodes):
        #m64p_error CoreAddCheat(const char *CheatName, m64p_cheat_code *CodeList, int NumCodes)
        #TODO: Untested
        function = wrp_dt.cfunc("CoreAddCheat", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("CheatName", c.c_char_p, 1, cheatname.encode("utf-8")),
                        ("CodeList", c.pointer(wrp_dt.m64p_cheat_code), 1, c.byref(codelist())),
                        ("NumCodes", c.c_int, 1, c.c_int(numcodes)))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"CoreAddCheat")

    def CoreCheatEnabled(self, cheatname, enabled):
        #m64p_error CoreCheatEnabled(const char *CheatName, int Enabled)
        #TODO: Untested
        function = wrp_dt.cfunc("CoreCheatEnabled", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("CheatName", c.c_char_p, 1, cheatname.encode("utf-8")),
                        ("Enabled", c.c_int, 1, c.c_int(enabled)))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"CoreCheatEnabled")

    ### Video Extension
    ### XXX: Those functions aren't intended to be used by frontend, but rather to help with vidext implementation

    ## Startup/Shutdown
    def VidExt_Init(self):
        #m64p_error VidExt_Init(void)
        #WARNING: Not for use
        function = wrp_dt.cfunc("VidExt_Init", self.m64p_lib_core, wrp_dt.m64p_error)

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_Init")

    def VidExt_Quit(self):
        #m64p_error VidExt_Quit(void)
        #WARNING: Not for use
        function = wrp_dt.cfunc("VidExt_Quit", self.m64p_lib_core, wrp_dt.m64p_error)

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_Quit")

    ## Screen Handling
    def VidExt_ListFullscreenModes(self):
        #m64p_error VidExt_ListFullscreenModes(m64p_2d_size *SizeArray, int *NumSizes)
        #WARNING: Not for use
        function = wrp_dt.cfunc("VidExt_ListFullscreenModes", self.m64p_lib_core, wrp_dt.m64p_error,
                       ("SizeArray", c.POINTER(wrp_dt.m64p_2d_size), 2, c.byref(wrp_dt.m64p_2d_size())),
                       ("NumSizes", c.POINTER(c.c_int), 2, c.c_int()))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_ListFullscreenModes")

    def VidExt_SetVideoMode(self, width, height, bits, screenmode, flags):
        #m64p_error VidExt_SetVideoMode(int Width, int Height, int BitsPerPixel, m64p_video_mode ScreenMode, m64p_video_flags Flags)
        #WARNING: Not for use
        function = wrp_dt.cfunc("VidExt_SetVideoMode", self.m64p_lib_core, wrp_dt.m64p_error,
                       ("Width", c.c_int, 1, c.c_int(width)),
                       ("Height", c.c_int, 1, c.c_int(height)),
                       ("BitsPerPixel", c.c_int, 1, c.c_int(bits)),
                       ("ScreenMode", c.c_int, 1, c.c_int(wrp_dt.m64p_video_mode(screenmode))),
                       ("Flags", c.c_int, 1, c.c_int(wrp_dt.m64p_video_flags(flags))))


        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_SetVideoMode")

    def VidExt_SetCaption(self, title):
        #m64p_error VidExt_SetCaption(const char *Title)
        #WARNING: Not for use
        function = wrp_dt.cfunc("VidExt_SetCaption", self.m64p_lib_core, wrp_dt.m64p_error,
                       ("Title", c.c_char_p, 1, title.encode("utf-8")))


        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_SetCaption")

    def VidExt_ToggleFullScreen(self):
        #m64p_error VidExt_ToggleFullScreen(void)
        #WARNING: Not for use
        function = wrp_dt.cfunc("VidExt_ToggleFullScreen", self.m64p_lib_core, wrp_dt.m64p_error)


        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_ToggleFullScreen")

    def VidExt_ResizeWindow(self, width, height):
        #m64p_error VidExt_ResizeWindow(int Width, int Height)
        #WARNING: Not for use
        function = wrp_dt.cfunc("VidExt_ResizeWindow", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("Width", c.c_int, 1, c.c_int(width)),
                        ("Height", c.c_int, 1, c.c_int(height)))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_ResizeWindow")

    ## OpenGL
    def VidExt_GL_GetProcAddress(self, proc):
        #void * VidExt_GL_GetProcAddress(const char* Proc)
        function = wrp_dt.cfunc("VidExt_GL_GetProcAddress", self.m64p_lib_core, wrp_dt.m64p_function,
                        ("Proc", c.c_char_p, 1, proc.encode("utf-8")))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        #if status == m64p_error.M64ERR_SUCCESS.value:
        #    return status
        #else:
        #    print(self.CoreErrorMessage(status, b"VidExt_GL_GetProcAddress"))

    def VidExt_GL_SetAttribute(self, attr, value):
        #m64p_error VidExt_GL_SetAttribute(m64p_GLattr Attr, int Value)
        function = wrp_dt.cfunc("VidExt_GL_SetAttribute", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("Attr", c.c_int, c.c_int(wrp_dt.m64p_GLattr(attr))),
                        ("Value", c.c_int, 1, c.c_int(value)))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_GL_SetAttribute")

    def VidExt_GL_GetAttribute(self, attr, pvalue):
        #m64p_error VidExt_GL_GetAttribute(m64p_GLattr Attr, int *pValue)
        function = wrp_dt.cfunc("VidExt_GL_GetAttribute", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("Attr", c.c_int, c.c_int(wrp_dt.m64p_GLattr(attr))),
                        ("pValue", c.POINTER(c.c_int), 1, c.byref(c.c_int(pvalue))))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_GL_GetAttribute")

    def VidExt_GL_SwapBuffers(self):
        #m64p_error VidExt_GL_SwapBuffers(void)
        function = wrp_dt.cfunc("VidExt_GL_SwapBuffers", self.m64p_lib_core, wrp_dt.m64p_error)


        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_GL_SwapBuffers")

    ### Debugger
    ## General
    def DebugSetCallbacks(self):
        #m64p_error DebugSetCallbacks(void (*dbg_frontend_init)(void), void (*dbg_frontend_update)(unsigned int pc), void (*dbg_frontend_vi)(void))
        #TODO: Untested

        frontend_init = wrp_dt.cfunc("dbg_frontend_init", self.m64p_lib_core, c.c_void_p)

        frontend_update = wrp_dt.cfunc("dbg_frontend_update", self.m64p_lib_core, c.c_void_p,
                                ("pc", c.c_uint, 1))
        frontend_vi = wrp_dt.cfunc("dbg_frontend_vi", self.m64p_lib_core, c.c_void_p)


        function = wrp_dt.cfunc("DebugSetCallbacks", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("dbg_frontend_init", c.c_void_p, 1, frontend_init),
                        ("dbg_frontend_update", c.c_void_p, 1, frontend_update),
                        ("dbg_frontend_vi", c.c_void_p, 1, frontend_vi))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"DebugSetCallbacks")

    def DebugSetCoreCompare(self):
        #m64p_error DebugSetCoreCompare(void (*dbg_core_compare)(unsigned int), void (*dbg_core_data_sync)(int, void *))
        #TODO: Untested
        core_compare = c.CFUNCTYPE(c.c_void_p, c.c_uint)

        core_data_sync = c.CFUNCTYPE(c.c_void_p, c.c_int, c.c_void_p)


        function = wrp_dt.cfunc("DebugSetCoreCompare", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("dbg_core_compare", c.c_void_p, 1, core_compare),
                        ("dbg_core_data_sync", c.c_void_p, 1, core_data_sync))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"DebugSetCoreCompare")

    def DebugSetRunState(self):
        #m64p_error DebugSetRunState(int runstate)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugSetRunState", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("runstate", c.c_int, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"DebugSetRunState")

    def DebugGetState(self):
        #int DebugGetState(m64p_dbg_state statenum)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugGetState", self.m64p_lib_core, c.c_int,
                        ("statenum", wrp_dt.m64p_dbg_state, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugStep(self):
        #m64p_error DebugStep(void)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugStep", self.m64p_lib_core, wrp_dt.m64p_error)

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"DebugStep")

    def DebugDecodeOp(self):
        #void DebugDecodeOp(unsigned int instruction, char *op, char *args, int pc)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugDecodeOp", self.m64p_lib_core, None,
                        ("instruction", c.c_uint, 1),
                        ("op", c.POINTER(c.c_char), 1),
                        ("args", c.POINTER(c.c_char), 1),
                        ("pc", c.c_int, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    ## Memory
    def DebugMemGetRecompInfo(self):
        #void * DebugMemGetRecompInfo(m64p_dbg_mem_info recomp_type, unsigned int address, int index)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugMemGetRecompInfo", self.m64p_lib_core, c.c_void_p,
                        ("recomp_type", wrp_dt.m64p_dbg_mem_info, 1),
                        ("address", c.c_uint, 1),
                        ("index", c.c_int, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemGetMemInfo(self):
        #int DebugMemGetMemInfo(m64p_dbg_mem_info mem_info_type, unsigned int address)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugMemGetMemInfo", self.m64p_lib_core, c.c_int,
                        ("mem_info_type", wrp_dt.m64p_dbg_mem_info, 1),
                        ("address", c.c_uint, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemGetPointer(self):
        #void * DebugMemGetPointer(m64p_dbg_memptr_type mem_ptr_type)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugMemGetPointer", self.m64p_lib_core, c.c_void_p,
                        ("mem_ptr_type", wrp_dt.m64p_dbg_memptr_type, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemRead64(self, address):
        #unsigned long long DebugMemRead64(unsigned int address)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugMemRead64", self.m64p_lib_core, c.c_ulonglong,
                        ("address", c.c_uint, 1, address))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemRead32(self, address):
        #unsigned int DebugMemRead32(unsigned int address)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugMemRead32", self.m64p_lib_core, c.c_uint,
                        ("address", c.c_uint, 1, address))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemRead16(self, address):
        #unsigned short DebugMemRead16(unsigned int address)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugMemRead16", self.m64p_lib_core, c.c_ushort,
                        ("address", c.c_uint, 1, address))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function(self)

    def DebugMemRead8(self, address):
        #unsigned char DebugMemRead8(unsigned int address)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugMemRead8", self.m64p_lib_core, c.c_ubyte,
                        ("address", c.c_uint, 1, address))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemWrite64(self, address, value):
        #void DebugMemWrite64(unsigned int address, unsigned long long value)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugMemWrite64", self.m64p_lib_core, None,
                        ("address", c.c_uint, 1, address),
                        ("value", c.c_ulonglong, 1, value))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemWrite32(self, address, value):
        #void DebugMemWrite32(unsigned int address, unsigned int value)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugMemWrite32", self.m64p_lib_core, None,
                        ("address", c.c_uint, 1, address),
                        ("value", c.c_uint, 1, value))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemWrite16(self, address, value):
        #void DebugMemWrite16(unsigned int address, unsigned short value)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugMemWrite16", self.m64p_lib_core, None,
                        ("address", c.c_uint, 1, address),
                        ("value", c.c_ushort, 1, value))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemWrite8(self, address, value):
        #void DebugMemWrite8(unsigned int address, unsigned char value)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugMemWrite8", self.m64p_lib_core, None,
                        ("address", c.c_uint, 1, address),
                        ("value", c.c_ubyte, 1, value))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    ## R4300 CPU
    def DebugGetCPUDataPtr(self):
        #void *DebugGetCPUDataPtr(m64p_dbg_cpu_data cpu_data_type)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugGetCPUDataPtr", self.m64p_lib_core, c.c_void_p,
                        ("cpu_data_type", wrp_dt.m64p_dbg_cpu_data, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    ## Breakpoint
    def DebugBreakpointLookup(self):
        #int DebugBreakpointLookup(unsigned int address, unsigned int size, unsigned int flags)
        #TODO: Untested
        function = wrp_dt.cfunc("DebugBreakpointLookup", self.m64p_lib_core, c.c_int,
                        ("address", c.c_uint, 1),
                        ("size", c.c_uint, 1),
                        ("flags", c.c_uint, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugBreakpointCommand(self):
        #int DebugBreakpointCommand(m64p_dbg_bkp_command command, unsigned int index, m64p_breakpoint *bkp)
        # M64P_BKP_CMD_ADD_ADDR
        # M64P_BKP_CMD_ADD_STRUCT
        # M64P_BKP_CMD_REPLACE
        # M64P_BKP_CMD_REMOVE_ADDR
        # M64P_BKP_CMD_REMOVE_IDX
        # M64P_BKP_CMD_ENABLE
        # M64P_BKP_CMD_DISABLE
        # M64P_BKP_CMD_CHECK
        #TODO: Untested
        function = wrp_dt.cfunc("DebugBreakpointCommand", self.m64p_lib_core, c.c_int,
                        ("command", wrp_dt.m64p_dbg_bkp_command, 1),
                        ("index", c.c_uint, 1),
                        ("bkp", c.POINTER(wrp_dt.m64p_breakpoint), 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugBreakpointTriggeredBy(self):
        #void DebugBreakpointTriggeredBy(uint32_t *flags, uint32_t *accessed)
        #TODO: Untested, https://github.com/mupen64plus/mupen64plus-core/blob/b4f43dbeb028d71f8af14547e26e5f862d295552/doc/emuwiki-api-doc/Mupen64Plus-v2.0-Core-Debugger.mediawiki
        function = wrp_dt.cfunc("DebugBreakpointTriggeredBy", self.m64p_lib_core, c.c_void_p,
                                ("flags", c.POINTER(c.c_uint), 1),
                                ("accessed", c.POINTER(c.c_uint), 1))
        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugVirtualToPhysical(self):
        #uint32_t DebugVirtualToPhysical(uint32_t address)
        #TODO: Untested, https://github.com/mupen64plus/mupen64plus-core/blob/b4f43dbeb028d71f8af14547e26e5f862d295552/doc/emuwiki-api-doc/Mupen64Plus-v2.0-Core-Debugger.mediawiki
        function = wrp_dt.cfunc("DebugVirtualToPhysical", self.m64p_lib_core, c.c_uint,
                                ("address", c.c_uint, 1))
        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    ### Configuration
    ## Selector functions
    def ConfigListSections(self):
        #m64p_error ConfigListSections(void *context, void (*SectionListCallback)(void * context, const char * SectionName))

        function = wrp_dt.cfunc("ConfigListSections", self.m64p_lib_core, wrp_dt.m64p_error,
                   ("context", c.c_void_p, 1, c.cast(b"Sections", c.c_void_p)),
                   ("SectionListCallback", c.c_void_p, 2, wrp_cb.CB_SECTIONS))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigListSections")

    def ConfigOpenSection(self, section):
        #m64p_error ConfigOpenSection(const char *SectionName, m64p_handle *ConfigSectionHandle)

        wrp_cb.section_cb = section

        wrp_cb.parameters[wrp_cb.section_cb] = {}

        handle = c.c_void_p()

        function = wrp_dt.cfunc("ConfigOpenSection", self.m64p_lib_core, wrp_dt.m64p_error,
                   ("SectionName", c.c_char_p, 1, section.encode("utf-8")),
                   ("ConfigSectionHandle", c.c_void_p, 2, c.byref(handle)))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            self.config_handle = handle.value
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigListSections")

    def ConfigListParameters(self):
        #m64p_error ConfigListParameters(m64p_handle ConfigSectionHandle, void *context, void (*ParameterListCallback)(void * context, const char *ParamName, m64p_type ParamType))

        function = wrp_dt.cfunc("ConfigListParameters", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("context", c.c_void_p, 1, c.cast(b"Parameters", c.c_void_p)),
                        ("ParameterListCallback", c.c_void_p, 2, wrp_cb.CB_PARAMETERS))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigListParameters")

    def ConfigHasUnsavedChanges(self, section):
        #int ConfigHasUnsavedChanges(const char *SectionName)
        function = wrp_dt.cfunc("ConfigHasUnsavedChanges", self.m64p_lib_core, c.c_int,
                   ("SectionName", c.c_char_p, 1, section.encode("utf-8")))

        #function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == 1:
            print(section + ": Changes detected!")
            return True
        else:
            print(section + ": No unsaved changes. Move along, nothing to see here.")
            return False

    ## Modifier functions
    def ConfigDeleteSection(self, section):
        #m64p_error ConfigDeleteSection(const char *SectionName)

        function = wrp_dt.cfunc("ConfigDeleteSection", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("SectionName", c.c_char_p, 1, section.encode("utf-8")))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigDeleteSection")

    def ConfigSaveFile(self):
        #m64p_error ConfigSaveFile(void)

        function = wrp_dt.cfunc("ConfigSaveFile", self.m64p_lib_core, wrp_dt.m64p_error)

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigSaveFile")

    def ConfigSaveSection(self, section):
        #m64p_error ConfigSaveSection(const char *SectionName)

        function = wrp_dt.cfunc("ConfigSaveSection", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("SectionName", c.c_char_p, 1, section.encode("utf-8")))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigSaveSection")

    def ConfigRevertChanges(self, section):
        #m64p_error ConfigRevertChanges(const char *SectionName)

        function = wrp_dt.cfunc("ConfigRevertChanges", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("SectionName", c.c_char_p, 1, section.encode("utf-8")))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigRevertChanges")

    ## Generic Get/Set Functions
    def ConfigSetParameter(self, name, paramvalue):
        #m64p_error ConfigSetParameter(m64p_handle ConfigSectionHandle, const char *ParamName, m64p_type ParamType, const void *ParamValue)
        #TODO: Check if there are memory corruption

        param_type = self.ConfigGetParameterType(name)
        #param_type = wrp_dt.m64p_type(param_result)

        paramvalue_type = None
        if param_type == 'M64TYPE_INT':
            paramvalue = c.byref(c.c_int(paramvalue))
            paramvalue_type = c.POINTER(c.c_int)
        elif param_type == 'M64TYPE_FLOAT':
            paramvalue = c.byref(c.c_float(paramvalue))
            paramvalue_type = c.POINTER(c.c_float)
        elif param_type == 'M64TYPE_BOOL':
            paramvalue = c.byref(c.c_bool(paramvalue))
            paramvalue_type = c.POINTER(c.c_bool)
        elif param_type == 'M64TYPE_STRING':
            # c_char_p
            paramvalue = paramvalue.encode("utf-8")
            paramvalue_type = c.c_char_p

        function = wrp_dt.cfunc("ConfigSetParameter", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("ConfigSectionHandle", c.c_void_p, 2, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")),
                        ("ParamType", c.c_int, 1, wrp_dt.m64p_type[param_type].value),
                        ("ParamValue", paramvalue_type, 1, paramvalue))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigSetParameter")

    def ConfigSetParameterHelp(self, name, help):
        #m64p_error ConfigSetParameterHelp(m64p_handle ConfigSectionHandle, const char *ParamName, const char *ParamHelp)

        function = wrp_dt.cfunc("ConfigSetParameterHelp", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("ConfigSectionHandle", c.c_void_p, 2, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")),
                        ("ParamHelp", c.c_char_p, 1, help.encode("utf-8")))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigSetParameterHelp")

    def ConfigGetParameter(self, name):
        #m64p_error ConfigGetParameter(m64p_handle ConfigSectionHandle, const char *ParamName, m64p_type ParamType, void *ParamValue, int MaxSize)
        #TODO: Check if there are memory corruptions.

        param_type = self.ConfigGetParameterType(name)
        param_result = wrp_dt.m64p_type[param_type].value

        paramvalue = None
        if param_type == 'M64TYPE_INT':
            maxsize = c.sizeof(c.c_int(param_result))
            paramvalue = c.pointer(c.c_int())
        elif param_type == 'M64TYPE_FLOAT':
            maxsize = c.sizeof(c.c_float(param_result))
            paramvalue = c.pointer(c.c_float())
        elif param_type == 'M64TYPE_BOOL':
            maxsize = c.sizeof(c.c_int(param_result)) #c_int to avoid INPUT_INVALID
            paramvalue = c.pointer(c.c_bool())
        elif param_type == 'M64TYPE_STRING':
            maxsize = 256
            paramvalue = c.create_string_buffer(maxsize)
        else:
            print("ConfigGetParameter: Unknown parameter type")

        function = wrp_dt.cfunc("ConfigGetParameter", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("ConfigSectionHandle", c.c_void_p, 2, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")),
                        ("ParamType", c.c_int, 1, param_result),
                        ("ParamValue", c.c_void_p, 1, paramvalue),
                        ("MaxSize", c.c_int, 1, maxsize))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            if param_type == 'M64TYPE_STRING':
                #print(paramvalue.value)
                return paramvalue.value.decode()
            else:
                #print(paramvalue.contents.value)
                return paramvalue.contents.value
        else:
            self.CoreErrorMessage(status, b"ConfigGetParameter")

    def ConfigExternalOpen(self, path):
        # m64p_error ConfigExternalOpen(const char *FileName, m64p_handle *Handle)

        handle = c.c_void_p()
        function = wrp_dt.cfunc("ConfigExternalOpen", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("FileName", c.c_char_p, 1, path.encode("utf-8")),
                        ("Handle", c.c_void_p, 1, c.byref(handle)))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            self.config_ext_handle = handle.value
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigExternalOpen")

    def ConfigExternalClose(self):
        # m64p_error ConfigExternalClose(m64p_handle Handle)

        function = wrp_dt.cfunc("ConfigExternalClose", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("Handle", c.c_void_p, 1, self.config_ext_handle))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigExternalClose")

    def ConfigExternalGetParameter(self, sectionname, paramname):
        # m64p_error ConfigExternalGetParameter(m64p_handle Handle, const char *SectionName, const char *ParamName, char* ParamPtr, int ParamMaxLength)

        maxlenght = 256
        paramptr = c.create_string_buffer(maxlenght)

        function = wrp_dt.cfunc("ConfigExternalGetParameter", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("Handle", c.c_void_p, 1, self.config_ext_handle),
                        ("SectionName", c.c_char_p, 1, sectionname.encode("utf-8")),
                        ("ParamName", c.c_char_p, 1,  paramname.encode("utf-8")),
                        ("ParamPtr", c.c_char_p, 2, paramptr),
                        ("ParamMaxLength", c.c_int, 1, c.c_int(maxlenght)))
        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return paramptr.value
        else:
            self.CoreErrorMessage(status, b"ConfigExternalGetParameter")

    def ConfigGetParameterType(self, paramname):
        #m64p_error ConfigGetParameterType(m64p_handle ConfigSectionHandle, const char *ParamName, m64p_type *ParamType)

        param_type = c.c_int()
        function = wrp_dt.cfunc("ConfigGetParameterType", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("ConfigSectionHandle", c.c_void_p, 2, self.config_handle),
                        ("ParamName", c.c_char_p, 1, paramname.encode("utf-8")),
                        ("ParamType", c.POINTER(c.c_int), 2, param_type))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return wrp_dt.m64p_type(param_type.value).name
        else:
            self.CoreErrorMessage(status, b"ConfigGetParameterType")

    def ConfigGetParameterHelp(self, name):
        #const char * ConfigGetParameterHelp(m64p_handle ConfigSectionHandle, const char *ParamName)
        function = wrp_dt.cfunc("ConfigGetParameterHelp", self.m64p_lib_core, c.c_char_p,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")))

        status = function()

        if status != None:
            return status.decode("utf-8")
        else:
            print("No description is available for this parameter: ", name)

    ##Special Get/Set Functions
    def ConfigSetDefaultInt(self, name, value, help):
        #m64p_error ConfigSetDefaultInt(m64p_handle ConfigSectionHandle, const char *ParamName, int ParamValue, const char *ParamHelp)

        function = wrp_dt.cfunc("ConfigSetDefaultInt", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")),
                        ("ParamValue", c.c_int, 1, value),
                        ("ParamHelp", c.c_char_p, 1, help.encode("utf-8")))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigSetDefaultInt")

    def ConfigSetDefaultFloat(self, name, value, help):
        #m64p_error ConfigSetDefaultFloat(m64p_handle ConfigSectionHandle, const char *ParamName, float ParamValue, const char *ParamHelp)

        function = wrp_dt.cfunc("ConfigSetDefaultFloat", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")),
                        ("ParamValue", c.c_float, 1, value),
                        ("ParamHelp", c.c_char_p, 1, help.encode("utf-8")))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigSetDefaultFloat")

    def ConfigSetDefaultBool(self, name, value, help):
        #m64p_error ConfigSetDefaultBool(m64p_handle ConfigSectionHandle, const char *ParamName, int ParamValue, const char *ParamHelp)

        function = wrp_dt.cfunc("ConfigSetDefaultBool", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")),
                        ("ParamValue", c.c_int, 1, value),
                        ("ParamHelp", c.c_char_p, 1, help.encode("utf-8")))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigSetDefaultBool")

    def ConfigSetDefaultString(self, name, value, help):
        #m64p_error ConfigSetDefaultString(m64p_handle ConfigSectionHandle, const char *ParamName, const char * ParamValue, const char *ParamHelp)

        function = wrp_dt.cfunc("ConfigSetDefaultString", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")),
                        ("ParamValue", c.c_char_p, 1, value.encode("utf-8")),
                        ("ParamHelp", c.c_char_p, 1, help.encode("utf-8")))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigSetDefaultString")

    def ConfigGetParamInt(self, name):
        #int ConfigGetParamInt(m64p_handle ConfigSectionHandle, const char *ParamName)
        function = wrp_dt.cfunc("ConfigGetParamInt", self.m64p_lib_core, c.c_int,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")))

        status = function()

        if status:
            return status
        else:
            print("ConfigGetParamInt error:" + name)

    def ConfigGetParamFloat(self, name):
        #float ConfigGetParamFloat(m64p_handle ConfigSectionHandle, const char *ParamName)
        function = wrp_dt.cfunc("ConfigGetParamFloat", self.m64p_lib_core, c.c_float,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")))

        status = function()

        if status:
            return status
        else:
            print("ConfigGetParamFloat error:" + name)

    def ConfigGetParamBool(self, name):
        #int ConfigGetParamBool(m64p_handle ConfigSectionHandle, const char *ParamName)
        function = wrp_dt.cfunc("ConfigGetParamBool", self.m64p_lib_core, c.c_int,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")))

        status = function()

        if status:
            return c_bool(status).value
        else:
            print("ConfigGetParamBool error:" + name)

    def ConfigGetParamString(self, name):
        #const char *ConfigGetParamString(m64p_handle ConfigSectionHandle, const char *ParamName)

        function = wrp_dt.cfunc("ConfigGetParamString", self.m64p_lib_core, c.c_char_p,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")))

        status = function()

        if status != None:
            return status
        else:
            print("ConfigGetParamString error:" + name)

    ## OS-Abstraction Functions
    def ConfigGetSharedDataFilepath(self, string):
        #const char * ConfigGetSharedDataFilepath(const char *filename)

        function = wrp_dt.cfunc("ConfigGetSharedDataFilepath", self.m64p_lib_core, c.c_char_p,
                         ("filename", c.c_char_p, 1, string.encode("utf-8")))
        filename = function()

        if type(filename) == bytes:
            return filename.decode("utf-8")
        else:
            return filename

    def ConfigGetUserConfigPath(self):
        #const char * ConfigGetUserConfigPath(void)
        function = wrp_dt.cfunc("ConfigGetUserConfigPath", self.m64p_lib_core, c.c_char_p)
        filename = function()

        return filename.decode("utf-8")

    def ConfigGetUserDataPath(self):
        #const char * ConfigGetUserDataPath(void)

        function = wrp_dt.cfunc("ConfigGetUserDataPath", self.m64p_lib_core, c.c_char_p)
        filename = function()

        return filename.decode("utf-8")

    def ConfigGetUserCachePath(self):
        #const char * ConfigGetUserCachePath(void)

        function = wrp_dt.cfunc("ConfigGetUserCachePath", self.m64p_lib_core, c.c_char_p)
        filename = function()

        return filename.decode("utf-8")

    def PluginStartup(self, plugin, context):
        #m64p_error PluginStartup(m64p_dynlib_handle CoreLibHandle, void *Context, void (*DebugCallback)(void *Context, int level, const char *Message))

        function = wrp_dt.cfunc("PluginStartup", plugin, wrp_dt.m64p_error,
                        ("CoreLibHandle", c.c_void_p, 1, c.c_void_p(self.m64p_lib_core._handle)),
                        ("Context", c.c_void_p, 2, context),
                        ("DebugCallback", c.c_void_p, 2, wrp_cb.CB_DEBUG))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, ("PluginStartup: " + wrp_dt.m64p_plugin_type(plugin).name).encode("utf-8"))

    def PluginShutdown(self, plugin):
        #m64p_error PluginShutdown(void)
        function = wrp_dt.cfunc("PluginShutdown", plugin, wrp_dt.m64p_error)

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, ("PluginShutdown: " + wrp_dt.m64p_plugin_type(plugin).name).encode("utf-8"))

    #######CoreDoCommand commands #####
    def rom_open(self, rom_path):
        #M64CMD_ROM_OPEN = 1

        self.load_rom = open(rom_path, "rb")
        self.read_rom = self.load_rom.read()
        self.rom_size = c.c_int(len(self.read_rom))
        #self.romtype = binascii.hexlify(rom[:4])
        self.rom_buffer = c.create_string_buffer(self.read_rom)

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_ROM_OPEN.value, self.rom_size, c.byref(self.rom_buffer))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Open ROM file failed!")

        return status

    def rom_close(self):
        #M64CMD_ROM_CLOSE = 2

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_ROM_CLOSE.value, c.c_int(), c.c_void_p())

        # Make sure everything is cleaned
        self.load_rom = None
        self.read_rom = None
        self.rom_size = None
        self.rom_buffer = None

        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Close ROM file failed!")
        return status

    def rom_get_header(self):
        #M64CMD_ROM_GET_HEADER = 3
        #TODO: Almost all outputs are raw (in integer). How to convert them to string?

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_ROM_GET_HEADER.value, c.c_int(c.sizeof(self.rom_header)), c.pointer(self.rom_header))

        header = None
        country = None

        lat = self.rom_header.init_PI_BSB_DOM1_LAT_REG
        pgs1 = self.rom_header.init_PI_BSB_DOM1_PGS_REG
        pwd = self.rom_header.init_PI_BSB_DOM1_PWD_REG
        pgs2 =self.rom_header.init_PI_BSB_DOM1_PGS_REG2
        clockrate = self.rom_header.ClockRate
        pc = self.rom_header.PC
        release = self.rom_header.Release
        crc1 = self.rom_header.CRC1
        crc2 = self.rom_header.CRC2

        raw_name = self.rom_header.Name[:]
        name = bytes(raw_name).decode('cp932','replace')

        manufacturer = self.rom_header.Manufacturer_ID
        cartridge = self.rom_header.Cartridge_ID
        country_raw = self.rom_header.Country_code
        if country_raw == 69 or country_raw == 325 or country_raw == 581:
            # 69 = 1.0, 325 = 1.1, 581 = 1.2
            country = 'U'
        elif country_raw == 74 or country_raw == 842 or country_raw == 330 or country_raw == 586:
            # 74 = 1.0, 330 = 1.1, 586 = 1.2, 842 = 1.3
            country = 'J'
        elif country_raw == 65:
            country = 'JU'
        elif country_raw == 80 or country_raw == 336 or country_raw == 592 or country_raw == 88  or country_raw == 89:
            # 80 = 1.0, 336 = 1.1, 592 = 1.2, 88 = region 1 with some lang, 89 = region 2 with some other lang
            country = 'E'
        elif country_raw == 85:
            country = 'A'
        elif country_raw == 70:
            country = 'F'
        elif country_raw == 68 or country_raw == 324 or country_raw == 580:
            #68 = 1.0, 324 = 1.1, 580 = 1.2
            country = 'G'
        elif country_raw == 73:
            country = 'I'
        elif country_raw == 83:
            country = 'S'
        else:
            country = '?'


        header = {"lat": lat, "pgs1": pgs1, "pwd": pwd, "pgs2": pgs2, "clockrate": clockrate,
                  "pc": pc, "release": release, "crc1": crc1, "crc2": crc2, "name": name,
                  "manufacturer": manufacturer, "cartridge": cartridge, "country": country}

        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Couldn't retrieve the ROM's header.")
            return status
        else:
            #print(header)
            return header

    def rom_get_settings(self):
        #M64CMD_ROM_GET_SETTINGS = 4
        #TODO: savetype needs to be converted. 0 = eep4k, 1 = eep16k, 2 = sram, 3 = flashram, 4 = ??, 5 = controller pak

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_ROM_GET_SETTINGS.value, c.c_int(c.sizeof(self.rom_settings)), c.pointer(self.rom_settings))

        name = self.rom_settings.goodname.decode()

        md5 = self.rom_settings.MD5.decode()
        savetype = self.rom_settings.savetype
        m64pstatus = self.rom_settings.status
        players = self.rom_settings.players
        rumble = self.rom_settings.rumble

        settings = {"name": name, "md5": md5, "savetype": savetype,
                    "status": m64pstatus, "players": players, "rumble": rumble}

        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Couldn't retrieve the ROM's settings.")
            return status
        else:
            #print(settings)
            return settings

    def execute(self):
        #M64CMD_EXECUTE = 5
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_EXECUTE.value, c.c_int(), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to execute")
        return status

    def stop(self):
        #M64CMD_STOP = 6
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_STOP.value, c.c_int(), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to stop emulation")
        return status

    def pause(self):
        #M64CMD_PAUSE = 7
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_PAUSE.value, c.c_int(), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to pause emulation")
        return status

    def resume(self):
        #M64CMD_RESUME = 8
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_RESUME.value, c.c_int(), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to resume emulation")
        return status

    def core_state_query(self, query):
        #M64CMD_CORE_STATE_QUERY = 9
        # M64CORE_EMU_STATE, M64CORE_VIDEO_MODE, M64CORE_SAVESTATE_SLOT, M64CORE_SPEED_FACTOR, M64CORE_SPEED_LIMITER, M64CORE_VIDEO_SIZE, M64CORE_AUDIO_VOLUME, M64CORE_AUDIO_MUTE, M64CORE_INPUT_GAMESHARK, M64CORE_STATE_LOADCOMPLETE, M64CORE_STATE_SAVECOMPLETE

        state_param = c.c_void_p()
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_CORE_STATE_QUERY.value, c.c_int(query), c.byref(state_param))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to query the core")
        return state_param.value

    def state_load(self, path=None):
        #M64CMD_STATE_LOAD = 10
        if path != None:
            path_param = path.encode('utf-8')
        else:
            path_param = c.c_char_p()
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_STATE_LOAD.value, c.c_int(), path_param)
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to load the state save")
        return status

    def state_save(self, path=None, save_type=1):
        #M64CMD_STATE_SAVE = 11
        #1 = m64p state save, 2= pj64 compressed, 3= pj64 uncompressed
        if path != None:
            path_param = path.encode('utf-8')
        else:
            path_param = c.c_char_p()
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_STATE_SAVE.value, c.c_int(save_type), path_param)
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to make a state save")
        return status

    def state_set_slot(self, slot):
        #M64CMD_STATE_SET_SLOT = 12

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_STATE_SET_SLOT.value, c.c_int(slot), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to change the state save slot")
        else:
            self.current_slot = slot
        return status

    def send_sdl_keydown(self, key):
        #M64CMD_SEND_SDL_KEYDOWN = 13
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_SEND_SDL_KEYDOWN.value, c.c_int(key), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to send SDL key down signal")
        return status

    def send_sdl_keyup(self, key):
        #M64CMD_SEND_SDL_KEYUP = 14
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_SEND_SDL_KEYUP.value, c.c_int(key), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to send SDL key up signal")
        return status

    def set_frame_callback(self, frame_cb):
        #M64CMD_SET_FRAME_CALLBACK = 15
        #TODO: UNTESTED, int is ignored, pointer to m64p_frame_callback object
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_SET_FRAME_CALLBACK.value, c.c_int(), c.byref(frame_cb))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to set up the frame callback")
        return status

    def take_next_screenshot(self):
        #M64CMD_TAKE_NEXT_SCREENSHOT = 16

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_TAKE_NEXT_SCREENSHOT.value, c.c_int(), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to take screenshot")
        return status

    def core_state_set(self, query, value):
        #M64CMD_CORE_STATE_SET = 17
        # M64CORE_EMU_STATE, M64CORE_VIDEO_MODE, M64CORE_SAVESTATE_SLOT, M64CORE_SPEED_FACTOR, M64CORE_SPEED_LIMITER, M64CORE_VIDEO_SIZE, M64CORE_AUDIO_VOLUME, M64CORE_AUDIO_MUTE, M64CORE_INPUT_GAMESHARK, M64CORE_STATE_LOADCOMPLETE, M64CORE_STATE_SAVECOMPLETE

        valueptr = c.byref(c.c_int(value))
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_CORE_STATE_SET.value, c.c_int(query), valueptr)
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to set the core state")
        return status

    def read_screen(self, buffer_type, buffer_ptr):
        #M64CMD_READ_SCREEN = 18
        #TODO: UNTESTED
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_READ_SCREEN.value, c.c_int(buffer_type), c.byref(c.c_void_p(buffer_ptr)))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to read the screen")
        return status

    def reset(self, reset):
        #M64CMD_RESET = 19
        #reset: soft = 0, hard = 1
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_RESET.value, c.c_int(reset))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to reset emulation")
        return status

    def advance_frame(self):
        #M64CMD_ADVANCE_FRAME = 20

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_ADVANCE_FRAME.value, c.c_int(), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to advance by one frame")
        return status

    def set_media_loader(self):
        #M64CMD_SET_MEDIA_LOADER = 21

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_SET_MEDIA_LOADER.value, c.c_int(c.sizeof(self.media_loader)), c.byref(self.media_loader))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            print("CoreDoCommand: Unable to set the media loader. This means that the Transfer Pak or the 64DD won't work.")
        return status

    ####################

    def preload(self):
        try:
            self.m64p_lib_core = c.CDLL(self.m64p_lib_core_path)

            check_core = self.PluginGetVersion(self.m64p_lib_core)
            if check_core["version"] >= self.core_version:
                self.compatible = True

        except:
            print("Core: mupen64plus library hasn't been found")
            g.lock = True

    def plugins_startup(self):
        if self.gfx_filename != "dummy":
            self.PluginStartup(self.m64p_lib_gfx, b"gfx")
        self.PluginStartup(self.m64p_lib_audio, b"audio")
        self.PluginStartup(self.m64p_lib_input, b"input")
        self.PluginStartup(self.m64p_lib_rsp, b"rsp")

    def plugins_shutdown(self):
        if self.gfx_filename != "dummy":
            self.PluginShutdown(self.m64p_lib_gfx)
        self.PluginShutdown(self.m64p_lib_audio)
        self.PluginShutdown(self.m64p_lib_input)
        self.PluginShutdown(self.m64p_lib_rsp)

    def plugins_attach(self):
        if self.gfx_filename != "dummy":
            self.CoreAttachPlugin(wrp_dt.m64p_plugin_type.M64PLUGIN_GFX.value, self.m64p_lib_gfx)
        if self.audio_filename != "dummy":
            self.CoreAttachPlugin(wrp_dt.m64p_plugin_type.M64PLUGIN_AUDIO.value, self.m64p_lib_audio)
        if self.input_filename != "dummy":
            self.CoreAttachPlugin(wrp_dt.m64p_plugin_type.M64PLUGIN_INPUT.value, self.m64p_lib_input)
        if self.rsp_filename != "dummy":
            self.CoreAttachPlugin(wrp_dt.m64p_plugin_type.M64PLUGIN_RSP.value, self.m64p_lib_rsp)

    def plugins_detach(self):
        if self.gfx_filename != "dummy":
            self.CoreDetachPlugin(wrp_dt.m64p_plugin_type.M64PLUGIN_GFX.value)
        if self.audio_filename != "dummy":
            self.CoreDetachPlugin(wrp_dt.m64p_plugin_type.M64PLUGIN_INPUT.value)
        if self.input_filename != "dummy":
            self.CoreDetachPlugin(wrp_dt.m64p_plugin_type.M64PLUGIN_AUDIO.value)
        if self.rsp_filename != "dummy":
            self.CoreDetachPlugin(wrp_dt.m64p_plugin_type.M64PLUGIN_RSP.value)

    def plugins_preload(self):
        if self.gfx_filename != "dummy":
            try:
                self.m64p_lib_gfx = c.CDLL(self.plugins_dir + self.gfx_filename)
            except:
                print(self.gfx_filename + ": Plugin cannot be used. Dummy plugin is used instead, which means no video.")
                self.gfx_filename = "dummy"

        try:
            self.m64p_lib_audio = c.CDLL(self.plugins_dir + self.audio_filename)
        except:
            print(self.audio_filename + ": Plugin not found, cannot be used. Default plugin is used instead.")
            self.m64p_lib_audio = c.CDLL(self.plugins_dir + 'mupen64plus-audio-hle.so')
        try:
            self.m64p_lib_input = c.CDLL(self.plugins_dir + self.input_filename)
        except:
            print(self.input_filename + ": Plugin not found, cannot be used. Default plugin is used instead.")
            self.m64p_lib_input = c.CDLL(self.plugins_dir + 'mupen64plus-input-sdl.so')
        try:
            self.m64p_lib_rsp = c.CDLL(self.plugins_dir + self.rsp_filename)
        except:
            print(self.rsp_filename + ": Plugin not found, cannot be used. Default plugin is used instead.")
            self.m64p_lib_rsp = c.CDLL(self.plugins_dir + 'mupen64plus-rsp-hle.so')

    def initialise(self):
        if self.compatible == True:
            self.CoreStartup(self.frontend_api_version)
            print(self.ConfigGetSharedDataFilepath("mupen64plus.ini"))
            print(self.ConfigGetUserConfigPath())
            print(self.ConfigGetUserDataPath())
            print(self.ConfigGetUserCachePath())

            self.plugins_preload()
            self.plugins_startup()

        else:
            print("Error! Either the actual core is not compatible or something has gone wrong.")

    def run(self, rom):
        if self.vext_override == True:
            self.CoreOverrideVidExt()
            print("Core: Vidext is now enabled!")
        else:
            print("Core: Vidext should be disabled.")

        retval = self.rom_open(rom)
        if retval == 0:
            self.rom_get_header() ###
            self.rom_get_settings() ###
            self.plugins_attach()
            self.set_media_loader()
            self.execute()
            self.plugins_detach()
            self.rom_close()

    def restart(self, m64p_lib_core):
        # XXX: Unreliable
        self.plugins_shutdown()
        self.CoreShutdown()
        self.m64p_lib_core = None
        self.m64p_lib_gfx = None
        self.m64p_lib_audio = None
        self.m64p_lib_input = None
        self.m64p_lib_rsp = None
        self.preload(m64p_lib_core)
        self.initialise()

    def plugins_validate(self):
        p = pathlib.Path(self.plugins_dir)
        system = platform.system()
        if system == "Linux":
            directory = p.glob('*.so*')
        elif system == "Windows":
            directory = p.glob('*.dll')
        elif system == "Darwin":
            directory = p.glob('*.dylib')
        else:
            print("Warning: Your system is not supported")
            directory = p.glob('*.so*')

        for plugin in sorted(directory):
            try:
                filename = plugin.name
                info = self.PluginGetVersion(c.CDLL(self.plugins_dir + filename))
                if info["type"] == wrp_dt.m64p_plugin_type.M64PLUGIN_CORE.value:
                    pass
                elif info["type"] == wrp_dt.m64p_plugin_type.M64PLUGIN_AUDIO.value:
                    self.audio_plugins[filename] = info["name"]
                elif info["type"] == wrp_dt.m64p_plugin_type.M64PLUGIN_INPUT.value:
                    self.input_plugins[filename] = info["name"]
                elif info["type"] == wrp_dt.m64p_plugin_type.M64PLUGIN_GFX.value:
                    self.gfx_plugins[filename] = info["name"]
                elif info["type"] == wrp_dt.m64p_plugin_type.M64PLUGIN_RSP.value:
                    self.rsp_plugins[filename] = info["name"]
                else:
                    print("Unknown plugin")
            except:
                print(filename + ": Plugin not working or not compatible, skipping it.")
