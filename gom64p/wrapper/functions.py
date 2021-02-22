#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

import sys, pathlib, binascii, platform, os
import ctypes as c
import logging as log
import zlib

import wrapper.callback as wrp_cb
import wrapper.datatypes as wrp_dt
import wrapper.vidext as wrp_vext

###############
## VARIABLES ##
###############

# Credits to n64splat
crc_to_cic = {
    0x6170A4A1: {"ntsc-name": "6101", "pal-name": "7102", "offset": 0x000000},
    0x90BB6CB5: {"ntsc-name": "6102", "pal-name": "7101", "offset": 0x000000},
    0x0B050EE0: {"ntsc-name": "6103", "pal-name": "7103", "offset": 0x100000},
    0x98BC2C86: {"ntsc-name": "6105", "pal-name": "7105", "offset": 0x000000},
    0xACC8580A: {"ntsc-name": "6106", "pal-name": "7106", "offset": 0x200000},
    0x00000000: {"ntsc-name": "unknown", "pal-name": "unknown", "offset": 0x0000000}
}

#############
## CLASSES ##
#############

class API():
    """Wrapper for calling libmupen64plus.so's functions into python code"""
    def __init__(self, parent, params):
        # https://github.com/mupen64plus/mupen64plus-core/blob/master/doc/emuwiki-api-doc/Mupen64Plus-v2.0-API-Versioning.mediawiki
        # MUPEN_CORE_NAME
        self.core_name = "Mupen64Plus Core"

        # Latest API version (MUPEN_CORE_VERSION) supported by this wrapper.
        self.core_version = 0x020509 # 2.5.9 BETA

        # MINIMUM_CORE_VERSION = 0x016300

        # FRONTEND_API_VERSION
        self.frontend_api = 0x020103

        # CONFIG_API_VERSION
        self.config_api = 0x20301

        # DEBUG_API_VERSION
        self.debug_api = 0x020001

        # VIDEXT_API_VERSION
        self.vidext_api = 0x030200

        # NETPLAY_API_VERSION
        self.netplay_api = 0x010000

        # Plugins API version
        ## RSP_API_VERSION
        self.rsp_api = 0x20000

        ## GFX_API_VERSION
        self.gfx_api = 0x20200

        ## AUDIO_API_VERSION
        self.audio_api = 0x20000

        ## INPUT_API_VERSION
        self.input_api = 0x20100

        # Setting up some variables....
        self.frontend = parent
        self.platform = params['platform']
        self.m64p_lib_core_path = params['m64plib']
        self.plugins_dir = params['pluginsdir']
        self.frontend_api_version = params['api_version']
        self.compatible = False
        self.emulating = False # This tells whether it's emulating a game or not
        self.running = False   # And this tell whether the game is running or it is paused
        self.lock = False
        self.vext_override = False
        self.current_slot = 0

        # Wire in the callbacks
        wrp_cb.frontend = self.frontend
        self.media_loader = wrp_cb.MEDIA_LOADER

        # If there is a path where the .cfg is found, tell the core to use it
        configpath = params['configdir'].encode('utf-8')
        if configpath != b'':
            self.config_dir = configpath
        else:
            self.config_dir = None

        # If there is a path where mupen64plus.ini is found, tell the core to use it
        datapath = params['datadir'].encode('utf-8')
        if datapath != b'':
            self.data_dir = datapath
        else:
            self.data_dir = None

        # Retrieve last used plugins from frontend's config
        self.gfx_filename = params['gfx']
        self.audio_filename = params['audio']
        self.input_filename = params['input']
        self.rsp_filename = params['rsp']

        # Initialise those lists to store plugins
        self.gfx_plugins = {}
        self.audio_plugins = {}
        self.input_plugins = {}
        self.rsp_plugins = {}

        # Determine which library extension is used.
        if self.platform == "Linux":
            self.extension_filename = ".so"
        elif self.platform == "Windows":
            self.extension_filename = ".dll"
        elif self.platform == "Darwin":
            self.extension_filename = ".dylib"
        else:
            log.warning("Warning: Your system is not supported")
            self.extension_filename = ".so"

        # Initialize those empty structures
        self.rom_header = wrp_dt.m64p_rom_header()
        self.rom_settings = wrp_dt.m64p_rom_settings()

        # Setting up those handles....
        self.config_handle = None
        self.config_ext_handle = None

        # Lastly, we must check if each plugins found are compatible
        self.plugins_validate()

    ### Basic core functions
    def PluginGetVersion(self, plugin):
        ''' This function retrieves version information from the core library
        or plugin.
        This function is the same for the core library and the plugins, so that
        a front-end may examine all shared libraries in a directory and
        determine their types. Any of the input parameters may be set to NULL
        and this function will succeed but won't return the corresponding
        information.
        REQUIREMENTS:
        - None
        PROTOTYPE:
         m64p_error PluginGetVersion(m64p_plugin_type *PluginType, int *PluginVersion,
                      int *APIVersion, const char **PluginNamePtr, int *Capabilities)'''
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
            return {"type": plugintype.value, "version": pluginversion.value,
                    "apiversion": apiversion.value, "name": pluginpointer.value.decode(),
                    "capabilities": capabilities.value}
        else:
            self.CoreErrorMessage(status, b"PluginGetVersion")

    def CoreGetAPIVersions(self):
        '''This function retrieves API version information from the core library.
        This function may be used by either the front-end application or any
        plugin modules. Any of the input parameters may be set to NULL and this
        function will succeed but won't return the corresponding information.
        REQUIREMENTS:
        - None
        PROTOTYPE:
         m64p_error CoreGetAPIVersions(int *ConfigVersion, int *DebugVersion,
                                       int *VidextVersion, int *ExtraVersion)'''
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
            return {"config": configversion.value, "debug": debugversion.value,
                    "vidext": vidextversion.value, "extra": extraversion.value}
        else:
            self.CoreErrorMessage(status, b"CoreGetAPIVersions")

    def CoreErrorMessage(self, ReturnCode, context=None):
        ''' This function returns a pointer to a NULL-terminated string giving
        a human-readable description of the error.
        REQUIREMENTS:
        - None
        PROTOTYPE:
        const char * CoreErrorMessage(m64p_error ReturnCode)'''
        # FIXME: context variable behaviour is inconsistent.

        function = wrp_dt.cfunc("CoreErrorMessage", self.m64p_lib_core, c.c_char_p,
                        ("ReturnCode", c.c_int, 1, c.c_int(ReturnCode)))
        status = function()

        if context != None:
            try:
                log.error(f"{c.cast(context, c.c_char_p).value.decode('utf-8')}: {status.decode('utf-8')}")
            except UnicodeDecodeError:
                log.error(f"{context}: {status.decode('utf-8')}")
        else:
            log.error(f"{status}")

    ### Frontend functions
    ## Startup/Shutdown
    def CoreStartup(self, version):
        ''' This function initializes libmupen64plus for use by allocating memory,
        creating data structures, and loading the configuration file.
        If ConfigPath is NULL, libmupen64plus will search for the configuration
        file in its usual place (On Linux, in ~/.config/mupen64plus/).
        This function may return M64ERR_INCOMPATIBLE if older front-end is used
        with newer core.
        REQUIREMENTS:
        - This function must be called before any other libmupen64plus functions.
        PROTOTYPE:
         m64p_error CoreStartup(int APIVersion, const char *ConfigPath, const char *DataPath,
            void *Context, void (*DebugCallback)(void *Context, int level, const char *message),
            void *Context2, void (*StateCallback)(void *Context2, m64p_core_param ParamChanged, int NewValue))'''

        function = wrp_dt.cfunc("CoreStartup", self.m64p_lib_core, wrp_dt.m64p_error,
                   ("APIVersion", c.c_int, 1, version),
                   ("ConfigPath", c.c_char_p, 1, c.c_char_p(self.config_dir)),
                   ("DataPath", c.c_char_p, 1, c.c_char_p(self.data_dir)),
                   ("Context", c.c_void_p, 1, c.cast(b"Core", c.c_void_p)),
                   ("DebugCallback", c.c_void_p , 2, wrp_cb.CB_DEBUG),
                   ("Context2", c.c_void_p, 1, c.cast(b"State", c.c_void_p)),
                   ("StateCallback", c.c_void_p , 2, self.frontend.CB_STATE))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"CoreStartup")

    def CoreShutdown(self):
        '''This function saves the configuration file, then destroys data
        structures and releases memory allocated by the core library.
        REQUIREMENTS:
        - None
        PROTOTYPE:
         m64p_error CoreShutdown(void)'''
        function = wrp_dt.cfunc("CoreShutdown", self.m64p_lib_core, wrp_dt.m64p_error)

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"CoreShutdown")

    def CoreAttachPlugin(self, plugin, handle):
        '''This function attaches the given plugin to the emulator core.
        There can only be one plugin of each type attached to the core at any given time.
        REQUIREMENTS:
        - Both the core library and the plugin library must already be initialized
          with the CoreStartup()/PluginStartup() functions.
        - ROM must be open.
        - Plugins must be attached in this order: video, audio, input, RSP.
        PROTOTYPE:
          m64p_error CoreAttachPlugin(m64p_plugin_type PluginType, m64p_dynlib_handle PluginLibHandle)'''
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
        '''This function detaches the given plugin from the emulator core,
        and re-attaches the 'dummy' plugin functions.
        REQUIREMENTS:
        - Both the core library and the plugin library must already be initialized
          with the CoreStartup()/PluginStartup() functions.
        - This function cannot be called while the emulator is running.
        PROTOTYPE:
          m64p_error CoreDetachPlugin(m64p_plugin_type PluginType)'''
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
        '''This function sends a command to the emulator core.
        Commands available:
          M64CMD_ROM_OPEN, M64CMD_ROM_CLOSE, M64CMD_ROM_GET_HEADER, M64CMD_ROM_GET_SETTINGS,
          M64CMD_EXECUTE, M64CMD_STOP, M64CMD_PAUSE, M64CMD_RESUME, M64CMD_CORE_STATE_QUERY,
          M64CMD_STATE_LOAD, M64CMD_STATE_SAVE, M64CMD_STATE_SET_SLOT, M64CMD_SEND_SDL_KEYDOWN,
          M64CMD_SEND_SDL_KEYUP, M64CMD_SET_FRAME_CALLBACK, M64CMD_TAKE_NEXT_SCREENSHOT,
          M64CMD_CORE_STATE_SET, M64CMD_READ_SCREEN, M64CMD_RESET, M64CMD_ADVANCE_FRAME,
          M64CMD_SET_MEDIA_LOADER, M64CMD_NETPLAY_INIT, M64CMD_NETPLAY_CONTROL_PLAYER,
          M64CMD_NETPLAY_GET_VERSION, M64CMD_NETPLAY_CLOSE, M64CMD_PIF_OPEN
        REQUIREMENTS:
        - The core library must already be initialized with the CoreStartup() function.
        - Each command may have its own requirements as well.
        PROTOTYPE:
         m64p_error CoreDoCommand(m64p_command Command, int ParamInt, void *ParamPtr)'''
        function = wrp_dt.cfunc("CoreDoCommand", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("Command", c.c_int, 1, command),
                        ("ParamInt", c.c_int, 1, arg1),
                        ("ParamPtr", c.c_void_p, 2, arg2))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.debug(f"CoreDoCommand: {wrp_dt.m64p_command(command).name}:{wrp_dt.m64p_core_param(arg1.value).name if arg1.value == 6 else arg1}:{arg2}")
        else:
            self.CoreErrorMessage(status, wrp_dt.m64p_command(command).name.encode("utf-8"))
        return status

    ## ROM Handling
    def CoreGetRomSettings(self, crc1, crc2):
        ''' This function searches through the data in the Mupen64Plus.ini file
        to find an entry which matches the given Crc1 and Crc2 hashes, and if
        found, fills in the RomSettings structure with the data from the Mupen64Plus.ini file.
        REQUIREMENTS:
        - The core library must already be initialized with the CoreStartup() function.
        - The RomSettings pointer must not be NULL.
        - The RomSettingsLength value must be greater than or equal to the size
          of the m64p_rom_settings structure.
        - This function does not require any ROM image to be currently open.
        PROTOTYPE:
         m64p_error CoreGetRomSettings(m64p_rom_settings *RomSettings, int RomSettingsLength, int Crc1, int Crc2)'''
        # XXX: For the CRCs base 16 must be specified, with int(x, 16)
        # XXX: a pointer has been added to RomSettingsLength even though the prototype
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
        '''This function overrides the core's internal SDL-based OpenGL functions
        which are called from the video plugin to perform various basic tasks like
        opening the video window, toggling between windowed and fullscreen modes,
        and swapping frame buffers after a frame has been rendered.
        This override functionality allows a front-end to define its own video
        extension functions to be used instead of the SDL functions, such as for
        the purpose of embedding the emulator display window inside of a Qt GUI
        window. If any of the function pointers in the structure are NULL, the
        override function will be disabled and the core's internal SDL functions
        will be used. The core library with a Video Extension API v3.0 expects
        the Functions struct member to be equal to 11 or more.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - This function cannot be called while the emulator is running.
        PROTOTYPE:
         m64p_error CoreOverrideVidExt(m64p_video_extension_functions *VideoFunctionStruct)'''
        function = wrp_dt.cfunc("CoreOverrideVidExt", self.m64p_lib_core, wrp_dt.m64p_error,
                       ("VideoFunctionStruct", c.POINTER(wrp_dt.m64p_video_extension_functions),
                        2, c.byref(wrp_vext.vidext_struct)))
        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"CoreOverrideVidExt")

    ## Cheat Functions
    def CoreAddCheat(self, cheatname, codelist):
        ''' This function will add a Cheat Function to a list of currently active
        cheats which are applied to the open ROM, and set its state to Enabled.
        This function may be called before a ROM begins execution or while a ROM
        is currently running. Some cheat codes must be applied before the ROM
        begins executing, and may not work correctly if added after the ROM
        begins execution.
        A Cheat Function consists of a list of one or more m64p_cheat_code
        elements. If a Cheat Function with the given CheatName already exists,
        it will be removed and the new Cheat Function will be added in its place.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - A ROM image must be currently opened.
        PROTOTYPE:
         m64p_error CoreAddCheat(const char *CheatName, m64p_cheat_code *CodeList, int NumCodes)'''
        function = wrp_dt.cfunc("CoreAddCheat", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("CheatName", c.c_char_p, 1, cheatname.encode("utf-8")),
                        ("CodeList", c.POINTER(wrp_dt.m64p_cheat_code * len(codelist)), 1, c.byref(codelist)),
                        ("NumCodes", c.c_int, 1, c.c_int(c.sizeof(codelist))))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.info(f"Cheats: activate '{cheatname}'")
            return status
        else:
            self.CoreErrorMessage(status, b"CoreAddCheat")

    def CoreCheatEnabled(self, cheatname, enabled):
        '''This function enables or disables a specified Cheat Function.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - A ROM image must be currently opened.
        PROTOTYPE:
         m64p_error CoreCheatEnabled(const char *CheatName, int Enabled)'''
        function = wrp_dt.cfunc("CoreCheatEnabled", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("CheatName", c.c_char_p, 1, cheatname.encode("utf-8")),
                        ("Enabled", c.c_int, 1, c.c_int(enabled)))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            if enabled == True:
                log.info(f"Cheats: activating '{cheatname}'")
            else:
                log.info(f"Cheats: deactivating '{cheatname}'")
            return status
        else:
            self.CoreErrorMessage(status, b"CoreCheatEnabled")

    ### Video Extension
    ### XXX: Those functions aren't intended to be used by frontend, but rather
    ### to help with vidext implementation

    ## Startup/Shutdown
    def __VidExt_Init(self):
        # WARNING: Not for use
        # m64p_error VidExt_Init(void)
        function = wrp_dt.cfunc("VidExt_Init", self.m64p_lib_core, wrp_dt.m64p_error)

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_Init")

    def __VidExt_Quit(self):
        # WARNING: Not for use
        # m64p_error VidExt_Quit(void)
        function = wrp_dt.cfunc("VidExt_Quit", self.m64p_lib_core, wrp_dt.m64p_error)

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_Quit")

    ## Screen Handling
    def __VidExt_ListFullscreenModes(self):
        # WARNING: Not for use
        # m64p_error VidExt_ListFullscreenModes(m64p_2d_size *SizeArray, int *NumSizes)
        function = wrp_dt.cfunc("VidExt_ListFullscreenModes", self.m64p_lib_core, wrp_dt.m64p_error,
                       ("SizeArray", c.POINTER(wrp_dt.m64p_2d_size), 2, c.byref(wrp_dt.m64p_2d_size())),
                       ("NumSizes", c.POINTER(c.c_int), 2, c.c_int()))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_ListFullscreenModes")

    def __VidExt_SetVideoMode(self, width, height, bits, screenmode, flags):
        # WARNING: Not for use
        # m64p_error VidExt_SetVideoMode(int Width, int Height, int BitsPerPixel,
        #                   m64p_video_mode ScreenMode, m64p_video_flags Flags)
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

    def __VidExt_SetCaption(self, title):
        # WARNING: Not for use
        # m64p_error VidExt_SetCaption(const char *Title)
        function = wrp_dt.cfunc("VidExt_SetCaption", self.m64p_lib_core, wrp_dt.m64p_error,
                       ("Title", c.c_char_p, 1, title.encode("utf-8")))


        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_SetCaption")

    def __VidExt_ToggleFullScreen(self):
        # WARNING: Not for use
        # m64p_error VidExt_ToggleFullScreen(void)
        function = wrp_dt.cfunc("VidExt_ToggleFullScreen", self.m64p_lib_core, wrp_dt.m64p_error)


        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_ToggleFullScreen")

    def __VidExt_ResizeWindow(self, width, height):
        # WARNING: Not for use
        # m64p_error VidExt_ResizeWindow(int Width, int Height)
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
    def __VidExt_GL_GetProcAddress(self, proc):
        # WARNING: Not for use
        # void * VidExt_GL_GetProcAddress(const char* Proc)
        function = wrp_dt.cfunc("VidExt_GL_GetProcAddress", self.m64p_lib_core, wrp_dt.m64p_function,
                        ("Proc", c.c_char_p, 1, proc.encode("utf-8")))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        #if status == m64p_error.M64ERR_SUCCESS.value:
        #    return status
        #else:
        #    print(self.CoreErrorMessage(status, b"VidExt_GL_GetProcAddress"))

    def __VidExt_GL_SetAttribute(self, attr, value):
        # WARNING: Not for use
        # m64p_error VidExt_GL_SetAttribute(m64p_GLattr Attr, int Value)
        function = wrp_dt.cfunc("VidExt_GL_SetAttribute", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("Attr", c.c_int, c.c_int(wrp_dt.m64p_GLattr(attr))),
                        ("Value", c.c_int, 1, c.c_int(value)))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_GL_SetAttribute")

    def __VidExt_GL_GetAttribute(self, attr, pvalue):
        # WARNING: Not for use
        # m64p_error VidExt_GL_GetAttribute(m64p_GLattr Attr, int *pValue)
        function = wrp_dt.cfunc("VidExt_GL_GetAttribute", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("Attr", c.c_int, c.c_int(wrp_dt.m64p_GLattr(attr))),
                        ("pValue", c.POINTER(c.c_int), 1, c.byref(c.c_int(pvalue))))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_GL_GetAttribute")

    def __VidExt_GL_SwapBuffers(self):
        # WARNING: Not for use
        # m64p_error VidExt_GL_SwapBuffers(void)
        function = wrp_dt.cfunc("VidExt_GL_SwapBuffers", self.m64p_lib_core, wrp_dt.m64p_error)


        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"VidExt_GL_SwapBuffers")

    ### Debugger https://github.com/mupen64plus/mupen64plus-core/blob/master/doc/emuwiki-api-doc/Mupen64Plus-v2.0-Core-Debugger.mediawiki
    ## General functions
    def DebugSetCallbacks(self):
        ''' This function is called by the front-end to supply debugger callback
        function pointers. If debugger is enabled and then later disabled within
        the GUI, this function may be called with NULL pointers in order to
        disable the callbacks.
        REQUIREMENTS:
        - The Mupen64Plus library must be built with debugger support and must
          be initialized before calling this function.
        PROTOTYPE:
         m64p_error DebugSetCallbacks(void (*dbg_frontend_init)(void),
             void (*dbg_frontend_update)(unsigned int pc), void (*dbg_frontend_vi)(void))'''
        # TODO: Stub

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
        '''This function is called by the front-end to supply callback function pointers
        for the Core Comparison feature. This feature is designed to work as follows.
        The front-end application will set up some channel for communicating data
        between two separately running instances of mupen64plus. For example, the
        unix console front-end will use named FIFOs. The front-end will register
        callback functions for comparing the 2 cores' states via this
        DebugSetCoreCompare API call. When the dbg_core_compare callback fires,
        the front-end will use the DebugGetCPUDataPtr function (and DebugMemGetPointer
        function if desired) to transmit emulator core state data from the 'sending'
        instance to the 'receiving' instance. The receiving instance may then check
        the core state data against it's own internal state and report any discrepancies.
        When the dbg_core_data_sync callback fires, the front-end should transmit a block
        of data from the sending instance to the receiving instance. This is for the
        purposes of synchronizing events such as controller inputs or state loading
        commands, so that the 2 cores may stay synchronized. This feature does not
        require the M64CAPS_DEBUGGER capability to built into the core,
        but it does require the M64CAPS_CORE_COMPARE capability.
        REQUIREMENTS:
        - The Mupen64Plus library must be initialized before calling this function.
        PROTOTYPE:
         m64p_error DebugSetCoreCompare(void (*dbg_core_compare)(unsigned int),
            void (*dbg_core_data_sync)(int, void *))'''
        # TODO: Stub
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
        '''This function sets the run state of the R4300 CPU emulator.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         m64p_error DebugSetRunState(int runstate)'''
        # TODO: Stub
        function = wrp_dt.cfunc("DebugSetRunState", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("runstate", c.c_int, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"DebugSetRunState")

    def DebugGetState(self):
        '''This function reads and returns a debugger state variable, which
        are enumerated in m64p_types.h.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         int DebugGetState(m64p_dbg_state statenum)
        '''
        # TODO: Stub
        function = wrp_dt.cfunc("DebugGetState", self.m64p_lib_core, c.c_int,
                        ("statenum", wrp_dt.m64p_dbg_state, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugStep(self):
        '''This function signals the debugger to advance one instruction when
        in the stepping mode.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        - The emulator core must be executing a ROM.
        - The debugger must be active.
        PROTOTYPE:
         m64p_error DebugStep(void)'''
        # TODO: Untested
        function = wrp_dt.cfunc("DebugStep", self.m64p_lib_core, wrp_dt.m64p_error)

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"DebugStep")

    def DebugDecodeOp(self):
        ''' This is a helper function for the debugger front-end.
        This instruction takes a PC value and an R4300 instruction opcode and
        writes the disassembled instruction mnemonic and arguments into character buffers.
        This is intended to be used to display disassembled code.
        REQUIREMENTS:
        - The Mupen64Plus library must be built with debugger support.
        PROTOTYPE:
         void DebugDecodeOp(unsigned int instruction, char *op, char *args, int pc)'''
        # TODO: Stub
        function = wrp_dt.cfunc("DebugDecodeOp", self.m64p_lib_core, None,
                        ("instruction", c.c_uint, 1),
                        ("op", c.POINTER(c.c_char), 1),
                        ("args", c.POINTER(c.c_char), 1),
                        ("pc", c.c_int, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    ## Memory debug functions
    def DebugMemGetRecompInfo(self):
        '''This function is used by the front-end to retrieve disassembly information
        about recompiled code. For example, the dynamic recompiler may take a single
        R4300 instruction and compile it into 10 x86 instructions.
        This function may then be used to retrieve the disassembled code of the 10
        x86 instructions. For recomp_type of M64P_DBG_RECOMP_OPCODE or M64P_DBG_RECOMP_ARGS,
        a character pointer will be returned which gives the disassembled instruction code.
        For recomp_type of M64P_DBG_RECOMP_ADDR, a pointer to the recompiled x86
        instruction will be given.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        WARNING:
         This function may not be available on all platforms.
        PROTOTYPE:
         void * DebugMemGetRecompInfo(m64p_dbg_mem_info recomp_type, unsigned int address, int index)'''
        # TODO: Stub
        function = wrp_dt.cfunc("DebugMemGetRecompInfo", self.m64p_lib_core, c.c_void_p,
                        ("recomp_type", wrp_dt.m64p_dbg_mem_info, 1),
                        ("address", c.c_uint, 1),
                        ("index", c.c_int, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemGetMemInfo(self):
        '''This function returns an integer value regarding the memory location
        address, corresponding to the information requested by mem_info_type,
        which is a type enumerated in m64p_types.h. For example, if address
        contains R4300 program code, the front-end may request the number of
        x86 instructions emitted by the dynamic recompiler by requesting
        M64P_DBG_MEM_NUM_RECOMPILED.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         int DebugMemGetMemInfo(m64p_dbg_mem_info mem_info_type, unsigned int address)'''
        # TODO: Stub
        function = wrp_dt.cfunc("DebugMemGetMemInfo", self.m64p_lib_core, c.c_int,
                        ("mem_info_type", wrp_dt.m64p_dbg_mem_info, 1),
                        ("address", c.c_uint, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemGetPointer(self):
        '''This function returns a memory pointer (in x86 memory space) to a block
        of emulated N64 memory. This may be used to retrieve a pointer to a special
        N64 block (such as the serial, video, or audio registers) or the RDRAM.
        The m64p_dbg_memptr_type type is enumerated in m64p_types.h.
        REQUIREMENTS:
        - The Mupen64Plus library must be initialized before calling this function.
        PROTOTYPE:
         void * DebugMemGetPointer(m64p_dbg_memptr_type mem_ptr_type)'''
        # TODO: Stub
        function = wrp_dt.cfunc("DebugMemGetPointer", self.m64p_lib_core, c.c_void_p,
                        ("mem_ptr_type", wrp_dt.m64p_dbg_memptr_type, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemRead64(self, address):
        '''This function retrieve a value from the emulated N64 memory.
        The returned value will be correctly byte-swapped for the host architecture.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         unsigned long long DebugMemRead64(unsigned int address)'''
        # TODO: Untested
        function = wrp_dt.cfunc("DebugMemRead64", self.m64p_lib_core, c.c_ulonglong,
                        ("address", c.c_uint, 1, address))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemRead32(self, address):
        '''This function retrieve a value from the emulated N64 memory.
        The returned value will be correctly byte-swapped for the host architecture.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         unsigned int DebugMemRead32(unsigned int address)'''
        # TODO: Untested
        function = wrp_dt.cfunc("DebugMemRead32", self.m64p_lib_core, c.c_uint,
                        ("address", c.c_uint, 1, address))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemRead16(self, address):
        '''This function retrieve a value from the emulated N64 memory.
        The returned value will be correctly byte-swapped for the host architecture.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         unsigned short DebugMemRead16(unsigned int address)'''
        # TODO: Untested
        function = wrp_dt.cfunc("DebugMemRead16", self.m64p_lib_core, c.c_ushort,
                        ("address", c.c_uint, 1, address))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function(self)

    def DebugMemRead8(self, address):
        '''This function retrieve a value from the emulated N64 memory.
        The returned value will be correctly byte-swapped for the host architecture.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         unsigned char DebugMemRead8(unsigned int address)'''
        # TODO: Untested
        function = wrp_dt.cfunc("DebugMemRead8", self.m64p_lib_core, c.c_ubyte,
                        ("address", c.c_uint, 1, address))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemWrite64(self, address, value):
        '''These functions write a value into the emulated N64 memory.
        The given value will be correctly byte-swapped before storage.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         void DebugMemWrite64(unsigned int address, unsigned long long value)'''
        # TODO: Untested
        function = wrp_dt.cfunc("DebugMemWrite64", self.m64p_lib_core, None,
                        ("address", c.c_uint, 1, address),
                        ("value", c.c_ulonglong, 1, value))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemWrite32(self, address, value):
        '''These functions write a value into the emulated N64 memory.
        The given value will be correctly byte-swapped before storage.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         void DebugMemWrite32(unsigned int address, unsigned int value)'''
        # TODO: Untested
        function = wrp_dt.cfunc("DebugMemWrite32", self.m64p_lib_core, None,
                        ("address", c.c_uint, 1, address),
                        ("value", c.c_uint, 1, value))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemWrite16(self, address, value):
        '''These functions write a value into the emulated N64 memory.
        The given value will be correctly byte-swapped before storage.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         void DebugMemWrite16(unsigned int address, unsigned short value)'''
        # TODO: Untested
        function = wrp_dt.cfunc("DebugMemWrite16", self.m64p_lib_core, None,
                        ("address", c.c_uint, 1, address),
                        ("value", c.c_ushort, 1, value))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugMemWrite8(self, address, value):
        '''These functions write a value into the emulated N64 memory.
        The given value will be correctly byte-swapped before storage.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         void DebugMemWrite8(unsigned int address, unsigned char value)'''
        # TODO: Untested
        function = wrp_dt.cfunc("DebugMemWrite8", self.m64p_lib_core, None,
                        ("address", c.c_uint, 1, address),
                        ("value", c.c_ubyte, 1, value))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    ## R4300 CPU functions
    def DebugGetCPUDataPtr(self):
        '''This function returns a memory pointer (in x86 memory space) to a
        specific register in the emulated R4300 CPU. The m64p_dbg_cpu_data type
        is enumerated in m64p_types.h.
        It is important to note that when the R4300 CPU core is in the Cached
        Interpreter or Dynamic Recompiler modes, the address of the PC register
        is not constant; it will change after each instruction is executed.
        The pointers to all other registers will never change, as the other
        registers are global variables.
        REQUIREMENTS:
        - The Mupen64Plus library must be initialized before calling this function.
        PROTOTYPE:
         void *DebugGetCPUDataPtr(m64p_dbg_cpu_data cpu_data_type)'''
        # TODO: stub
        function = wrp_dt.cfunc("DebugGetCPUDataPtr", self.m64p_lib_core, c.c_void_p,
                        ("cpu_data_type", wrp_dt.m64p_dbg_cpu_data, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    ## Breakpoint functions
    def DebugBreakpointLookup(self):
        '''This function searches through all current breakpoints in the debugger
        to find one that matches the given input parameters.
        If a matching breakpoint is found, the index number is returned.
        If no breakpoints are found, -1 is returned.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         int DebugBreakpointLookup(unsigned int address, unsigned int size, unsigned int flags)'''
        # TODO: Stub
        function = wrp_dt.cfunc("DebugBreakpointLookup", self.m64p_lib_core, c.c_int,
                        ("address", c.c_uint, 1),
                        ("size", c.c_uint, 1),
                        ("flags", c.c_uint, 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugBreakpointCommand(self):
        '''This function is used to process common breakpoint commands, such as
        adding, removing, or searching the breakpoints. The meanings of the index
        and bkp input parameters vary by command, and are given in the table below.
        The m64p_dbg_bkp_command type is enumerated in m64p_types.h.
        Commands available:
         M64P_BKP_CMD_ADD_ADDR, M64P_BKP_CMD_ADD_STRUCT, M64P_BKP_CMD_REPLACE,
         M64P_BKP_CMD_REMOVE_ADDR, M64P_BKP_CMD_REMOVE_IDX, M64P_BKP_CMD_ENABLE,
         M64P_BKP_CMD_DISABLE, M64P_BKP_CMD_CHECK
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        PROTOTYPE:
         int DebugBreakpointCommand(m64p_dbg_bkp_command command, unsigned int index, m64p_breakpoint *bkp)'''
        #TODO: Stub
        function = wrp_dt.cfunc("DebugBreakpointCommand", self.m64p_lib_core, c.c_int,
                        ("command", wrp_dt.m64p_dbg_bkp_command, 1),
                        ("index", c.c_uint, 1),
                        ("bkp", c.POINTER(wrp_dt.m64p_breakpoint), 1))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugBreakpointTriggeredBy(self):
        '''This function is used to programmatically access the trigger reason
        and address for the most recently triggered breakpoint.
        The meaning of the flags value are the same as the m64p_dbg_bkp_flags
        enumerated in m64p_types.h. For memory read/write breakpoints, the value
        of accessed will be set to the physical address accessed; exec breakpoints
        will not populate this value as the necessary information is already
        encoded in the program counter.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        - The emulator core must be executing a ROM.
        - The debugger must be active.
        PROTOTYPE:
         void DebugBreakpointTriggeredBy(uint32_t *flags, uint32_t *accessed)'''
        #TODO: Stub
        function = wrp_dt.cfunc("DebugBreakpointTriggeredBy", self.m64p_lib_core, c.c_void_p,
                                ("flags", c.POINTER(c.c_uint), 1),
                                ("accessed", c.POINTER(c.c_uint), 1))
        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    def DebugVirtualToPhysical(self, address):
        '''This function resolves the physical address in R4300 memory corresponding
        to the provided virtual address. Memory read and write breakpoints only
        operate in terms of physical addresses, thus this function is provided to
        assist in the necessary virtual to physical translations.
        REQUIREMENTS (before calling this function):
        - The Mupen64Plus library must be built with debugger support.
        - The Mupen64Plus library must be initialized.
        - The emulator core must be executing a ROM.
        - The debugger must be active.
        PROTOTYPE:
         uint32_t DebugVirtualToPhysical(uint32_t address)'''
        # TODO: Untested
        function = wrp_dt.cfunc("DebugVirtualToPhysical", self.m64p_lib_core, c.c_uint,
                                ("address", c.c_uint, 1, address))
        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

    ### Configuration
    ## Selector functions
    def ConfigListSections(self):
        '''This function sets the value of one of the emulator's configuration
        parameters in the section which is represented by ConfigSectionHandle.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The SectionListCallback pointer cannot be NULL.
        PROTOTYPE:
         m64p_error ConfigListSections(void *context, void (*SectionListCallback)
                                       (void * context, const char * SectionName))'''

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
        ''' This function is used to give a configuration section handle to the
        front-end which may be used to read or write configuration parameter
        values in a given section of the configuration file.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The SectionName and ConfigSectionHandle pointers cannot be NULL.
        PROTOTYPE:
         m64p_error ConfigOpenSection(const char *SectionName, m64p_handle *ConfigSectionHandle)'''

        # Wire in the section callback
        wrp_cb.section_cb = section

        # Reset the parameter list
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
        '''This function is called to enumerate the list of Parameters in a
        given Section of the Mupen64Plus Core configuration file.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle and ParameterListCallback pointers cannot be NULL.
        PROTOTYPE:
         m64p_error ConfigListParameters(m64p_handle ConfigSectionHandle, void *context,
             void (*ParameterListCallback)(void * context, const char *ParamName, m64p_type ParamType))'''

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
        '''This function is called to determine if a given Section (or all sections)
        of the Mupen64Plus Core configuration file has been modified since it was
        last saved. A return value of 0 means there are no unsaved changes,
        while a 1 will be returned if there are unsaved changes.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - Config API >= 2.2.0
        PROTOTYPE:
         int ConfigHasUnsavedChanges(const char *SectionName)'''
        function = wrp_dt.cfunc("ConfigHasUnsavedChanges", self.m64p_lib_core, c.c_int,
                   ("SectionName", c.c_char_p, 1, section.encode("utf-8")))

        # function.errcheck is not required here as there's no m64p_error
        status = function()

        if status == True:
            log.debug(section + ": Changes detected!")
            return status
        else:
            log.debug(section + ": No unsaved changes. Move along, nothing to see here.")
            return status

    ## Modifier functions
    def ConfigDeleteSection(self, section):
        '''This function deletes a section from the Mupen64Plus configuration data.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        PROTOTYPE:
         m64p_error ConfigDeleteSection(const char *SectionName)'''

        function = wrp_dt.cfunc("ConfigDeleteSection", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("SectionName", c.c_char_p, 1, section.encode("utf-8")))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigDeleteSection")

    def ConfigSaveFile(self):
        '''This function saves the Mupen64Plus configuration file to disk.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        PROTOTYPE:
         m64p_error ConfigSaveFile(void)'''

        function = wrp_dt.cfunc("ConfigSaveFile", self.m64p_lib_core, wrp_dt.m64p_error)

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigSaveFile")

    def ConfigSaveSection(self, section):
        '''This function saves one section of the current Mupen64Plus
        configuration to disk, while leaving the other sections unmodified.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The named section must exist in the current configuration.
        - Config API >= 2.1.0
        PROTOTYPE:
         m64p_error ConfigSaveSection(const char *SectionName)'''

        function = wrp_dt.cfunc("ConfigSaveSection", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("SectionName", c.c_char_p, 1, section.encode("utf-8")))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigSaveSection")

    def ConfigRevertChanges(self, section):
        ''' This function reverts changes previously made to one section of the
        current Mupen64Plus configuration file, so that it will match with the
        configuration at the last time that it was loaded from or saved to disk.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The named section must exist in the current configuration.
        - Config API >= 2.2.0
        PROTOTYPE:
         m64p_error ConfigRevertChanges(const char *SectionName)'''

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
        '''This function sets the value of one of the emulator's configuration
        parameters in the section which is represented by ConfigSectionHandle.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle, ParamName and ParamValue pointers cannot be NULL.
        PROTOTYPE:
         m64p_error ConfigSetParameter(m64p_handle ConfigSectionHandle,
                  const char *ParamName, m64p_type ParamType, const void *ParamValue)'''
        paramvalue_type = None

        # First check type of the parameter
        param_type = self.ConfigGetParameterType(name)

        # Then, according to parameter's type, set up pointer and its datatype
        if param_type == wrp_dt.m64p_type.M64TYPE_INT.name:
            paramvalue = c.byref(c.c_int(paramvalue))
            paramvalue_type = c.POINTER(c.c_int)
        elif param_type == wrp_dt.m64p_type.M64TYPE_FLOAT.name:
            paramvalue = c.byref(c.c_float(paramvalue))
            paramvalue_type = c.POINTER(c.c_float)
        elif param_type == wrp_dt.m64p_type.M64TYPE_BOOL.name:
            paramvalue = c.byref(c.c_bool(paramvalue))
            paramvalue_type = c.POINTER(c.c_bool)
        elif param_type == wrp_dt.m64p_type.M64TYPE_STRING.name:
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
        '''This function sets the help string of one of the emulator's
        configuration parameters in the section which is represented by
        ConfigSectionHandle.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle and ParamName pointers cannot be NULL.
        PROTOTYPE:
         m64p_error ConfigSetParameterHelp(m64p_handle ConfigSectionHandle,
                    const char *ParamName, const char *ParamHelp)'''

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
        '''This function retrieves the value of one of the emulator's parameters
        in the section which is represented by ConfigSectionHandle.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle, ParamName and ParamValue pointers cannot be NULL.
        PROTOTYPE:
         m64p_error ConfigGetParameter(m64p_handle ConfigSectionHandle,
             const char *ParamName, m64p_type ParamType, void *ParamValue, int MaxSize)'''
        # TODO: Something is not right. Check if there are memory corruptions.
        paramvalue = None

        # First check type of the parameter
        param_type = self.ConfigGetParameterType(name)
        param_result = wrp_dt.m64p_type[param_type].value
        #print(wrp_dt.m64p_type(param_result), param_result)

        if param_type == wrp_dt.m64p_type.M64TYPE_INT.name:
            maxsize = c.sizeof(c.c_int(param_result))
            paramvalue = c.pointer(c.c_int())
        elif param_type == wrp_dt.m64p_type.M64TYPE_FLOAT.name:
            maxsize = c.sizeof(c.c_float(param_result))
            paramvalue = c.pointer(c.c_float())
        elif param_type == wrp_dt.m64p_type.M64TYPE_BOOL.name:
            # c_int to avoid INPUT_INVALID
            maxsize = c.sizeof(c.c_int(param_result))
            paramvalue = c.pointer(c.c_bool())
        elif param_type == wrp_dt.m64p_type.M64TYPE_STRING.name:
            maxsize = 512
            paramvalue = c.create_string_buffer(maxsize)
        else:
            log.warning("ConfigGetParameter: Unknown parameter type")

        function = wrp_dt.cfunc("ConfigGetParameter", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("ConfigSectionHandle", c.c_void_p, 2, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")),
                        ("ParamType", c.c_int, 1, param_result),
                        ("ParamValue", c.c_void_p, 1, paramvalue),
                        ("MaxSize", c.c_int, 1, maxsize))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            if param_type == wrp_dt.m64p_type.M64TYPE_STRING.name:
                return paramvalue.value.decode()
            else:
                return paramvalue.contents.value
        else:
            self.CoreErrorMessage(status, b"ConfigGetParameter")

    def ConfigExternalOpen(self, path):
        '''This function opens an external config file and reads the contents
        into memory.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - FileName cannot be NULL.
        PROTOTYPE:
         m64p_error ConfigExternalOpen(const char *FileName, m64p_handle *Handle)'''

        handle = c.c_void_p()
        function = wrp_dt.cfunc("ConfigExternalOpen", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("FileName", c.c_char_p, 1, path.encode("utf-8")),
                        ("Handle", c.c_void_p, 1, c.byref(handle)))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            # If everything is right, make wrapper remember this handle.
            self.config_ext_handle = handle.value
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigExternalOpen")

    def ConfigExternalClose(self):
        '''This function closes an external config file.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - Handle should have already been passed to ConfigExternalOpen().
        PROTOTYPE:
         m64p_error ConfigExternalClose(m64p_handle Handle)'''

        function = wrp_dt.cfunc("ConfigExternalClose", self.m64p_lib_core, wrp_dt.m64p_error,
                        ("Handle", c.c_void_p, 1, self.config_ext_handle))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, b"ConfigExternalClose")

    def ConfigExternalGetParameter(self, sectionname, paramname):
        '''This functions allows a plugin to leverage the built-in ini parser
        to read any cfg/ini file.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - Handle should have already been passed to ConfigExternalOpen.
        - The SectionName and ParamName pointers cannot be NULL.
        - ParamPtr must be a pre-allocated char array that is at least as large as ParamMaxLength.
        PROTOTYPE:
         m64p_error ConfigExternalGetParameter(m64p_handle Handle, const char *SectionName,
              const char *ParamName, char* ParamPtr, int ParamMaxLength)'''

        # Sets up a pre-allocated char array.
        maxlenght = 512
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
            string = paramptr.value.decode("utf-8")
            if string.startswith('"') and string.endswith('"'):
                # Removes quotes, if they are here
                return string[1:][:-1]
            else:
                return string
        else:
            self.CoreErrorMessage(status, b"ConfigExternalGetParameter")

    def ConfigGetParameterType(self, paramname):
        '''This function retrieves the type of one of the emulator's parameters
        in the section which is represented by ConfigSectionHandle.
        If there is no parameter with the given ParamName, the error
        M64ERR_INPUT_NOT_FOUND will be returned.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle, ParamName, and ParamType pointers cannot be NULL.
        PROTOTYPE:
         m64p_error ConfigGetParameterType(m64p_handle ConfigSectionHandle,
               const char *ParamName, m64p_type *ParamType)'''

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
        ''' This function retrieves the help information about one of the
        emulator's parameters in the section which is represented by
        ConfigSectionHandle.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle, and ParamName pointers cannot be NULL.
        PROTOTYPE:
         const char * ConfigGetParameterHelp(m64p_handle ConfigSectionHandle,
                const char *ParamName)'''
        function = wrp_dt.cfunc("ConfigGetParameterHelp", self.m64p_lib_core, c.c_char_p,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")))

        status = function()

        if status != None:
            return status.decode("utf-8")
        else:
            log.warning(f"No description is available for parameter {name}.")

    ##Special Get/Set Functions
    def ConfigSetDefaultInt(self, name, value, help):
        '''This function is used to set the value of a configuration parameter
        if it is not already present in the configuration file. This may happen
        if a new user runs the emulator, or an upgraded module uses a new
        parameter, or the user deletes his or her configuration file. If a
        parameter named ParamName is already present in the given section of the
        configuration file, then no action will be taken and this function will
        return successfully. Otherwise, a new parameter will be created its
        value will be assigned to ParamValue.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle and ParamName pointers cannot be NULL.
        PROTOTYPE:
         m64p_error ConfigSetDefaultInt(m64p_handle ConfigSectionHandle, const char *ParamName,
                int ParamValue, const char *ParamHelp)'''

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
        '''This function is used to set the value of a configuration parameter
        if it is not already present in the configuration file. This may happen
        if a new user runs the emulator, or an upgraded module uses a new
        parameter, or the user deletes his or her configuration file. If a
        parameter named ParamName is already present in the given section of the
        configuration file, then no action will be taken and this function will
        return successfully. Otherwise, a new parameter will be created its
        value will be assigned to ParamValue.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle and ParamName pointers cannot be NULL.
        PROTOTYPE:
         m64p_error ConfigSetDefaultFloat(m64p_handle ConfigSectionHandle,
               const char *ParamName, float ParamValue, const char *ParamHelp)'''

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
        '''This function is used to set the value of a configuration parameter
        if it is not already present in the configuration file. This may happen
        if a new user runs the emulator, or an upgraded module uses a new
        parameter, or the user deletes his or her configuration file. If a
        parameter named ParamName is already present in the given section of the
        configuration file, then no action will be taken and this function will
        return successfully. Otherwise, a new parameter will be created its
        value will be assigned to ParamValue.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle and ParamName pointers cannot be NULL.
        PROTOTYPE:
         m64p_error ConfigSetDefaultBool(m64p_handle ConfigSectionHandle, const char *ParamName,
               int ParamValue, const char *ParamHelp)'''

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
        '''This function is used to set the value of a configuration parameter
        if it is not already present in the configuration file. This may happen
        if a new user runs the emulator, or an upgraded module uses a new
        parameter, or the user deletes his or her configuration file. If a
        parameter named ParamName is already present in the given section of the
        configuration file, then no action will be taken and this function will
        return successfully. Otherwise, a new parameter will be created its
        value will be assigned to ParamValue.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle and ParamName pointers cannot be NULL.
        PROTOTYPE:
         m64p_error ConfigSetDefaultString(m64p_handle ConfigSectionHandle, const char *ParamName,
               const char * ParamValue, const char *ParamHelp)'''

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
        '''This function retrieves the value of one of the emulator's parameters
        in the section which is represented by ConfigSectionHandle, and returns
        the value directly to the calling function. If an errors occurs (such as
        if ConfigSectionHandle is invalid, or there is no configuration
        parameter named ParamName), then an error will be sent to the front-end
        via the DebugCallback() function, and either a 0 (zero) or an empty string
        will be returned.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle and ParamName pointers cannot be NULL.
        PROTOTYPE:
         int ConfigGetParamInt(m64p_handle ConfigSectionHandle, const char *ParamName)'''
        function = wrp_dt.cfunc("ConfigGetParamInt", self.m64p_lib_core, c.c_int,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")))

        status = function()

        if status:
            return status
        else:
            log.error(f"ConfigGetParamInt error: {name}")

    def ConfigGetParamFloat(self, name):
        '''This function retrieves the value of one of the emulator's parameters
        in the section which is represented by ConfigSectionHandle, and returns
        the value directly to the calling function. If an errors occurs (such as
        if ConfigSectionHandle is invalid, or there is no configuration
        parameter named ParamName), then an error will be sent to the front-end
        via the DebugCallback() function, and either a 0 (zero) or an empty string
        will be returned.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle and ParamName pointers cannot be NULL.
        PROTOTYPE:
         float ConfigGetParamFloat(m64p_handle ConfigSectionHandle, const char *ParamName)'''
        function = wrp_dt.cfunc("ConfigGetParamFloat", self.m64p_lib_core, c.c_float,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")))

        status = function()

        if status:
            return status
        else:
            log.error(f"ConfigGetParamFloat error:  {name}")

    def ConfigGetParamBool(self, name):
        '''This function retrieves the value of one of the emulator's parameters
        in the section which is represented by ConfigSectionHandle, and returns
        the value directly to the calling function. If an errors occurs (such as
        if ConfigSectionHandle is invalid, or there is no configuration
        parameter named ParamName), then an error will be sent to the front-end
        via the DebugCallback() function, and either a 0 (zero) or an empty string
        will be returned.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle and ParamName pointers cannot be NULL.
        PROTOTYPE:
         int ConfigGetParamBool(m64p_handle ConfigSectionHandle, const char *ParamName)'''

        function = wrp_dt.cfunc("ConfigGetParamBool", self.m64p_lib_core, c.c_int,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")))

        status = function()

        if status:
            return c_bool(status).value
        else:
            log.error(f"ConfigGetParamBool error: {name}")

    def ConfigGetParamString(self, name):
        '''This function retrieves the value of one of the emulator's parameters
        in the section which is represented by ConfigSectionHandle, and returns
        the value directly to the calling function. If an errors occurs (such as
        if ConfigSectionHandle is invalid, or there is no configuration
        parameter named ParamName), then an error will be sent to the front-end
        via the DebugCallback() function, and either a 0 (zero) or an empty string
        will be returned.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        - The ConfigSectionHandle and ParamName pointers cannot be NULL.
        PROTOTYPE:
         const char *ConfigGetParamString(m64p_handle ConfigSectionHandle, const char *ParamName)'''

        function = wrp_dt.cfunc("ConfigGetParamString", self.m64p_lib_core, c.c_char_p,
                        ("ConfigSectionHandle", c.c_void_p, 1, self.config_handle),
                        ("ParamName", c.c_char_p, 1, name.encode("utf-8")))

        status = function()

        if status != None:
            return status
        else:
            log.error(f"ConfigGetParamString error: {name}")

    ## OS-Abstraction Functions
    def ConfigGetSharedDataFilepath(self, string):
        ''' It is common for shared data files on Unix systems to be installed
        in different places on different systems. Therefore, this core function
        is provided to allow a plugin to retrieve a full pathname to a given
        shared data file. This type of file is intended to be shared among
        multiple users on a system, so it is likely to be read-only.
        Examples of these types of files include: the .ini files for Rice Video
        and Glide64, the font and Mupen64Plus.ini files for the core, and the
        cheat code files for the front-end. This function will first search in a
        directory given via the DataPath parameter to the CoreStartup function,
        then in a directory given by the SharedDataPath core configuration
        parameter, then in a directory which may be supplied at compile time
        through a Makefile or configure script option, and finally in some
        common system locations (such as /usr/share/mupen64plus and
        /usr/local/share/mupen64plus on Unix systems).
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        PROTOTYPE:
         const char * ConfigGetSharedDataFilepath(const char *filename)'''

        function = wrp_dt.cfunc("ConfigGetSharedDataFilepath", self.m64p_lib_core, c.c_char_p,
                         ("filename", c.c_char_p, 1, string.encode("utf-8")))
        filename = function()

        if type(filename) == bytes:
            return filename.decode("utf-8")
        else:
            return filename

    def ConfigGetUserConfigPath(self):
        '''This function may be used by the plugins or front-end to get a path
        to the directory for storing user-specific configuration files.
        This will be the directory where the configuration file
        "mupen64plus.cfg" is located.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        PROTOTYPE:
         const char * ConfigGetUserConfigPath(void)'''
        function = wrp_dt.cfunc("ConfigGetUserConfigPath", self.m64p_lib_core, c.c_char_p)
        filename = function()

        return filename.decode("utf-8")

    def ConfigGetUserDataPath(self):
        '''This function may be used by the plugins or front-end to get a path
        to the directory for storing user-specific data files. This may be used
        to store files such as screenshots, saved game states, or hi-res textures.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        PROTOTYPE:
         const char * ConfigGetUserDataPath(void)'''

        function = wrp_dt.cfunc("ConfigGetUserDataPath", self.m64p_lib_core, c.c_char_p)
        filename = function()

        return filename.decode("utf-8")

    def ConfigGetUserCachePath(self):
        ''' This function may be used by the plugins or front-end to get a path
        to the directory for storing user-specific caching data files. Files in
        this directory may be deleted by the user to save space, so critical
        information should not be stored here. This directory may be used to
        store files such as the ROM browser cache.
        REQUIREMENTS:
        - The Mupen64Plus library must already be initialized before calling this function.
        PROTOTYPE:
         const char * ConfigGetUserCachePath(void)'''

        function = wrp_dt.cfunc("ConfigGetUserCachePath", self.m64p_lib_core, c.c_char_p)
        filename = function()

        return filename.decode("utf-8")

    def PluginStartup(self, plugin, context):
        '''This function initializes plugin for use by allocating memory,
        creating data structures, and loading the configuration data.
        This function may return M64ERR_INCOMPATIBLE if an older core library
        is used with a newer plugin.
        REQUIREMENTS:
        - This function must be called before any other plugin functions.
        - The Core library must already be started before calling this function.
        - This function must be called before attaching the plugin to the core.
        PROTOTYPE:
         m64p_error PluginStartup(m64p_dynlib_handle CoreLibHandle, void *Context,
               void (*DebugCallback)(void *Context, int level, const char *Message))'''

        function = wrp_dt.cfunc("PluginStartup", plugin, wrp_dt.m64p_error,
                        ("CoreLibHandle", c.c_void_p, 1, c.c_void_p(self.m64p_lib_core._handle)),
                        ("Context", c.c_void_p, 2, context),
                        ("DebugCallback", c.c_void_p, 2, wrp_cb.CB_DEBUG))

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, f"PluginStartup: {wrp_dt.m64p_plugin_type(self.PluginGetVersion(plugin)['type']).name}")

    def PluginShutdown(self, plugin):
        '''This function destroys data structures and releases memory allocated
        by the plugin library.
        REQUIREMENTS:
        - This plugin should be detached from the core before calling this function.
        PROTOTYPE:
         m64p_error PluginShutdown(void)'''
        function = wrp_dt.cfunc("PluginShutdown", plugin, wrp_dt.m64p_error)

        function.errcheck = wrp_dt.m64p_errcheck
        status = function()

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return status
        else:
            self.CoreErrorMessage(status, f"PluginShutdown: {wrp_dt.m64p_plugin_type(self.PluginGetVersion(plugin)['type']).name}")
    #######CoreDoCommand commands #####
    def rom_open(self, rom_path):
        ''' This will cause the core to read in a binary ROM image provided by
        the front-end.
        REQUIREMENTS:
        - The emulator cannot be currently running.
        - A ROM image must not be currently opened.
        COMMAND:
         M64CMD_ROM_OPEN = 1'''

        try:
            with open(rom_path, "rb") as self.load_rom:
                self.read_rom = self.load_rom.read()
                self.rom_size = c.c_int(len(self.read_rom))
                #self.romtype = binascii.hexlify(rom[:4])
                self.rom_buffer = c.create_string_buffer(self.read_rom)

            status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_ROM_OPEN.value,
                                     self.rom_size, c.byref(self.rom_buffer))
        except FileNotFoundError as e:
            log.error(e)
            status = wrp_dt.m64p_error.M64ERR_FILES.value
            self.frontend.trigger_popup("error", str(e))

        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Opening of ROM file has failed!")

        return status

    def rom_close(self):
        ''' This will close any currently open ROM.
        The current cheat code list will also be deleted.
        REQUIREMENTS:
        - The emulator cannot be currently running.
        - A ROM image must have been previously opened.
        - There should be no plugins currently attached.
        COMMAND:
         M64CMD_ROM_CLOSE = 2'''

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_ROM_CLOSE.value, c.c_int(), c.c_void_p())

        # Make sure everything is cleaned
        self.load_rom = None
        self.read_rom = None
        self.rom_size = None
        self.rom_buffer = None

        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Closing of ROM file has failed!")
        return status

    def __check_length(self, crc):
        # Make sure a CRC hash has exactly 8 digits, because some hash may have
        # initial zeroes that are automatically stripped by the core library.
        if len(crc) < 8:
            fixed_crc = f"{(8 - len(crc)) * '0'}{crc}"
            return fixed_crc
        else:
            return crc

    def rom_get_header(self):
        '''This will retrieve the header data of the currently open ROM.
        REQUIREMENTS:
        -  A ROM image must be open.
        COMMAND:
         M64CMD_ROM_GET_HEADER = 3'''
        # TODO: Almost all outputs are raw (in integer). How to convert them to string?

        header = None
        country = None

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_ROM_GET_HEADER.value, \
                        c.c_int(c.sizeof(self.rom_header)), c.pointer(self.rom_header))

        # Those values are just super-technical numbers and cannot be decoded.
        lat = self.rom_header.init_PI_BSB_DOM1_LAT_REG
        pgs1 = self.rom_header.init_PI_BSB_DOM1_PGS_REG
        pwd = self.rom_header.init_PI_BSB_DOM1_PWD_REG
        pgs2 =self.rom_header.init_PI_BSB_DOM1_PGS_REG2
        clockrate = self.rom_header.ClockRate
        pc = self.rom_header.PC

        # This refers to the version of libultra, used for compiling the ROM
        release_raw = self.rom_header.Release
        release = bytes(c.cast(release_raw, c.c_char_p)).decode("cp932", "replace")

        # Since mupen64plus reads the rom in little endian order, and the ROM
        # could be in big endian order, so let's byteswap the CRCs in that order.
        crc1 = self.__check_length(hex(int.from_bytes(self.rom_header.CRC1.to_bytes(4, byteorder='little'),
                        byteorder='big', signed=False)).lstrip("0x").rstrip("L")).upper()
        crc2 = self.__check_length(hex(int.from_bytes(self.rom_header.CRC2.to_bytes(4, byteorder='little'),
                        byteorder='big', signed=False)).lstrip("0x").rstrip("L")).upper()

        # The internal name is NUL-terminated.
        # XXX: We currently remove this NUL bit. For the sake of completeness, we currently remove this NUL bit. Or should we not?
        raw_name = self.rom_header.Name[:]
        i = 0
        for value in raw_name:
            if raw_name[i] == 0:
                raw_name[i] = 32
            i += 1

        # The internal name is also codified in ms-kanji, so let's decode this way.
        name = bytes(raw_name).decode('cp932', 'replace')
        country_raw = self.rom_header.Country_code
        # Game revision, format in hex without 0x
        revision = f"1.{format(country_raw >> 8, 'x')}"

        # Have to convert hexadecimal to int, because Python treats hex as str...
        country_code = int(hex(country_raw & 0xFF), base=16)

        # Map the codes with known regions
        cartridge_region = ""
        cartridge_letter = ""
        if country_code == 0x37:
            # 7, BETA
            #country = 'ꞵ'
            pass
        elif country_code == 0x41:
            # A, asian NTSC
            country = 'JU'
        elif country_code == 0x42:
            # Brazil
            country = 'B'
            cartridge_region = "BRA"
            cartridge_letter = "B"
        elif country_code == 0x43:
            # China
            country = 'Ch'
            cartridge_region = "CHN" # Unofficial?
            cartridge_letter = "C"
        elif country_code == 0x44:
            # Germany
            country = 'G'
            cartridge_region = "NOE" # Nintendo of Europe, located in Germany
            cartridge_letter = "D" # Deutsch
        elif country_code == 0x45:
            # USA
            country = 'U'
            cartridge_region = "USA"
            cartridge_letter = "E" # As in 'English language of the NTSC version', for North America.
        elif country_code == 0x46:
            # France
            country = 'F'
            cartridge_region = "FRA"
            cartridge_letter = "F"
        elif country_code == 0x47:
            # 'G': Gateway 64 (NTSC)
            pass
        elif country_code == 0x48:
            # 'H' "Netherlands/Holland"
            pass
        elif country_raw == 0x49:
            # Italy
            country = 'I'
            cartridge_region = "ITA"
            cartridge_letter = "I"
        elif country_code == 0x4A:
            # Japan
            country = 'J'
            cartridge_region = "JPN"
            cartridge_letter = "J"
        elif country_code == 0x4B:
            # K, Korea
            pass
        elif country_code == 0x4C:
            # 'L': Gateway 64 (PAL)
            pass
        elif country_code == 0x4E:
            # 'N' "Canada"
            pass
        elif country_code == 0x50 or country_code == 0x58 or country_code == 0x59:
            # Europe
            # 0x50 = standard, 0x58 = region X, 0x59 = region Y
            country = 'E'
            cartridge_region = "EUR"
            cartridge_letter = "P" # As in "PAL region"
        elif country_code == 0x53:
            # Spain
            country = 'S'
            cartridge_region = "ESP" # España
            cartridge_letter = "S"
        elif country_code == 0x55:
            # 'U', Australia
            country = 'A'
            cartridge_region = "AUS"
            cartridge_letter = "P" # As in "PAL region"
        else:
            log.debug(f"Code country: {country_raw}")
            country = 'Unk'
            log.warning(f'Unknown region for {name}.')

        cartridge_bit = bytes(c.cast(self.rom_header.Cartridge_ID, c.c_char_p)).decode("cp932", "replace").rstrip("\x00")

        # There are exceptions, though...
        if crc1 == "E48E01F5" and crc2 == "E6E51F9B":
            # Carmageddon 64 (E) (M4) (Eng-Spa-Fre-Ita) [!]
            cartridge_letter = "Y"
        elif crc1 == "580162EC" and crc2 == "E3108BF1":
            # Carmageddon 64 (E) (M4) (Eng-Spa-Fre-Ger) [!]
            cartridge_letter = "X"
            cartridge_region = "EUU"
        elif crc1 == "874733A4" and crc2 == "A823745A":
            # Gex 3 - Deep Cover Gecko (E) (M2) (Fre-Ger) [!]
            cartridge_letter = "X"
            cartridge_region = "EUU"
        elif crc1 == "72611D7D" and crc2 == "9919BDD2":
            # HSV Adventure Racing (A) [!]
            cartridge_letter = "X"
        elif crc1 == "336364A0" and crc2 == "06C8D5BF":
            # International Superstar Soccer 2000 (E) (M2) (Eng-Ger) [!]
            cartridge_letter = "X"
        elif crc1 == "BAE8E871" and crc2 == "35FF944E":
            # International Superstar Soccer 2000 (E) (M2) (Fre-Ita) [!]
            cartridge_letter = "Y"
            cartridge_region = "EUU"
        elif crc1 == "E36166C2" and crc2 == "8613A2E5":
            # Michael Owens WLS 2000 (E) [!]
            cartridge_region = "UKV"
            cartridge_letter = "X"
        if crc1 == "D84EEA84" and crc2 == "45B2F1B4":
            # Shadowgate 64 - Trials Of The Four Towers (E) [!]
            cartridge_region = "UKV"
        elif crc1 == "02B46F55" and crc2 == "61778D0B":
            # Shadowgate 64 - Trials Of The Four Towers (E) (M2) (Ita-Spa) [!]
            cartridge_letter = "Y"
            cartridge_region = "ITA" # And the spanish version?
        elif crc1 == "2BC1FCF2" and crc2 == "7B9A0DF4":
            # Shadowgate 64 - Trials Of The Four Towers (E) (M3) (Fre-Ger-Dut) [!]
            cartridge_letter = "X"
        elif crc1 == "B6BE20A5" and crc2 == "FACAF66D":
            # Turok - Rage Wars (E) (M3) (Eng-Fre-Ita) [!]
            pass

        manufacturer_raw = bytes(c.cast(self.rom_header.Manufacturer_ID,
                                 c.c_char_p)).decode("cp932", "replace").lstrip("\x00").rstrip("\x00")
        if manufacturer_raw == "N":
            manufacturer = "N64 cartridge"
        elif manufacturer_raw == "C":
            manufacturer = "Cartridge part of N64DD combo"
        elif manufacturer_raw == "E":
            # "E" as in "Expansion"?
            manufacturer = "Disk part of N64DD combo"
        elif manufacturer_raw == "Z":
            manufacturer = "Arcade (Aleck64)"
        else:
            manufacturer = "Unknown"

        if country_code == 0x41:
            cartridge = f'NUS-{manufacturer_raw}{cartridge_bit}E-USA/NUS-{manufacturer_raw}{cartridge_bit}J-JPN'
        else:
            cartridge = f'NUS-{manufacturer_raw}{cartridge_bit}{cartridge_letter}-{cartridge_region}'

        header = {"lat": lat, "pgs1": pgs1, "pwd": pwd, "pgs2": pgs2,
                  "clockrate": clockrate, "pc": pc, "release": release,
                  "crc1": crc1, "crc2": crc2, "internalname": name,
                  "manufacturer": manufacturer, "cartridge": cartridge,
                  "country": country, "revision": revision}

        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Couldn't retrieve the ROM's header.")
            return status
        else:
            return header

    def rom_get_header_raw(self):
        # M64CMD_ROM_GET_HEADER = 3
        # XXX: In case anyone needs or prefer the raw values of the header...
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_ROM_GET_HEADER.value,
                        c.c_int(c.sizeof(self.rom_header)), c.pointer(self.rom_header))

        header = None

        lat = self.rom_header.init_PI_BSB_DOM1_LAT_REG
        pgs1 = self.rom_header.init_PI_BSB_DOM1_PGS_REG
        pwd = self.rom_header.init_PI_BSB_DOM1_PWD_REG
        pgs2 =self.rom_header.init_PI_BSB_DOM1_PGS_REG2
        clockrate = self.rom_header.ClockRate
        pc = self.rom_header.PC
        release = self.rom_header.Release
        crc1 = self.rom_header.CRC1
        crc2 = self.rom_header.CRC2
        name = self.rom_header.Name
        manufacturer = self.rom_header.Manufacturer_ID
        cartridge = self.rom_header.Cartridge_ID
        country_raw = self.rom_header.Country_code
        # Game revision, format in hex without 0x
        revision = format(country_raw >> 8, 'x')

        # Have to convert hexadecimal to int, because Python treats hex as str...
        country = int(hex(country_raw & 0xFF), base=16)

        header = {"lat": lat, "pgs1": pgs1, "pwd": pwd, "pgs2": pgs2,
                  "clockrate": clockrate, "pc": pc, "release": release,
                  "crc1": crc1, "crc2": crc2, "internalname": name,
                  "manufacturer": manufacturer, "cartridge": cartridge,
                  "country": country, "revision": revision}

        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Couldn't retrieve the ROM's header.")
            return status
        else:
            return header

    def rom_get_settings(self):
        # M64CMD_ROM_GET_SETTINGS = 4

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_ROM_GET_SETTINGS.value,
                        c.c_int(c.sizeof(self.rom_settings)), c.pointer(self.rom_settings))

        name = self.rom_settings.goodname.decode("utf-8")

        md5 = self.rom_settings.MD5.decode("utf-8")
        savetype_raw = self.rom_settings.savetype
        if savetype_raw == 0:
            savetype = "EEPROM 4 kb"
        elif savetype_raw == 1:
            savetype = "EEPROM 16 kb"
        elif savetype_raw == 2:
            savetype = "SRAM 256 kb"
        elif savetype_raw == 3:
            savetype = "FlashRAM 1 Mb"
        elif savetype_raw == 4:
            #TODO: what's this value for? controller pak maybe? or it's SRAM 768 kb for dezaemon 3d?
            #savetype = "Controller Pak 2 Mb"
            savetype = savetype_raw
        elif savetype_raw == 5:
            savetype = "None"
        else:
            savetype = savetype_raw

        m64pstatus = self.rom_settings.status
        players = self.rom_settings.players
        rumble = bool(self.rom_settings.rumble)
        transferpak = bool(self.rom_settings.transferpak)
        mempak = bool(self.rom_settings.mempak)
        biopak = bool(self.rom_settings.biopak)

        settings = {"goodname": name, "md5": md5, "savetype": savetype,
                    "status": m64pstatus, "players": players, "rumble": rumble,
                    "transferpak": transferpak, "mempak": mempak, "biopak": biopak}

        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Couldn't retrieve the ROM's settings.")
            return status
        else:
            #print(settings)
            return settings

    def rom_get_settings_raw(self):
        #M64CMD_ROM_GET_SETTINGS = 4
        # XXX: In case anyone needs or prefer the raw values of the settings...

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_ROM_GET_SETTINGS.value,
                        c.c_int(c.sizeof(self.rom_settings)), c.pointer(self.rom_settings))

        name = self.rom_settings.goodname

        md5 = self.rom_settings.MD5
        savetype = self.rom_settings.savetype
        m64pstatus = self.rom_settings.status
        players = self.rom_settings.players
        rumble = self.rom_settings.rumble
        transferpak = self.rom_settings.transferpak
        mempak = self.rom_settings.mempak
        biopak = self.rom_settings.biopak

        settings = {"goodname": name, "md5": md5, "savetype": savetype,
                    "status": m64pstatus, "players": players, "rumble": rumble,
                    "transferpak": transferpak, "mempak": mempak, "biopak": biopak}

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            return settings
        else:
            log.error("CoreDoCommand: Couldn't retrieve the ROM's settings.")
            return status

    def execute(self):
        # M64CMD_EXECUTE = 5
        response = True
        self.emulating = True
        self.running = True
        if "dummy" in [self.gfx_filename, self.audio_filename, self.input_filename, self.rsp_filename]:
            # TODO: assertion 'GDK_IS_FRAME_CLOCK (clock)' failed
            response = self.frontend.trigger_popup("question",f"One of the plugins is set on 'dummy', which means the game won't work properly. \nDo you still want to run it?", "dummy")

        if response == True:
            status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_EXECUTE.value, c.c_int(), c.c_void_p())
        else:
            status = wrp_dt.m64p_error.M64ERR_PLUGIN_FAIL.value

        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            pass
        else:
            self.emulating = False
            self.running = False
            log.error("CoreDoCommand: Unable to execute")
        return status

    def stop(self):
        # M64CMD_STOP = 6
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_STOP.value, c.c_int(), c.c_void_p())
        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            self.emulating = False
            self.running = False
        else:
            log.error("CoreDoCommand: Unable to stop emulation")
        return status

    def pause(self):
        # M64CMD_PAUSE = 7
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_PAUSE.value, c.c_int(), c.c_void_p())
        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            self.running = False
        else:
            log.error("CoreDoCommand: Unable to pause emulation")
        return status

    def resume(self):
        # M64CMD_RESUME = 8
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_RESUME.value, c.c_int(), c.c_void_p())
        if status == wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            self.running = True
        else:
            log.error("CoreDoCommand: Unable to resume emulation")
        return status

    def core_state_query(self, state):
        # M64CMD_CORE_STATE_QUERY = 9
        ## M64CORE_EMU_STATE, M64CORE_VIDEO_MODE, M64CORE_SAVESTATE_SLOT, M64CORE_SPEED_FACTOR,
        ## M64CORE_SPEED_LIMITER, M64CORE_VIDEO_SIZE, M64CORE_AUDIO_VOLUME, M64CORE_AUDIO_MUTE,
        ## M64CORE_INPUT_GAMESHARK, M64CORE_STATE_LOADCOMPLETE, M64CORE_STATE_SAVECOMPLETE

        state_query = c.pointer(c.c_int())
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_CORE_STATE_QUERY.value,
                                c.c_int(state), c.byref(state_query))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Unable to query the core")
        return state_query.contents.value

    def state_load(self, path=None):
        # M64CMD_STATE_LOAD = 10
        if path != None:
            path_param = path.encode('utf-8')
        else:
            path_param = c.c_char_p()
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_STATE_LOAD.value,
                                     c.c_int(), path_param)
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Unable to load the state save")
        return status

    def state_save(self, path=None, save_type=1):
        # M64CMD_STATE_SAVE = 11
        # 1 = m64p state save, 2= pj64 compressed, 3= pj64 uncompressed
        if path != None:
            path_param = path.encode('utf-8')
        else:
            path_param = c.c_char_p()
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_STATE_SAVE.value,
                                     c.c_int(save_type), path_param)
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Unable to make a state save")
        return status

    def state_set_slot(self, slot):
        # M64CMD_STATE_SET_SLOT = 12

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_STATE_SET_SLOT.value,
                                     c.c_int(slot), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Unable to change the state save slot")
        else:
            self.current_slot = slot
        return status

    def send_sdl_keydown(self, key):
        # M64CMD_SEND_SDL_KEYDOWN = 13
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_SEND_SDL_KEYDOWN.value,
                                     c.c_int(key), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Unable to send SDL key down signal")
        return status

    def send_sdl_keyup(self, key):
        # M64CMD_SEND_SDL_KEYUP = 14
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_SEND_SDL_KEYUP.value,
                                     c.c_int(key), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Unable to send SDL key up signal")
        return status

    def set_frame_callback(self, frame_cb):
        # M64CMD_SET_FRAME_CALLBACK = 15
        # TODO: UNTESTED, int is ignored, pointer to m64p_frame_callback object
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_SET_FRAME_CALLBACK.value,
                                     c.c_int(), c.byref(frame_cb))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Unable to set up the frame callback")
        return status

    def take_next_screenshot(self):
        # M64CMD_TAKE_NEXT_SCREENSHOT = 16

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_TAKE_NEXT_SCREENSHOT.value,
                                     c.c_int(), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Unable to take screenshot")
        return status

    def core_state_set(self, state, value):
        # M64CMD_CORE_STATE_SET = 17
        ## M64CORE_EMU_STATE, M64CORE_VIDEO_MODE, M64CORE_SAVESTATE_SLOT, M64CORE_SPEED_FACTOR,
        ## M64CORE_SPEED_LIMITER, M64CORE_VIDEO_SIZE, M64CORE_AUDIO_VOLUME, M64CORE_AUDIO_MUTE,
        ## M64CORE_INPUT_GAMESHARK, M64CORE_STATE_LOADCOMPLETE, M64CORE_STATE_SAVECOMPLETE

        valueptr = c.pointer(c.c_int(value))
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_CORE_STATE_SET.value,
                                     c.c_int(state), valueptr)
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error(f"CoreDoCommand: Unable to set the core state, error is {wrp_dt.m64p_error(status).name}")
        return valueptr.contents.value

    def read_screen(self, buffer_type, buffer_ptr):
        # M64CMD_READ_SCREEN = 18
        # TODO: UNTESTED
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_READ_SCREEN.value,
                            c.c_int(buffer_type), c.byref(c.c_void_p(buffer_ptr)))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Unable to read the screen")
        return status

    def reset(self, reset):
        # M64CMD_RESET = 19
        ## reset: soft = 0, hard = 1
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_RESET.value, c.c_int(reset))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Unable to reset emulation")
        return status

    def advance_frame(self):
        # M64CMD_ADVANCE_FRAME = 20

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_ADVANCE_FRAME.value,
                                    c.c_int(), c.c_void_p())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Unable to advance by one frame")
        return status

    def set_media_loader(self):
        # M64CMD_SET_MEDIA_LOADER = 21

        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_SET_MEDIA_LOADER.value,
                                 c.c_int(c.sizeof(self.media_loader)), c.byref(self.media_loader))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            log.error("CoreDoCommand: Unable to set the media loader. This means that the Transfer Pak or the 64DD won't work.")
        return status

    def netplay_init(self, port, hostname):
        # M64CMD_NETPLAY_INIT = 22
        # TODO: Untested
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_NETPLAY_INIT.value,
                                 c.c_int(port), c.byref(c.create_string_buffer(hostname)))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            self.CoreErrorMessage(status, b"NETPLAY_INIT")
            log.error("CoreDoCommand: Unable to initiate the Netplay subsystem.")
        return status

    def netplay_control_player(self, controller):
        # M64CMD_NETPLAY_CONTROL_PLAYER = 23
        # TODO: Untested
        registration_id = c.c_uint32()
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_NETPLAY_CONTROL_PLAYER.value,
                                 c.c_int(controller), c.byref(registration_id))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            self.CoreErrorMessage(status, b"CONTROL_PLAYER")
            log.error("CoreDoCommand: The server has rejected your request for controller {controller}.")
        return status

    def netplay_get_version(self, frontend_api):
        # M64CMD_NETPLAY_GET_VERSION = 24
        # TODO: Untested
        server_api = c.c_uint32()
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_NETPLAY_GET_VERSION.value,
                                     c.c_int(frontend_api), c.byref(server_api))
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            self.CoreErrorMessage(status, b"NETPLAY_GET_VERSION")
            log.error(f"CoreDoCommand: Netplay API version mismatch between client and server!")
        return status

    def netplay_close(self):
        # M64CMD_NETPLAY_CLOSE = 25
        # TODO: Untested
        status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_NETPLAY_CLOSE.value,
                                     c.c_int(), c.byref())
        if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
            self.CoreErrorMessage(status, b"NETPLAY_CLOSE")
            log.error(f"CoreDoCommand: Unable to close any connections to server or shutdown the Netplay subsystem.")
        return status

    def pif_open(self, pif_path):
        # M64CMD_PIF_OPEN = 26
        with open(pif_path, "rb") as self.load_pif:
            self.read_pif = self.load_pif.read()
            self.pif_size = len(self.read_pif)
            self.pif_buffer = c.create_string_buffer(self.read_pif)

        if self.pif_size == 2048:
            status = self.CoreDoCommand(wrp_dt.m64p_command.M64CMD_PIF_OPEN.value,
                                     c.c_int(self.pif_size), c.byref(self.pif_buffer))

            if status != wrp_dt.m64p_error.M64ERR_SUCCESS.value:
                log.error("CoreDoCommand: Opening of PIF ROM file has failed!")
            return status
        else:
            log.error("CoreDoCommand: PIF ROM file is not of the right size!")
            return wrp_dt.m64p_error.M64ERR_FILES.value

    ####################

    def get_cic(self, country):
        crc = zlib.crc32(self.read_rom[0x40:0x1000])
        if crc in crc_to_cic:
           return crc_to_cic[crc]["ntsc-name"] if country in ["U", "J", "JU"] \
                    else crc_to_cic[crc]["pal-name"]
        else:
           return crc_to_cic[0]

    def preload(self):
        try:
            self.m64p_lib_core = self.load_module(self.m64p_lib_core_path)

            check_core = self.PluginGetVersion(self.m64p_lib_core)
            if check_core["version"] >= self.core_version:
                self.compatible = True

        except:
            log.error("Core: mupen64plus library hasn't been found")
            self.lock = True

    def plugins_startup(self):
        if self.gfx_filename != "dummy":
            self.PluginStartup(self.m64p_lib_gfx, b"gfx")
        if self.audio_filename != "dummy":
            self.PluginStartup(self.m64p_lib_audio, b"audio")
        if self.input_filename != "dummy":
            self.PluginStartup(self.m64p_lib_input, b"input")
        if self.rsp_filename != "dummy":
            self.PluginStartup(self.m64p_lib_rsp, b"rsp")

    def plugins_shutdown(self):
        if self.gfx_filename != "dummy":
            self.PluginShutdown(self.m64p_lib_gfx)
        if self.audio_filename != "dummy":
            self.PluginShutdown(self.m64p_lib_audio)
        if self.input_filename != "dummy":
            self.PluginShutdown(self.m64p_lib_input)
        if self.rsp_filename != "dummy":
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
                self.m64p_lib_gfx = self.load_module(f'{self.plugins_dir}{os.sep}{self.gfx_filename}{self.extension_filename}')
            except:
                log.error(f"{self.gfx_filename}: Plugin cannot be used. Dummy plugin is used instead, which means no video.")
                self.gfx_filename = "dummy"

        if self.audio_filename != "dummy":
            try:
                self.m64p_lib_audio = self.load_module(f'{self.plugins_dir}{os.sep}{self.audio_filename}{self.extension_filename}')
            except:
                if self.audio_filename == "mupen64plus-audio-sdl":
                    log.error(f"{self.audio_filename}: Plugin cannot be used. Dummy plugin is used instead, which means no audio.")
                    self.audio_filename = "dummy"
                else:
                    #TODO: What if even the default plugin fails?
                    log.error(f"{self.audio_filename}: Plugin not found, cannot be used. Default plugin is used instead.")
                    self.m64p_lib_audio = self.load_module(f'{self.plugins_dir}{os.sep}mupen64plus-audio-sdl{self.extension_filename}')

        if self.input_filename != "dummy":
            try:
                self.m64p_lib_input = self.load_module(f'{self.plugins_dir}{os.sep}{self.input_filename}{self.extension_filename}')
            except:
                log.error(f"{self.input_filename}: Plugin not found, cannot be used. Default plugin is used instead.")
                self.m64p_lib_input = self.load_module(f'{self.plugins_dir}{os.sep}mupen64plus-input-sdl{self.extension_filename}')

        if self.rsp_filename != "dummy":
            try:
                self.m64p_lib_rsp = self.load_module(f'{self.plugins_dir}{os.sep}{self.rsp_filename}{self.extension_filename}')
            except:
                log.error(f"{self.rsp_filename}: Plugin not found, cannot be used. Default plugin is used instead.")
                self.m64p_lib_rsp = self.load_module(f'{self.plugins_dir}{os.sep}mupen64plus-rsp-hle{self.extension_filename}')

    def initialise(self):
        if self.compatible == True:
            self.CoreStartup(self.frontend_api_version)
            log.debug(self.ConfigGetSharedDataFilepath("mupen64plus.ini"))
            log.debug(self.ConfigGetUserConfigPath())
            log.debug(self.ConfigGetUserDataPath())
            log.debug(self.ConfigGetUserCachePath())

            self.plugins_preload()
            self.plugins_startup()

        else:
            log.error("Error! Either the actual core is not compatible or something has gone wrong.")

    def run(self, rom):
        if self.vext_override == True:
            wrp_vext.enable_vidext()
            log.debug("Core: Vidext is enabled!")
        else:
            wrp_vext.disable_vidext()
            log.debug("Core: Vidext is not enabled.")
        self.CoreOverrideVidExt()

        retval = self.rom_open(rom)
        if retval == 0:
            header = self.rom_get_header() ###
            self.rom_get_settings() ###
            # TODO: Asia, Brazil
            if header["country"] in ("U", "J", "UJ"):
                pif_region = "PifNtscPath"
            elif header["country"] in ("A", "E", "F", "G", "I", "S"):
                pif_region = "PifPalPath"
            else:
                pif_region = None
            if pif_region is not None:
                self.pif_open(self.frontend.frontend_conf.get("Frontend", pif_region))
            self.plugins_attach()
            self.set_media_loader()
            if self.frontend.cheats:
                self.frontend.cheats.set_game(header["crc1"], header["crc2"], header["country"])
                self.frontend.cheats.dispatch()
            self.execute()
            if self.frontend.cheats:
                self.frontend.cheats.clean()
            self.plugins_detach()
            self.rom_close()

    def __restart(self, m64p_lib_core):
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
        try:
            p = pathlib.Path(self.plugins_dir)
            directory = p.glob(f'mupen64plus*{self.extension_filename}*')

            for plugin in sorted(directory):
                try:
                    # x.name takes the file's name from the path
                    filename = os.path.splitext(plugin.name)[0]
                    info = self.PluginGetVersion(self.load_module(f'{self.plugins_dir}{filename}{self.extension_filename}'))
                    log.debug(info)
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
                        log.error("Unknown plugin")
                except OSError as e:
                    log.warning(f"{filename}: Plugin not working or not compatible, skipping it. \n > {e}")
                    #TODO: It's not that good to have the popup this early, before main window.
                    self.frontend.trigger_popup("warning", f"{filename}: Plugin not working or not compatible, skipping it. \nReason: {e}")
        except (AttributeError, TypeError) as e:
            log.error(f"The plugin directory is NOT FOUND! gom64p needs this directory to work properly. \n > {e}")

    def load_module(self, path):
        if self.platform == 'Windows':
            os.chdir(self.plugins_dir)
            c.windll.kernel32.SetDllDirectoryW(self.plugins_dir)
            dylib = c.cdll.LoadLibrary(path)
            os.chdir(self.frontend.m64p_dir)
            try:
                # gom64p creates a temp folder and stores path in _MEIPASS
                c.windll.kernel32.SetDllDirectoryW(sys._MEIPASS)
            except AttributeError:
                c.windll.kernel32.SetDllDirectoryW(os.path.abspath("."))

            return dylib
        else:
            return c.cdll.LoadLibrary(path)
