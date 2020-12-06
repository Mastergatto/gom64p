#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
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



#FIXME: This drives me crazy, because it always causes memory corruption after a while or at the closing of the frontend (segfault, double free or corruption(out or !prev), invalid pointer, corrupted size vs. prev_size while consolidating)
ml_filename = None
ml_string = c.create_string_buffer(1024)

cb_data_cb = c.PYFUNCTYPE(c.c_void_p, c.c_void_p)
cart_rom_cb = c.PYFUNCTYPE(c.c_char_p, cb_data_cb, c.c_int)
cart_ram_cb = c.PYFUNCTYPE(c.c_char_p, cb_data_cb, c.c_int)
dd_rom_cb = c.PYFUNCTYPE(c.c_char_p, cb_data_cb)
dd_disk_cb = c.PYFUNCTYPE(c.c_char_p, cb_data_cb)

class m64p_media_loader(c.Structure):
    _fields_ = [
        ("cb_data", cb_data_cb),
        ("get_gb_cart_rom", cart_rom_cb), #char* (*get_gb_cart_rom)(void* cb_data, int controller_num);
        ("get_gb_cart_ram", cart_ram_cb), #char* (*get_gb_cart_ram)(void* cb_data, int controller_num);
        ("get_dd_rom", dd_rom_cb),        #char* (*get_dd_rom)(void* cb_data)
        ("get_dd_disk", dd_disk_cb)       #char* (*get_dd_disk)(void* cb_data);
    ]

@cb_data_cb
def ml_cb(data):
    return data

def media_loader_get_filename(cb_data, section, param):
    ml_filename = ''
    frontend.m64p_wrapper.ConfigOpenSection(section)
    ml_filename = frontend.m64p_wrapper.ConfigGetParameter(param)

    if ml_filename != '':
        ml_string.value = ml_filename.encode("utf-8")
        return cb_data(c.byref(ml_string))

@cart_rom_cb
def ml_gb_cart_rom(cb_data, controller_id):
    return media_loader_get_filename(cb_data, "Transferpak", f'GB-rom-{controller_id + 1}')

@cart_ram_cb
def ml_gb_cart_ram(cb_data, controller_id):
    return media_loader_get_filename(cb_data, "Transferpak", f'GB-ram-{controller_id + 1}')

@dd_rom_cb
def ml_dd_rom(cb_data):
    try:
        return media_loader_get_filename(cb_data, "64DD", "IPL-ROM")
    except:
        log.warning("IPL-ROM parameter not found. Creating it.")
        frontend.m64p_wrapper.ConfigSetDefaultString("IPL-ROM", "", "64DD Bios filename")

@dd_disk_cb
def ml_dd_disk(cb_data):
    try:
        return media_loader_get_filename(cb_data, "64DD", "Disk")
    except:
        log.warning("Disk image parameter not found. Creating it.")
        frontend.m64p_wrapper.ConfigSetDefaultString("Disk", "", "Disk Image filename")

MEDIA_LOADER = m64p_media_loader(ml_cb, ml_gb_cart_rom, ml_gb_cart_ram, ml_dd_rom, ml_dd_disk)

