#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

import enum
import ctypes as c

def m64p_errcheck(retval, function, args):
    if retval and function:
        return retval.value

# Create a custom Enum so that it can return a c_int value
class EnumC(enum.Enum):
    @property
    def from_param(cls, data):
        return c.c_int(encode_flags(self.flags, data))

# Make function prototypes a bit easier to declare
def cfunc(name, dll, result, *args):
    '''Build and apply a ctypes prototype complete with parameter flags.
       Example: function = cfunc("DllFunction", dll, c_int, ("Parameter", POINTER(c_char_p), 1, "Example")) '''
    atypes = []
    aflags = []
    for arg in args:
        atypes.append(arg[1])
        aflags.append((arg[2], arg[0]) + arg[3:])
    return c.CFUNCTYPE(result, *atypes)((name, dll), tuple(aflags))

#class EnumC(IntEnum):
#    """A ctypes-compatible IntEnum superclass."""
#    @classmethod
#    def from_param(cls, obj):
#        return int(obj)

####################################  m64p_types.h ####################################

# typedef void * m64p_handle;
def m64p_handle(handle):
    return c.c_void_p(handle._handle)

# typedef void * m64p_dynlib_handle;
def m64p_dynlib_handle(handle):
    return c.c_void_p(handle._handle)

# typedef void (*m64p_function)(void);
def m64p_function(handle):
    function = c.CFUNCTYPE(c.c_void_p)(("m64p_function", m64p_dynlib_handle(handle)))
    return function

# typedef void (*m64p_frame_callback)(unsigned int FrameIndex);
def m64p_frame_callback(handle, frame):
    cb = c.CFUNCTYPE(c.c_void_p, c.c_int)(("m64p_frame_callback", m64p_dynlib_handle(handle)), (frame))
    return cb

# typedef void (*m64p_input_callback)(void);
def m64p_input_callback():
    cb = c.CFUNCTYPE(c.c_void_p)(("m64p_input_callback", m64p_dynlib_handle(handle)))
    return cb
# typedef void (*m64p_audio_callback)(void);
def m64p_audio_callback():
    cb = c.CFUNCTYPE(c.c_void_p)(("m64p_audio_callback", m64p_dynlib_handle(handle)))
    return cb
# typedef void (*m64p_vi_callback)(void);
def m64p_vi_callback():
    cb = c.CFUNCTYPE(c.c_void_p)(("m64p_vi_callback", m64p_dynlib_handle(handle)))
    return cb

# 1° void = no return, 2° void = no args

class m64p_type(EnumC):
    M64TYPE_INT = 1
    M64TYPE_FLOAT = 2
    M64TYPE_BOOL = 3
    M64TYPE_STRING = 4

class m64p_msg_level(EnumC):
    M64MSG_ERROR = 1
    M64MSG_WARNING = 2
    M64MSG_INFO = 3
    M64MSG_STATUS = 4
    M64MSG_VERBOSE = 5

class m64p_error(EnumC):
    M64ERR_SUCCESS = 0
    M64ERR_NOT_INIT = 1        # Function is disallowed before InitMupen64Plus() is called
    M64ERR_ALREADY_INIT = 2    # InitMupen64Plus() was called twice
    M64ERR_INCOMPATIBLE = 3    # API versions between components are incompatible
    M64ERR_INPUT_ASSERT = 4    # Invalid parameters for function call, such as ParamValue=NULL for GetCoreParameter()
    M64ERR_INPUT_INVALID = 5   # Invalid input data, such as ParamValue="maybe" for SetCoreParameter() to set a BOOL-type value
    M64ERR_INPUT_NOT_FOUND = 6 # The input parameter(s) specified a particular item which was not found
    M64ERR_NO_MEMORY = 7       # Memory allocation failed
    M64ERR_FILES = 8           # Error opening, creating, reading, or writing to a file
    M64ERR_INTERNAL = 9        # Internal error (bug)
    M64ERR_INVALID_STATE = 10  # Current program state does not allow operation
    M64ERR_PLUGIN_FAIL = 11    # A plugin function returned a fatal error
    M64ERR_SYSTEM_FAIL = 12    # A system function call, such as an SDL or file operation, failed
    M64ERR_UNSUPPORTED = 13    # Function call is not supported (ie, core not built with debugger)
    M64ERR_WRONG_TYPE = 14     # A given input type parameter cannot be used for desired operation

class m64p_core_caps(EnumC):
    M64CAPS_DYNAREC = 1
    M64CAPS_DEBUGGER = 2
    M64CAPS_CORE_COMPARE = 4

class m64p_plugin_type(EnumC):
    M64PLUGIN_NULL = 0
    M64PLUGIN_RSP = 1
    M64PLUGIN_GFX = 2
    M64PLUGIN_AUDIO = 3
    M64PLUGIN_INPUT = 4
    M64PLUGIN_CORE = 5

class m64p_emu_state(EnumC):
    M64EMU_STOPPED = 1
    M64EMU_RUNNING = 2
    M64EMU_PAUSED = 3

class m64p_video_mode(EnumC):
    M64VIDEO_NONE = 1
    M64VIDEO_WINDOWED = 2
    M64VIDEO_FULLSCREEN = 3

class m64p_video_flags(EnumC):
    M64VIDEOFLAG_NO_FLAGS = 0 #not official
    M64VIDEOFLAG_SUPPORT_RESIZING = 1

class m64p_core_param(EnumC):
    M64CORE_EMU_STATE = 1
    M64CORE_VIDEO_MODE = 2
    M64CORE_SAVESTATE_SLOT = 3
    M64CORE_SPEED_FACTOR = 4
    M64CORE_SPEED_LIMITER = 5
    M64CORE_VIDEO_SIZE = 6
    M64CORE_AUDIO_VOLUME = 7
    M64CORE_AUDIO_MUTE = 8
    M64CORE_INPUT_GAMESHARK = 9
    M64CORE_STATE_LOADCOMPLETE = 10
    M64CORE_STATE_SAVECOMPLETE = 11

class m64p_command(EnumC):
    M64CMD_NOP = 0
    M64CMD_ROM_OPEN = 1
    M64CMD_ROM_CLOSE = 2
    M64CMD_ROM_GET_HEADER = 3
    M64CMD_ROM_GET_SETTINGS = 4
    M64CMD_EXECUTE = 5
    M64CMD_STOP = 6
    M64CMD_PAUSE = 7
    M64CMD_RESUME = 8
    M64CMD_CORE_STATE_QUERY = 9
    M64CMD_STATE_LOAD = 10
    M64CMD_STATE_SAVE = 11
    M64CMD_STATE_SET_SLOT = 12
    M64CMD_SEND_SDL_KEYDOWN = 13
    M64CMD_SEND_SDL_KEYUP = 14
    M64CMD_SET_FRAME_CALLBACK = 15
    M64CMD_TAKE_NEXT_SCREENSHOT = 16
    M64CMD_CORE_STATE_SET = 17
    M64CMD_READ_SCREEN = 18
    M64CMD_RESET = 19
    M64CMD_ADVANCE_FRAME = 20
    M64CMD_SET_MEDIA_LOADER = 21

class m64p_cheat_code(c.Structure):
    _fields_ = [
        ("address", c.c_uint),
        ("value", c.c_int)
    ]

cb_data = c.c_void_p
cart_rom = c.CFUNCTYPE(c.c_char_p, cb_data, c.c_int)
cart_ram = c.CFUNCTYPE(c.c_char_p, cb_data, c.c_int)

class m64p_media_loader(c.Structure):
    #TODO: UNTESTED! c_char_p = path, c_int = number controller
    _fields_ = [
        ("cb_data", cb_data),
        ("get_gb_cart_rom", c.POINTER(cart_rom)), #char* (*get_gb_cart_rom)(void* cb_data, int controller_num);
        ("get_gb_cart_ram", c.POINTER(cart_ram))  #char* (*get_gb_cart_ram)(void* cb_data, int controller_num);
    ]

##############################################
## Structures to hold ROM image information ##
##############################################

class m64p_system_type(EnumC):
    SYSTEM_NTSC = 0
    SYSTEM_PAL = 1
    SYSTEM_MPAL = 2

class m64p_rom_header(c.Structure):
    _fields_ = [
        ("init_PI_BSB_DOM1_LAT_REG", c.c_ubyte),  # 0x00
        ("init_PI_BSB_DOM1_PGS_REG", c.c_ubyte),  # 0x01
        ("init_PI_BSB_DOM1_PWD_REG", c.c_ubyte),  # 0x02
        ("init_PI_BSB_DOM1_PGS_REG2", c.c_ubyte), # 0x03
        ("ClockRate", c.c_uint),                  # 0x04
        ("PC", c.c_uint),                         # 0x08
        ("Release", c.c_uint),                    # 0x0C
        ("CRC1", c.c_uint),                       # 0x10
        ("CRC2", c.c_uint),                       # 0x14
        ("Unknown", c.c_uint * 2),                # 0x18
        ("Name", c.c_ubyte * 20),                 # 0x20
        ("unknown", c.c_uint),                    # 0x34
        ("Manufacturer_ID", c.c_uint),            # 0x38
        ("Cartridge_ID", c.c_ushort),             # 0x3C - Game serial number
        ("Country_code", c.c_ushort)              # 0x3E
    ]

class m64p_rom_settings(c.Structure):
    _fields_ = [
        ("goodname", c.c_char * 256),
        ("MD5", c.c_char * 33),
        ("savetype", c.c_ubyte),
        ("status", c.c_ubyte),                    # Rom status on a scale from 0-5.
        ("players", c.c_ubyte),                   # Local players 0-4, 2/3/4 way Netplay indicated by 5/6/7.
        ("rumble", c.c_ubyte)                     # 0 - No, 1 - Yes boolean for rumble support.
    ]

###########################################
## Structures and Types for the Debugger ##
###########################################

class m64p_dbg_state(EnumC):
    M64P_DBG_RUN_STATE = 1
    M64P_DBG_PREVIOUS_PC = 2
    M64P_DBG_NUM_BREAKPOINTS = 3
    M64P_DBG_CPU_DYNACORE = 4
    M64P_DBG_CPU_NEXT_INTERRUPT = 5

class m64p_dbg_mem_info(EnumC):
    M64P_DBG_MEM_TYPE = 1
    M64P_DBG_MEM_FLAGS = 2
    M64P_DBG_MEM_HAS_RECOMPILED = 3
    M64P_DBG_MEM_NUM_RECOMPILED = 4
    M64P_DBG_RECOMP_OPCODE = 16
    M64P_DBG_RECOMP_ARGS = 17
    M64P_DBG_RECOMP_ADDR = 18

class m64p_dbg_mem_type(EnumC):
    M64P_MEM_NOMEM = 0
    M64P_MEM_NOTHING = 1
    M64P_MEM_RDRAM = 2
    M64P_MEM_RDRAMREG = 3
    M64P_MEM_RSPMEM = 4
    M64P_MEM_RSPREG = 5
    M64P_MEM_RSP = 6
    M64P_MEM_DP = 7
    M64P_MEM_DPS = 8
    M64P_MEM_VI = 9
    M64P_MEM_AI = 10
    M64P_MEM_PI = 11
    M64P_MEM_RI = 12
    M64P_MEM_SI = 13
    M64P_MEM_FLASHRAMSTAT = 14
    M64P_MEM_ROM = 15
    M64P_MEM_PIF = 16
    M64P_MEM_MI = 17
    M64P_MEM_BREAKPOINT = 18

class m64p_dbg_mem_flags(EnumC):
    M64P_MEM_FLAG_READABLE = 0x01
    M64P_MEM_FLAG_WRITABLE = 0x02
    M64P_MEM_FLAG_READABLE_EMUONLY = 0x04   # the EMUONLY flags signify that emulated code can read/write here, but debugger cannot
    M64P_MEM_FLAG_WRITABLE_EMUONLY = 0x08

class m64p_dbg_memptr_type(EnumC):
    M64P_DBG_PTR_RDRAM = 1
    M64P_DBG_PTR_PI_REG = 2
    M64P_DBG_PTR_SI_REG = 3
    M64P_DBG_PTR_VI_REG = 4
    M64P_DBG_PTR_RI_REG = 5
    M64P_DBG_PTR_AI_REG = 6

class m64p_dbg_cpu_data(EnumC):
    M64P_CPU_PC = 1
    M64P_CPU_REG_REG = 2
    M64P_CPU_REG_HI = 3
    M64P_CPU_REG_LO = 4
    M64P_CPU_REG_COP0 = 5
    M64P_CPU_REG_COP1_DOUBLE_PTR = 6
    M64P_CPU_REG_COP1_SIMPLE_PTR = 7
    M64P_CPU_REG_COP1_FGR_64 = 8
    M64P_CPU_TLB = 9

class m64p_dbg_bkp_command(EnumC):
    M64P_BKP_CMD_ADD_ADDR = 1
    M64P_BKP_CMD_ADD_STRUCT = 2
    M64P_BKP_CMD_REPLACE = 3
    M64P_BKP_CMD_REMOVE_ADDR = 4
    M64P_BKP_CMD_REMOVE_IDX = 5
    M64P_BKP_CMD_ENABLE = 6
    M64P_BKP_CMD_DISABLE = 7
    M64P_BKP_CMD_CHECK = 8

def M64P_MEM_INVALID():
    return 0xFFFFFFFF  # Invalid memory read will return this

def BREAKPOINTS_MAX_NUMBER():
    return 128

class m64p_dbg_bkp_flags(EnumC):
    M64P_BKP_FLAG_ENABLED = 0x01
    M64P_BKP_FLAG_READ = 0x02
    M64P_BKP_FLAG_WRITE = 0x04
    M64P_BKP_FLAG_EXEC = 0x08
    M64P_BKP_FLAG_LOG = 0x10 # Log to the console when this breakpoint hits.

#define BPT_CHECK_FLAG(a, b)  ((a.flags & b) == b)
def BPT_CHECK_FLAG(breakpoint, flag):
    # AND bitwise operator
    return ((breakpoint.flags & flag) == flag)

#define BPT_SET_FLAG(a, b)    a.flags = (a.flags | b);
def BPT_SET_FLAG(breakpoint, flag):
    # OR bitwise operator
    breakpoint.flags = (breakpoint.flags | flag)
    return breakpoint.flags

#define BPT_CLEAR_FLAG(a, b)  a.flags = (a.flags & (~b));
def BPT_CLEAR_FLAG(breakpoint, flag):
    # NOT bitwise operator
    breakpoint.flags = (breakpoint.flags & (~flag))
    return breakpoint.flags

#define BPT_TOGGLE_FLAG(a, b) a.flags = (a.flags ^ b);
def BPT_TOGGLE_FLAG(breakpoint, flag):
    # XOR bitwise operator
    breakpoint.flags = (breakpoint.flags ^ flag)
    return breakpoint.flags

class m64p_breakpoint(c.Structure):
    _fields_ = [
        ("address", c.c_uint),
        ("endaddr", c.c_uint),
        ("flags", c.c_uint)
    ]

#######################################################
## Structures and Types for Core Video Extension API ##
#######################################################

class m64p_2d_size(c.Structure):
    _fields_ = [
        ("uiWidth", c.c_uint),
        ("uiHeight", c.c_uint)
    ]

class m64p_GLContextType(EnumC):
    M64P_GL_CONTEXT_PROFILE_CORE = 1
    M64P_GL_CONTEXT_PROFILE_COMPATIBILITY = 2
    M64P_GL_CONTEXT_PROFILE_ES = 3

class m64p_GLattr(EnumC):
    M64P_GL_DOUBLEBUFFER = 1
    M64P_GL_BUFFER_SIZE = 2
    M64P_GL_DEPTH_SIZE = 3
    M64P_GL_RED_SIZE = 4
    M64P_GL_GREEN_SIZE = 5
    M64P_GL_BLUE_SIZE = 6
    M64P_GL_ALPHA_SIZE = 7
    M64P_GL_SWAP_CONTROL = 8
    M64P_GL_MULTISAMPLEBUFFERS = 9
    M64P_GL_MULTISAMPLESAMPLES = 10
    M64P_GL_CONTEXT_MAJOR_VERSION = 11
    M64P_GL_CONTEXT_MINOR_VERSION = 12
    M64P_GL_CONTEXT_PROFILE_MASK = 13


vext_init = c.CFUNCTYPE(c.c_int)
vext_quit = c.CFUNCTYPE(c.c_int)
vext_list_modes = c.CFUNCTYPE(c.c_int, c.POINTER(m64p_2d_size), c.POINTER(c.c_int))
vext_set_mode = c.CFUNCTYPE(c.c_int, c.c_int, c.c_int, c.c_int, c.c_int, c.c_int)
vext_gl_getproc = c.CFUNCTYPE(c.c_void_p, c.c_char_p)
vext_gl_setattr = c.CFUNCTYPE(c.c_int, c.c_int, c.c_int)
vext_gl_getattr = c.CFUNCTYPE(c.c_int, c.c_int, c.POINTER(c.c_int))
vext_gl_swapbuf = c.CFUNCTYPE(c.c_int)
vext_set_caption = c.CFUNCTYPE(c.c_int, c.c_char_p)
vext_toggle_fs = c.CFUNCTYPE(c.c_int)
vext_resize_window = c.CFUNCTYPE(c.c_int, c.c_int, c.c_int)
vext_get_default_fb = c.CFUNCTYPE(c.c_uint32)
class m64p_video_extension_functions(c.Structure):
    _fields_ = [
        ("Functions", c.c_uint),
        ("VidExtFuncInit", vext_init),
        ("VidExtFuncQuit", vext_quit),
        ("VidExtFuncListModes", vext_list_modes),
        ("VidExtFuncSetMode", vext_set_mode),
        ("VidExtFuncGLGetProc", vext_gl_getproc),
        ("VidExtFuncGLSetAttr", vext_gl_setattr),
        ("VidExtFuncGLGetAttr", vext_gl_getattr),
        ("VidExtFuncGLSwapBuf", vext_gl_swapbuf),
        ("VidExtFuncSetCaption", vext_set_caption),
        ("VidExtFuncToggleFS", vext_toggle_fs),
        ("VidExtFuncResizeWindow", vext_resize_window),
        ("VidExtFuncGLGetDefaultFramebuffer", vext_get_default_fb)
    ]


###void (*DebugCallback)(void *Context, int level, const char *message)
#DEBUGPROTO = CFUNCTYPE(None, c_void_p, c_int, c_char_p)

###void (*StateCallback)(void *Context2, m64p_core_param ParamChanged, int NewValue)
#STATEPROTO = CFUNCTYPE(None, POINTER(c_void_p), c_int, c_int)

#configs
#SECTIONSPROTO = CFUNCTYPE(None, POINTER(c_void_p), c_char_p)

#PARAMETERSPROTO = CFUNCTYPE(None, POINTER(c_void_p), c_char_p, c_int)
