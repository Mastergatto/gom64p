#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

import ctypes as c

import wrapper.datatypes as wrp_dt
import global_module as g

###void (*DebugCallback)(void *Context, int level, const char *message)
DEBUGPROTO = c.CFUNCTYPE(None, c.c_void_p, c.c_int, c.c_char_p)

#TODO: logging
def debug_callback(context, level, message):
    context_dec = c.cast(context, c.c_char_p).value.decode("utf-8")
    if level <= wrp_dt.m64p_msg_level.M64MSG_ERROR.value:
        #sys.stderr.write("%s: %s\n" % (context, message))
        #print(m64p_msg_level(level),"(",context,"):", message.decode())
        print("ERROR(" + context_dec + "):", message.decode("utf-8"))
        #pass
    elif level == wrp_dt.m64p_msg_level.M64MSG_WARNING.value:
        #sys.stderr.write("%s: %s\n" % (context.decode(), message.decode()))
        #print("WARNING(" + context_dec + "):", message.decode())
        pass
    elif level == wrp_dt.m64p_msg_level.M64MSG_INFO.value or level == wrp_dt.m64p_msg_level.M64MSG_STATUS.value:
        #sys.stderr.write("%s: %s\n" % (context.decode(), message.decode()))
        #print("INFO(" + context_dec +"):", message.decode())
        pass
    elif level == wrp_dt.m64p_msg_level.M64MSG_VERBOSE.value:
        #sys.stderr.write("%s: %s\n" % (context, message.decode()))
        #print("VERBOSE(" + context_dec +"):", message.decode())
        pass

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
    #print(sections)

CB_SECTIONS = SECTIONSPROTO(list_sections_callback)


PARAMETERSPROTO = c.CFUNCTYPE(None, c.POINTER(c.c_void_p), c.c_char_p, c.c_int)

parameters = {}
section_cb = None
def list_param_callback(context, param_name, param_type):
    """Callback function for enumerating parameters."""
    parameters[section_cb][param_name.decode()] = param_type
    #print(parameters)

CB_PARAMETERS = PARAMETERSPROTO(list_param_callback)

cb_data = c.c_void_p
cart_rom_cb = c.CFUNCTYPE(c.c_void_p, cb_data, c.c_int)
cart_ram_cb = c.CFUNCTYPE(c.c_void_p, cb_data, c.c_int)
dd_rom_cb = c.CFUNCTYPE(c.c_void_p, cb_data)
dd_disk_cb = c.CFUNCTYPE(c.c_void_p, cb_data)

class m64p_media_loader(c.Structure):
    _fields_ = [
        ("cb_data", cb_data),
        ("get_gb_cart_rom", cart_rom_cb), #char* (*get_gb_cart_rom)(void* cb_data, int controller_num);
        ("get_gb_cart_ram", cart_ram_cb), #char* (*get_gb_cart_ram)(void* cb_data, int controller_num);
        ("get_dd_rom", dd_rom_cb),      #char* (*get_dd_rom)(void* cb_data)
        ("get_dd_disk", dd_disk_cb)     #char* (*get_dd_disk)(void* cb_data);
    ]



#FIXME: This drives me crazy, because it always causes memory corruption after a while or at the closing of the frontend
#value = c.cast(c.create_string_buffer(4096),c.c_void_p).value
#filename = c.create_string_buffer(4096)


@cart_rom_cb
def get_gb_cart_rom(cb_data, controller_id):
    #print(cb_data, controller_id)
    #filename = None
    value = None
    g.m64p_wrapper.ConfigOpenSection("Transferpak")
    if controller_id == 0:
        filename = g.m64p_wrapper.ConfigGetParameter("GB-rom-1")
    elif controller_id == 1:
        filename = g.m64p_wrapper.ConfigGetParameter("GB-rom-2")
    elif controller_id == 2:
        filename = g.m64p_wrapper.ConfigGetParameter("GB-rom-3")
    elif controller_id == 3:
        filename = g.m64p_wrapper.ConfigGetParameter("GB-rom-4")
    if filename != '':
        value = c.cast(c.create_string_buffer(filename.encode('utf-8'), 4096), c.c_void_p).value
        return value
    else:
        return None

@cart_ram_cb
def get_gb_cart_ram(cb_data, controller_id):
    #filename = None
    value = None
    g.m64p_wrapper.ConfigOpenSection("Transferpak")
    if controller_id == 0:
        filename = g.m64p_wrapper.ConfigGetParameter("GB-ram-1")
    elif controller_id == 1:
        filename = g.m64p_wrapper.ConfigGetParameter("GB-ram-2")
    elif controller_id == 2:
        filename = g.m64p_wrapper.ConfigGetParameter("GB-ram-3")
    elif controller_id == 3:
        filename = g.m64p_wrapper.ConfigGetParameter("GB-ram-4")
    if filename != '':
        value = c.cast(c.create_string_buffer(filename.encode('utf-8'), 4096), c.c_void_p).value
        return value
    else:
        return None

@dd_rom_cb
def get_dd_rom(cb_data):
    #filename = None
    value = None
    g.m64p_wrapper.ConfigOpenSection("64DD")
    try:
        filename = g.m64p_wrapper.ConfigGetParameter("IPL-ROM")
        if filename != '':
            #media_array = media_buffer(filename, 4096)
            media_value = c.cast(c.create_string_buffer(filename.encode('utf-8'), 4096), c.c_void_p).value
            return media_value
        else:
            return None
    except:
        print("IPL-ROM parameter not found. Creating it.")
        g.m64p_wrapper.ConfigSetDefaultString("IPL-ROM", "", "64DD Bios filename")
        return None

@dd_disk_cb
def get_dd_disk(cb_data):
    #filename = None
    value = None
    g.m64p_wrapper.ConfigOpenSection("64DD")
    try:
        filename = g.m64p_wrapper.ConfigGetParameter("Disk")
        if filename != '':
            #media_array = media_buffer(filename, 4096)
            media_value = c.cast(c.create_string_buffer(filename.encode('utf-8'), 4096), c.c_void_p).value
            return media_value
        else:
            return None
    except:
        print("Disk image parameter not found. Creating it.")
        g.m64p_wrapper.ConfigSetDefaultString("Disk", "", "Disk Image filename")
        return None

MEDIA_LOADER = m64p_media_loader(None, get_gb_cart_rom, get_gb_cart_ram, get_dd_rom, get_dd_disk)
