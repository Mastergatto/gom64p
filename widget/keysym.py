#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################
import external.sdl2 as sdl

def keysym_map(param):
    ### <gtk keycode value>: <sdl scancode value>, #<character present on US keyboard>
    switch = {
        0: sdl.SDL_SCANCODE_UNKNOWN,
        9: sdl.SDL_SCANCODE_ESCAPE, # Escape
        10: sdl.SDL_SCANCODE_1, # 1
        11: sdl.SDL_SCANCODE_2, # 2
        12: sdl.SDL_SCANCODE_3, # 3
        13: sdl.SDL_SCANCODE_4, # 4
        14: sdl.SDL_SCANCODE_5, # 5
        15: sdl.SDL_SCANCODE_6, # 6
        16: sdl.SDL_SCANCODE_7, # 7
        17: sdl.SDL_SCANCODE_8, # 8
        18: sdl.SDL_SCANCODE_9, # 9
        19: sdl.SDL_SCANCODE_0, # 0
        20: sdl.SDL_SCANCODE_MINUS, # < - (minus)> <'>
        21: sdl.SDL_SCANCODE_EQUALS, # < = (equal)> <ì>
        22: sdl.SDL_SCANCODE_BACKSPACE, # Return/backspace
        23: sdl.SDL_SCANCODE_TAB, # TAB
        24: sdl.SDL_SCANCODE_Q, # Q
        25: sdl.SDL_SCANCODE_W, # W
        26: sdl.SDL_SCANCODE_E, # E
        27: sdl.SDL_SCANCODE_R, # R
        28: sdl.SDL_SCANCODE_T, # T
        29: sdl.SDL_SCANCODE_Y, # Y
        30: sdl.SDL_SCANCODE_U, # U
        31: sdl.SDL_SCANCODE_I, # I
        32: sdl.SDL_SCANCODE_O, # O
        33: sdl.SDL_SCANCODE_P, # P
        34: sdl.SDL_SCANCODE_LEFTBRACKET, # <[> <è>
        35: sdl.SDL_SCANCODE_RIGHTBRACKET, # <]> <+>
        36: sdl.SDL_SCANCODE_RETURN, # # Enter/Return
        37: sdl.SDL_SCANCODE_LCTRL, #L-ctrl
        38: sdl.SDL_SCANCODE_A, # A
        39: sdl.SDL_SCANCODE_S, # S
        40: sdl.SDL_SCANCODE_D, # D
        41: sdl.SDL_SCANCODE_F, # F
        42: sdl.SDL_SCANCODE_G, # G
        43: sdl.SDL_SCANCODE_H, # H
        44: sdl.SDL_SCANCODE_J, # J
        45: sdl.SDL_SCANCODE_K, # K
        46: sdl.SDL_SCANCODE_L, # L
        47: sdl.SDL_SCANCODE_SEMICOLON, # <;> <ò>
        48: sdl.SDL_SCANCODE_APOSTROPHE, # <'> <à>
        49: sdl.SDL_SCANCODE_GRAVE, # ` (grave), \
        50: sdl.SDL_SCANCODE_LSHIFT, # L-shift
        51: sdl.SDL_SCANCODE_BACKSLASH, # <\> <ù>
        52: sdl.SDL_SCANCODE_Z, # Z
        53: sdl.SDL_SCANCODE_X, # X
        54: sdl.SDL_SCANCODE_C, # C
        55: sdl.SDL_SCANCODE_V, # V
        56: sdl.SDL_SCANCODE_B, # B
        57: sdl.SDL_SCANCODE_N, # N
        58: sdl.SDL_SCANCODE_M, # M
        59: sdl.SDL_SCANCODE_COMMA, # <,>
        60: sdl.SDL_SCANCODE_PERIOD, # <.>
        61: sdl.SDL_SCANCODE_SLASH, # </> <->
        62: sdl.SDL_SCANCODE_RSHIFT, # R-shift
        63: sdl.SDL_SCANCODE_KP_MULTIPLY, # <*>
        64: sdl.SDL_SCANCODE_LALT, # L-alt
        65: sdl.SDL_SCANCODE_SPACE, # Space
        66: sdl.SDL_SCANCODE_CAPSLOCK, # Caps lock
        67: sdl.SDL_SCANCODE_F1, # F1
        68: sdl.SDL_SCANCODE_F2, # F2
        69: sdl.SDL_SCANCODE_F3, # F3
        70: sdl.SDL_SCANCODE_F4, # F4
        71: sdl.SDL_SCANCODE_F5, # F5
        72: sdl.SDL_SCANCODE_F6, # F6
        73: sdl.SDL_SCANCODE_F7, # F7
        74: sdl.SDL_SCANCODE_F8, # F8
        75: sdl.SDL_SCANCODE_F9, # F9
        #??: sdl.SDL_SCANCODE_F10, #F10
        77: sdl.SDL_SCANCODE_NUMLOCKCLEAR, # Num lock
        #78: sdl.SDL_SCANCODE_, #
        79: sdl.SDL_SCANCODE_KP_7, # KP 7
        80: sdl.SDL_SCANCODE_KP_8, # KP 8
        81: sdl.SDL_SCANCODE_KP_9, # KP 9
        82: sdl.SDL_SCANCODE_KP_MINUS, # <KP -(minus)>
        83: sdl.SDL_SCANCODE_KP_4, # KP 4
        84: sdl.SDL_SCANCODE_KP_5, # KP 5
        85: sdl.SDL_SCANCODE_KP_6, # KP 6
        86: sdl.SDL_SCANCODE_KP_PLUS, # <KP + (plus)>
        87: sdl.SDL_SCANCODE_KP_1, # KP 1
        88: sdl.SDL_SCANCODE_KP_2, # KP 2
        89: sdl.SDL_SCANCODE_KP_3, # KP 3
        90: sdl.SDL_SCANCODE_KP_0, # KP 0
        91: sdl.SDL_SCANCODE_KP_PERIOD, # <KP . (period)>
        #92: sdl.SDL_SCANCODE_, #
        #93: sdl.SDL_SCANCODE_, #
        94: sdl.SDL_SCANCODE_NONUSBACKSLASH, # <> '<'
        95: sdl.SDL_SCANCODE_F11, #F11
        #??: sdl.SDL_SCANCODE_F12, #F12
        #??: sdl.SDL_SCANCODE_F13, #F13
        #??: sdl.SDL_SCANCODE_F14, #F14
        #??: sdl.SDL_SCANCODE_F15, #F15
        104: sdl.SDL_SCANCODE_KP_ENTER, # KP Enter
        105: sdl.SDL_SCANCODE_RCTRL, # R-ctrl
        106: sdl.SDL_SCANCODE_KP_DIVIDE, # <KP / (divide)>
        108: sdl.SDL_SCANCODE_RALT, # Alt gr/Ralt
        110: sdl.SDL_SCANCODE_HOME, # Start?
        111: sdl.SDL_SCANCODE_UP, # Up
        112: sdl.SDL_SCANCODE_PAGEUP, # Pag up
        113: sdl.SDL_SCANCODE_LEFT, # Left
        114: sdl.SDL_SCANCODE_RIGHT, # Right
        115: sdl.SDL_SCANCODE_END, # End
        116: sdl.SDL_SCANCODE_DOWN, # Down
        117: sdl.SDL_SCANCODE_PAGEDOWN, #Pag down
        118: sdl.SDL_SCANCODE_INSERT, # Insert, FIXME SDL_SCANCODE_SCROLLLOCK?
        119: sdl.SDL_SCANCODE_DELETE, # Canc?
        #??: sdl.SDL_SCANCODE_PRINTSCREEN, # Print Screen
        127: sdl.SDL_SCANCODE_PAUSE, # Pause/interrupt?
        135: sdl.SDL_SCANCODE_RGUI, # Super/menu? to the right

        #??: sdl.SDL_SCANCODE_LGUI, #Super to the left
    }
    return switch.get(param, sdl.SDL_SCANCODE_UNKNOWN)
