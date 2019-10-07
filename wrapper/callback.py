#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

import ctypes as c

import wrapper.datatypes as wrp_dt
import logging as log

frontend = None

###void (*DebugCallback)(void *Context, int level, const char *message)
DEBUGPROTO = c.CFUNCTYPE(None, c.c_void_p, c.c_int, c.c_char_p)

def debug_callback(context, level, message):
    context_dec = c.cast(context, c.c_char_p).value.decode("utf-8")
    if level <= wrp_dt.m64p_msg_level.M64MSG_ERROR.value:
        #sys.stderr.write("%s: %s\n" % (context, message))
        try:
            log.error(f'({context_dec}) {message.decode("utf-8")}')
        except UnicodeDecodeError:
            log.error(f'({context_dec}) {message.decode("cp932", "replace")}')
    elif level == wrp_dt.m64p_msg_level.M64MSG_WARNING.value:
        try:
            log.warning(f'({context_dec}) {message.decode("utf-8")}')
        except UnicodeDecodeError:
            log.warning(f'({context_dec}) {message.decode("cp932", "replace")}')
    elif level == wrp_dt.m64p_msg_level.M64MSG_INFO.value or level == wrp_dt.m64p_msg_level.M64MSG_STATUS.value:
        try:
            log.info(f'({context_dec}) {message.decode("utf-8")}')
        except UnicodeDecodeError:
            log.info(f'({context_dec}) {message.decode("cp932", "replace")}')
    elif level == wrp_dt.m64p_msg_level.M64MSG_VERBOSE.value:
        log.debug(f'({context_dec}) {message.decode("utf-8", "replace")}')

CB_DEBUG = DEBUGPROTO(debug_callback)

###void (*StateCallback)(void *Context2, m64p_core_param ParamChanged, int NewValue)
STATEPROTO = c.CFUNCTYPE(None, c.POINTER(c.c_void_p), c.c_int, c.c_int)

def state_callback(self, context, param, value):
    # NOTE: Unused, it's here just for reference
    if param == t.m64p_core_param.M64CORE_EMU_STATE.value:
        if wrp_dt.m64p_emu_state(value).name == 'M64EMU_STOPPED':
            pass
        elif wrp_dt.m64p_emu_state(value).name == 'M64EMU_RUNNING':
            pass
        elif wrp_dt.m64p_emu_state(value).name == 'M64EMU_PAUSED':
            pass

    elif param == wrp_dt.m64p_core_param.M64CORE_VIDEO_MODE.value:
        pass
    elif param == wrp_dt.m64p_core_param.M64CORE_SAVESTATE_SLOT.value:
        pass
    elif param == wrp_dt.m64p_core_param.M64CORE_SPEED_FACTOR.value:
        pass
    elif param == wrp_dt.m64p_core_param.M64CORE_SPEED_LIMITER.value:
        pass
    elif param == wrp_dt.m64p_core_param.M64CORE_VIDEO_SIZE.value:
        pass
    elif param == wrp_dt.m64p_core_param.M64CORE_AUDIO_VOLUME.value:
        pass
    elif param == wrp_dt.m64p_core_param.M64CORE_AUDIO_MUTE.value:
        pass
    elif param == wrp_dt.m64p_core_param.M64CORE_INPUT_GAMESHARK.value:
        pass
    elif param == wrp_dt.m64p_core_param.M64CORE_STATE_LOADCOMPLETE.value:
        pass
    elif param == wrp_dt.m64p_core_param.M64CORE_STATE_SAVECOMPLETE.value:
        pass
    else:
        # Unmapped params go here.
        print(context.contents, param, value)

#CB_STATE = STATEPROTO(state_callback)
CB_STATE = None


SECTIONSPROTO = c.CFUNCTYPE(None, c.POINTER(c.c_void_p), c.c_char_p)

sections = []
def list_sections_callback(context, section_name):
    """Callback function for enumerating sections."""
    sections.append(section_name)
    #log.debug(sections)

CB_SECTIONS = SECTIONSPROTO(list_sections_callback)


PARAMETERSPROTO = c.CFUNCTYPE(None, c.POINTER(c.c_void_p), c.c_char_p, c.c_int)

parameters = {}
section_cb = None
def list_param_callback(context, param_name, param_type):
    """Callback function for enumerating parameters."""
    parameters[section_cb][param_name.decode()] = param_type
    #log.debug(parameters)

CB_PARAMETERS = PARAMETERSPROTO(list_param_callback)



#FIXME: This drives me crazy, because it always causes memory corruption after a while or at the closing of the frontend (segfault, double free or corruption(out), invalid pointer)
#GLib.strdup(str) ?
class Media_callback(object):
    cart_rom_cb = c.CFUNCTYPE(c.c_void_p, c.c_void_p, c.c_int)
    cart_ram_cb = c.CFUNCTYPE(c.c_void_p, c.c_void_p, c.c_int)
    dd_rom_cb = c.CFUNCTYPE(c.c_void_p, c.c_void_p)
    dd_disk_cb = c.CFUNCTYPE(c.c_void_p, c.c_void_p)

    @cart_rom_cb
    def get_gb_cart_rom(cb_data, controller_id):
        frontend.m64p_wrapper.ConfigOpenSection("Transferpak")
        if controller_id == 0:
            filename = frontend.m64p_wrapper.ConfigGetParameter("GB-rom-1")
        elif controller_id == 1:
            filename = frontend.m64p_wrapper.ConfigGetParameter("GB-rom-2")
        elif controller_id == 2:
            filename = frontend.m64p_wrapper.ConfigGetParameter("GB-rom-3")
        elif controller_id == 3:
            filename = frontend.m64p_wrapper.ConfigGetParameter("GB-rom-4")
        else:
            log.warning("Unknown controller")
        if filename != '':
            return c.cast(c.create_string_buffer(filename.encode('utf-8'), 1023), c.c_void_p).value
        else:
            return None

    @cart_ram_cb
    def get_gb_cart_ram(cb_data, controller_id):
        frontend.m64p_wrapper.ConfigOpenSection("Transferpak")
        if controller_id == 0:
            filename = frontend.m64p_wrapper.ConfigGetParameter("GB-ram-1")
        elif controller_id == 1:
            filename = frontend.m64p_wrapper.ConfigGetParameter("GB-ram-2")
        elif controller_id == 2:
            filename = frontend.m64p_wrapper.ConfigGetParameter("GB-ram-3")
        elif controller_id == 3:
            filename = frontend.m64p_wrapper.ConfigGetParameter("GB-ram-4")
        else:
            log.warning("Unknown controller")
        if filename != '':
            return c.cast(c.create_string_buffer(filename.encode('utf-8'), 1023), c.c_void_p).value
        else:
            return None

    @dd_rom_cb
    def get_dd_rom(cb_data):
        frontend.m64p_wrapper.ConfigOpenSection("64DD")
        try:
            filename = frontend.m64p_wrapper.ConfigGetParameter("IPL-ROM")
            if filename != '':
                return c.cast(c.create_string_buffer(filename.encode('utf-8'), 1023), c.c_void_p).value
            else:
                return None
        except:
            log.warning("IPL-ROM parameter not found. Creating it.")
            frontend.m64p_wrapper.ConfigSetDefaultString("IPL-ROM", "", "64DD Bios filename")
            return None

    @dd_disk_cb
    def get_dd_disk(cb_data):
        frontend.m64p_wrapper.ConfigOpenSection("64DD")
        try:
            filename = frontend.m64p_wrapper.ConfigGetParameter("Disk")
            if filename != '':
                return c.cast(c.create_string_buffer(filename.encode('utf-8'), 1023), c.c_void_p).value
            else:
                return None
        except:
            log.warning("Disk image parameter not found. Creating it.")
            frontend.m64p_wrapper.ConfigSetDefaultString("Disk", "", "Disk Image filename")
            return None

cb = Media_callback()
class m64p_media_loader(c.Structure):
    _fields_ = [
        ("cb_data", c.c_void_p),
        ("get_gb_cart_rom", cb.cart_rom_cb), #char* (*get_gb_cart_rom)(void* cb_data, int controller_num);
        ("get_gb_cart_ram", cb.cart_ram_cb), #char* (*get_gb_cart_ram)(void* cb_data, int controller_num);
        ("get_dd_rom", cb.dd_rom_cb),      #char* (*get_dd_rom)(void* cb_data)
        ("get_dd_disk", cb.dd_disk_cb)     #char* (*get_dd_disk)(void* cb_data);
    ]

MEDIA_LOADER = m64p_media_loader(None, cb.get_gb_cart_rom, cb.get_gb_cart_ram, cb.get_dd_rom, cb.get_dd_disk)
