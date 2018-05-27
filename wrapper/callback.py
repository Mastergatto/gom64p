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
    if level <= wrp_dt.m64p_msg_level.M64MSG_ERROR.value:
        #sys.stderr.write("%s: %s\n" % (context, message))
        #print(m64p_msg_level(level),"(",context,"):", message.decode())
        print("ERROR(",context,"):", message.decode())
        #pass
    elif level == wrp_dt.m64p_msg_level.M64MSG_WARNING.value:
        #sys.stderr.write("%s: %s\n" % (context.decode(), message.decode()))
        #print("WARNING(",context,"):", message.decode())
        pass
    elif level == wrp_dt.m64p_msg_level.M64MSG_INFO.value or level == wrp_dt.m64p_msg_level.M64MSG_STATUS.value:
        #sys.stderr.write("%s: %s\n" % (context.decode(), message.decode()))
        #print("INFO(",context,"):", message.decode())
        pass
    elif level == wrp_dt.m64p_msg_level.M64MSG_VERBOSE.value:
        #sys.stderr.write("%s: %s\n" % (context, message.decode()))
        #print("VERBOSE(",context,"):", message.decode())
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

cart_rom = c.CFUNCTYPE(c.c_void_p, c.POINTER(c.c_void_p), c.c_int)
cart_ram = c.CFUNCTYPE(c.c_void_p, c.POINTER(c.c_void_p), c.c_int)
ipl_rom = c.CFUNCTYPE(c.c_void_p, c.POINTER(c.c_void_p))
disk_image = c.CFUNCTYPE(c.c_void_p, c.POINTER(c.c_void_p))

class m64p_media_loader(c.Structure):
    pass

m64p_media_loader._fields_ = [
        ("cb_data", c.POINTER(m64p_media_loader)),
        ("get_gb_cart_rom", cart_rom), #char* (*get_gb_cart_rom)(void* cb_data, int controller_num);
        ("get_gb_cart_ram", cart_ram), #char* (*get_gb_cart_ram)(void* cb_data, int controller_num);
        ("get_dd_rom", ipl_rom), #char* (*get_dd_rom)(void* cb_data);
        ("get_dd_disk", disk_image) #char* (*get_dd_disk)(void* cb_data);
    ]

#media_buffer = c.create_string_buffer
#media_array = c.create_string_buffer(4096)

def get_gb_cart_rom(cb_data, controller_id):
    #print(cb_data.contents, controller_id)
    filename = None
    caster = None
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
        #media_array = media_buffer(filename, 4096)
        caster = c.cast(filename.encode('utf-8'), c.c_void_p).value
        return caster
    else:
        return None

def get_gb_cart_ram(cb_data, controller_id):
    #print(cb_data.contents, controller_id)
    filename = None
    caster = None
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
        #media_array = media_buffer(filename, 4096)
        caster = c.cast(filename.encode('utf-8'), c.c_void_p).value
        return caster
    else:
        return None

def get_ipl_rom(cb_data):
    g.m64p_wrapper.ConfigOpenSection("64DD")
    filename = g.m64p_wrapper.ConfigGetParameter("IPL-ROM")
    if filename != '':
        #media_array = media_buffer(filename, 4096)
        caster = c.cast(filename.encode('utf-8'), c.c_void_p).value
        return caster
    else:
        return None

def get_dd_image(cb_data):
    g.m64p_wrapper.ConfigOpenSection("64DD")
    filename = g.m64p_wrapper.ConfigGetParameter("Disk")
    if filename != '':
        #media_array = media_buffer(filename, 4096)
        caster = c.cast(filename.encode('utf-8'), c.c_void_p).value
        return caster
    else:
        return None


MEDIA_LOADER = m64p_media_loader()
MEDIA_LOADER.cb_data = c.pointer(MEDIA_LOADER)
MEDIA_LOADER.get_gb_cart_rom = cart_rom(get_gb_cart_rom)
MEDIA_LOADER.get_gb_cart_ram = cart_ram(get_gb_cart_ram)
MEDIA_LOADER.get_dd_rom = ipl_rom(get_ipl_rom)
MEDIA_LOADER.get_dd_disk = disk_image(get_dd_image)
