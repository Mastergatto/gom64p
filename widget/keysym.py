#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################
import platform

import external.sdl2 as sdl
from enum import Enum

class Scancodes(Enum):
    SDL_SCANCODE_UNKNOWN = 0
    SDL_SCANCODE_A = 4
    SDL_SCANCODE_B = 5
    SDL_SCANCODE_C = 6
    SDL_SCANCODE_D = 7
    SDL_SCANCODE_E = 8
    SDL_SCANCODE_F = 9
    SDL_SCANCODE_G = 10
    SDL_SCANCODE_H = 11
    SDL_SCANCODE_I = 12
    SDL_SCANCODE_J = 13
    SDL_SCANCODE_K = 14
    SDL_SCANCODE_L = 15
    SDL_SCANCODE_M = 16
    SDL_SCANCODE_N = 17
    SDL_SCANCODE_O = 18
    SDL_SCANCODE_P = 19
    SDL_SCANCODE_Q = 20
    SDL_SCANCODE_R = 21
    SDL_SCANCODE_S = 22
    SDL_SCANCODE_T = 23
    SDL_SCANCODE_U = 24
    SDL_SCANCODE_V = 25
    SDL_SCANCODE_W = 26
    SDL_SCANCODE_X = 27
    SDL_SCANCODE_Y = 28
    SDL_SCANCODE_Z = 29

    SDL_SCANCODE_1 = 30
    SDL_SCANCODE_2 = 31
    SDL_SCANCODE_3 = 32
    SDL_SCANCODE_4 = 33
    SDL_SCANCODE_5 = 34
    SDL_SCANCODE_6 = 35
    SDL_SCANCODE_7 = 36
    SDL_SCANCODE_8 = 37
    SDL_SCANCODE_9 = 38
    SDL_SCANCODE_0 = 39

    SDL_SCANCODE_RETURN = 40
    SDL_SCANCODE_ESCAPE = 41
    SDL_SCANCODE_BACKSPACE = 42
    SDL_SCANCODE_TAB = 43
    SDL_SCANCODE_SPACE = 44

    SDL_SCANCODE_MINUS = 45
    SDL_SCANCODE_EQUALS = 46
    SDL_SCANCODE_LEFTBRACKET = 47
    SDL_SCANCODE_RIGHTBRACKET = 48
    SDL_SCANCODE_BACKSLASH = 49

    SDL_SCANCODE_NONUSHASH = 50

    SDL_SCANCODE_SEMICOLON = 51
    SDL_SCANCODE_APOSTROPHE = 52
    SDL_SCANCODE_GRAVE = 53

    SDL_SCANCODE_COMMA = 54
    SDL_SCANCODE_PERIOD = 55
    SDL_SCANCODE_SLASH = 56

    SDL_SCANCODE_CAPSLOCK = 57

    SDL_SCANCODE_F1 = 58
    SDL_SCANCODE_F2 = 59
    SDL_SCANCODE_F3 = 60
    SDL_SCANCODE_F4 = 61
    SDL_SCANCODE_F5 = 62
    SDL_SCANCODE_F6 = 63
    SDL_SCANCODE_F7 = 64
    SDL_SCANCODE_F8 = 65
    SDL_SCANCODE_F9 = 66
    SDL_SCANCODE_F10 = 67
    SDL_SCANCODE_F11 = 68
    SDL_SCANCODE_F12 = 69

    SDL_SCANCODE_PRINTSCREEN = 70
    SDL_SCANCODE_SCROLLLOCK = 71
    SDL_SCANCODE_PAUSE = 72
    SDL_SCANCODE_INSERT = 73

    SDL_SCANCODE_HOME = 74
    SDL_SCANCODE_PAGEUP = 75
    SDL_SCANCODE_DELETE = 76
    SDL_SCANCODE_END = 77
    SDL_SCANCODE_PAGEDOWN = 78
    SDL_SCANCODE_RIGHT = 79
    SDL_SCANCODE_LEFT = 80
    SDL_SCANCODE_DOWN = 81
    SDL_SCANCODE_UP = 82

    SDL_SCANCODE_NUMLOCKCLEAR = 83
    SDL_SCANCODE_KP_DIVIDE = 84
    SDL_SCANCODE_KP_MULTIPLY = 85
    SDL_SCANCODE_KP_MINUS = 86
    SDL_SCANCODE_KP_PLUS = 87
    SDL_SCANCODE_KP_ENTER = 88
    SDL_SCANCODE_KP_1 = 89
    SDL_SCANCODE_KP_2 = 90
    SDL_SCANCODE_KP_3 = 91
    SDL_SCANCODE_KP_4 = 92
    SDL_SCANCODE_KP_5 = 93
    SDL_SCANCODE_KP_6 = 94
    SDL_SCANCODE_KP_7 = 95
    SDL_SCANCODE_KP_8 = 96
    SDL_SCANCODE_KP_9 = 97
    SDL_SCANCODE_KP_0 = 98
    SDL_SCANCODE_KP_PERIOD = 99

    SDL_SCANCODE_NONUSBACKSLASH = 100

    SDL_SCANCODE_APPLICATION = 101
    SDL_SCANCODE_POWER = 102

    SDL_SCANCODE_KP_EQUALS = 103

    SDL_SCANCODE_F13 = 104
    SDL_SCANCODE_F14 = 105
    SDL_SCANCODE_F15 = 106
    SDL_SCANCODE_F16 = 107
    SDL_SCANCODE_F17 = 108
    SDL_SCANCODE_F18 = 109
    SDL_SCANCODE_F19 = 110
    SDL_SCANCODE_F20 = 111
    SDL_SCANCODE_F21 = 112
    SDL_SCANCODE_F22 = 113
    SDL_SCANCODE_F23 = 114
    SDL_SCANCODE_F24 = 115
    SDL_SCANCODE_EXECUTE = 116
    SDL_SCANCODE_HELP = 117
    SDL_SCANCODE_MENU = 118
    SDL_SCANCODE_SELECT = 119
    SDL_SCANCODE_STOP = 120
    SDL_SCANCODE_AGAIN = 121
    SDL_SCANCODE_UNDO = 122
    SDL_SCANCODE_CUT = 123
    SDL_SCANCODE_COPY = 124
    SDL_SCANCODE_PASTE = 125
    SDL_SCANCODE_FIND = 126
    SDL_SCANCODE_MUTE = 127
    SDL_SCANCODE_VOLUMEUP = 128
    SDL_SCANCODE_VOLUMEDOWN = 129
    SDL_SCANCODE_KP_COMMA = 133
    SDL_SCANCODE_KP_EQUALSAS400 = 134

    SDL_SCANCODE_INTERNATIONAL1 = 135
    SDL_SCANCODE_INTERNATIONAL2 = 136
    SDL_SCANCODE_INTERNATIONAL3 = 137
    SDL_SCANCODE_INTERNATIONAL4 = 138
    SDL_SCANCODE_INTERNATIONAL5 = 139
    SDL_SCANCODE_INTERNATIONAL6 = 140
    SDL_SCANCODE_INTERNATIONAL7 = 141
    SDL_SCANCODE_INTERNATIONAL8 = 142
    SDL_SCANCODE_INTERNATIONAL9 = 143

    SDL_SCANCODE_LANG1 = 144
    SDL_SCANCODE_LANG2 = 145
    SDL_SCANCODE_LANG3 = 146
    SDL_SCANCODE_LANG4 = 147
    SDL_SCANCODE_LANG5 = 148
    SDL_SCANCODE_LANG6 = 149
    SDL_SCANCODE_LANG7 = 150
    SDL_SCANCODE_LANG8 = 151
    SDL_SCANCODE_LANG9 = 152

    SDL_SCANCODE_ALTERASE = 153
    SDL_SCANCODE_SYSREQ = 154
    SDL_SCANCODE_CANCEL = 155
    SDL_SCANCODE_CLEAR = 156
    SDL_SCANCODE_PRIOR = 157
    SDL_SCANCODE_RETURN2 = 158
    SDL_SCANCODE_SEPARATOR = 159
    SDL_SCANCODE_OUT = 160
    SDL_SCANCODE_OPER = 161
    SDL_SCANCODE_CLEARAGAIN = 162
    SDL_SCANCODE_CRSEL = 163
    SDL_SCANCODE_EXSEL = 164

    SDL_SCANCODE_KP_00 = 176
    SDL_SCANCODE_KP_000 = 177
    SDL_SCANCODE_THOUSANDSSEPARATOR = 178
    SDL_SCANCODE_DECIMALSEPARATOR = 179
    SDL_SCANCODE_CURRENCYUNIT = 180
    SDL_SCANCODE_CURRENCYSUBUNIT = 181
    SDL_SCANCODE_KP_LEFTPAREN = 182
    SDL_SCANCODE_KP_RIGHTPAREN = 183
    SDL_SCANCODE_KP_LEFTBRACE = 184
    SDL_SCANCODE_KP_RIGHTBRACE = 185
    SDL_SCANCODE_KP_TAB = 186
    SDL_SCANCODE_KP_BACKSPACE = 187
    SDL_SCANCODE_KP_A = 188
    SDL_SCANCODE_KP_B = 189
    SDL_SCANCODE_KP_C = 190
    SDL_SCANCODE_KP_D = 191
    SDL_SCANCODE_KP_E = 192
    SDL_SCANCODE_KP_F = 193
    SDL_SCANCODE_KP_XOR = 194
    SDL_SCANCODE_KP_POWER = 195
    SDL_SCANCODE_KP_PERCENT = 196
    SDL_SCANCODE_KP_LESS = 197
    SDL_SCANCODE_KP_GREATER = 198
    SDL_SCANCODE_KP_AMPERSAND = 199
    SDL_SCANCODE_KP_DBLAMPERSAND = 200
    SDL_SCANCODE_KP_VERTICALBAR = 201
    SDL_SCANCODE_KP_DBLVERTICALBAR = 202
    SDL_SCANCODE_KP_COLON = 203
    SDL_SCANCODE_KP_HASH = 204
    SDL_SCANCODE_KP_SPACE = 205
    SDL_SCANCODE_KP_AT = 206
    SDL_SCANCODE_KP_EXCLAM = 207
    SDL_SCANCODE_KP_MEMSTORE = 208
    SDL_SCANCODE_KP_MEMRECALL = 209
    SDL_SCANCODE_KP_MEMCLEAR = 210
    SDL_SCANCODE_KP_MEMADD = 211
    SDL_SCANCODE_KP_MEMSUBTRACT = 212
    SDL_SCANCODE_KP_MEMMULTIPLY = 213
    SDL_SCANCODE_KP_MEMDIVIDE = 214
    SDL_SCANCODE_KP_PLUSMINUS = 215
    SDL_SCANCODE_KP_CLEAR = 216
    SDL_SCANCODE_KP_CLEARENTRY = 217
    SDL_SCANCODE_KP_BINARY = 218
    SDL_SCANCODE_KP_OCTAL = 219
    SDL_SCANCODE_KP_DECIMAL = 220
    SDL_SCANCODE_KP_HEXADECIMAL = 221

    SDL_SCANCODE_LCTRL = 224
    SDL_SCANCODE_LSHIFT = 225
    SDL_SCANCODE_LALT = 226
    SDL_SCANCODE_LGUI = 227
    SDL_SCANCODE_RCTRL = 228
    SDL_SCANCODE_RSHIFT = 229
    SDL_SCANCODE_RALT = 230
    SDL_SCANCODE_RGUI = 231

    SDL_SCANCODE_MODE = 257

    SDL_SCANCODE_AUDIONEXT = 258
    SDL_SCANCODE_AUDIOPREV = 259
    SDL_SCANCODE_AUDIOSTOP = 260
    SDL_SCANCODE_AUDIOPLAY = 261
    SDL_SCANCODE_AUDIOMUTE = 262
    SDL_SCANCODE_MEDIASELECT = 263
    SDL_SCANCODE_WWW = 264
    SDL_SCANCODE_MAIL = 265
    SDL_SCANCODE_CALCULATOR = 266
    SDL_SCANCODE_COMPUTER = 267
    SDL_SCANCODE_AC_SEARCH = 268
    SDL_SCANCODE_AC_HOME = 269
    SDL_SCANCODE_AC_BACK = 270
    SDL_SCANCODE_AC_FORWARD = 271
    SDL_SCANCODE_AC_STOP = 272
    SDL_SCANCODE_AC_REFRESH = 273
    SDL_SCANCODE_AC_BOOKMARKS = 274
    SDL_SCANCODE_BRIGHTNESSDOWN = 275
    SDL_SCANCODE_BRIGHTNESSUP = 276
    SDL_SCANCODE_DISPLAYSWITCH = 277
    SDL_SCANCODE_KBDILLUMTOGGLE = 278
    SDL_SCANCODE_KBDILLUMDOWN = 279
    SDL_SCANCODE_KBDILLUMUP = 280
    SDL_SCANCODE_EJECT = 281
    SDL_SCANCODE_SLEEP = 282

    SDL_SCANCODE_APP1 = 283
    SDL_SCANCODE_APP2 = 284
    SDL_SCANCODE_AUDIOREWIND = 285
    SDL_SCANCODE_AUDIOFASTFORWARD = 286

    SDL_NUM_SCANCODES = 512

platform = platform.system()
def keysym2sdl(param):
    ### evdev: https://github.com/xkbcommon/libxkbcommon/blob/master/test/evdev-scancodes.h
    ### win32: https://gitlab.gnome.org/GNOME/gtk/raw/master/gdk/gdkkeysyms.h
    ### https://github.com/GNOME/gtk/blob/master/gdk/win32/gdkkeys-win32.c
    if platform == "Linux":
        switch = {
            ### <gtk keycode value + 8>: <sdl scancode value>, #<character present on US keyboard>
            0: 'SDL_SCANCODE_UNKNOWN',
            9: 'SDL_SCANCODE_ESCAPE', # Escape
            10: 'SDL_SCANCODE_1', # 1
            11: 'SDL_SCANCODE_2', # 2
            12: 'SDL_SCANCODE_3', # 3
            13: 'SDL_SCANCODE_4', # 4
            14: 'SDL_SCANCODE_5', # 5
            15: 'SDL_SCANCODE_6', # 6
            16: 'SDL_SCANCODE_7', # 7
            17: 'SDL_SCANCODE_8', # 8
            18: 'SDL_SCANCODE_9', # 9
            19: 'SDL_SCANCODE_0', # 0
            20: 'SDL_SCANCODE_MINUS', # < - (minus)> <'>
            21: 'SDL_SCANCODE_EQUALS', # < = (equal)> <ì>
            22: 'SDL_SCANCODE_BACKSPACE', # Return/backspace
            23: 'SDL_SCANCODE_TAB', # TAB
            24: 'SDL_SCANCODE_Q', # Q
            25: 'SDL_SCANCODE_W', # W
            26: 'SDL_SCANCODE_E', # E
            27: 'SDL_SCANCODE_R', # R
            28: 'SDL_SCANCODE_T', # T
            29: 'SDL_SCANCODE_Y', # Y
            30: 'SDL_SCANCODE_U', # U
            31: 'SDL_SCANCODE_I', # I
            32: 'SDL_SCANCODE_O', # O
            33: 'SDL_SCANCODE_P', # P
            34: 'SDL_SCANCODE_LEFTBRACKET', # <[> <è>
            35: 'SDL_SCANCODE_RIGHTBRACKET', # <]> <+>
            36: 'SDL_SCANCODE_RETURN', # # Enter/Return
            37: 'SDL_SCANCODE_LCTRL', #L-ctrl
            38: 'SDL_SCANCODE_A', # A
            39: 'SDL_SCANCODE_S', # S
            40: 'SDL_SCANCODE_D', # D
            41: 'SDL_SCANCODE_F', # F
            42: 'SDL_SCANCODE_G', # G
            43: 'SDL_SCANCODE_H', # H
            44: 'SDL_SCANCODE_J', # J
            45: 'SDL_SCANCODE_K', # K
            46: 'SDL_SCANCODE_L', # L
            47: 'SDL_SCANCODE_SEMICOLON', # <;> <ò>
            48: 'SDL_SCANCODE_APOSTROPHE', # <'> <à>
            49: 'SDL_SCANCODE_GRAVE', # ` (grave), \
            50: 'SDL_SCANCODE_LSHIFT', # L-shift
            51: 'SDL_SCANCODE_BACKSLASH', # <\> <ù>
            52: 'SDL_SCANCODE_Z', # Z
            53: 'SDL_SCANCODE_X', # X
            54: 'SDL_SCANCODE_C', # C
            55: 'SDL_SCANCODE_V', # V
            56: 'SDL_SCANCODE_B', # B
            57: 'SDL_SCANCODE_N', # N
            58: 'SDL_SCANCODE_M', # M
            59: 'SDL_SCANCODE_COMMA', # <,>
            60: 'SDL_SCANCODE_PERIOD', # <.>
            61: 'SDL_SCANCODE_SLASH', # </> <->
            62: 'SDL_SCANCODE_RSHIFT', # R-shift
            63: 'SDL_SCANCODE_KP_MULTIPLY', # <*>
            64: 'SDL_SCANCODE_LALT', # L-alt
            65: 'SDL_SCANCODE_SPACE', # Space
            66: 'SDL_SCANCODE_CAPSLOCK', # Caps lock
            67: 'SDL_SCANCODE_F1', # F1
            68: 'SDL_SCANCODE_F2', # F2
            69: 'SDL_SCANCODE_F3', # F3
            70: 'SDL_SCANCODE_F4', # F4
            71: 'SDL_SCANCODE_F5', # F5
            72: 'SDL_SCANCODE_F6', # F6
            73: 'SDL_SCANCODE_F7', # F7
            74: 'SDL_SCANCODE_F8', # F8
            75: 'SDL_SCANCODE_F9', # F9
            76: 'SDL_SCANCODE_F10', #F10
            77: 'SDL_SCANCODE_NUMLOCKCLEAR', # Num lock
            78: 'SDL_SCANCODE_SCROLLLOCK', # Scroll lock
            79: 'SDL_SCANCODE_KP_7', # KP 7
            80: 'SDL_SCANCODE_KP_8', # KP 8
            81: 'SDL_SCANCODE_KP_9', # KP 9
            82: 'SDL_SCANCODE_KP_MINUS', # <KP -(minus)>
            83: 'SDL_SCANCODE_KP_4', # KP 4
            84: 'SDL_SCANCODE_KP_5', # KP 5
            85: 'SDL_SCANCODE_KP_6', # KP 6
            86: 'SDL_SCANCODE_KP_PLUS', # <KP + (plus)>
            87: 'SDL_SCANCODE_KP_1', # KP 1
            88: 'SDL_SCANCODE_KP_2', # KP 2
            89: 'SDL_SCANCODE_KP_3', # KP 3
            90: 'SDL_SCANCODE_KP_0', # KP 0
            91: 'SDL_SCANCODE_KP_PERIOD', # <KP . (period)>
            92: 'SDL_SCANCODE_UNKNOWN',
            #93: '', # ZENKAKUHANKAKU
            94: 'SDL_SCANCODE_NONUSBACKSLASH', # <> '<'
            95: 'SDL_SCANCODE_F11', #F11
            96: 'SDL_SCANCODE_F12', #F12
            #97: '', # RO
            #98: '', # Katakana
            #99: '', # Hiragana
            #100: '', # Henkan
            #101: '', # Katakana/Hiragana
            #102: '', # MUHENKAN
            #103: '', # KP JP Comma
            104: 'SDL_SCANCODE_KP_ENTER', # KP Enter
            105: 'SDL_SCANCODE_RCTRL', # R-ctrl
            106: 'SDL_SCANCODE_KP_DIVIDE', # <KP / (divide)>
            107: 'SDL_SCANCODE_PRINTSCREEN', # Print Screen
            108: 'SDL_SCANCODE_RALT', # Alt gr/Ralt
            #109: '', # Linefeed
            110: 'SDL_SCANCODE_HOME', # Start
            111: 'SDL_SCANCODE_UP', # Up
            112: 'SDL_SCANCODE_PAGEUP', # Pag up
            113: 'SDL_SCANCODE_LEFT', # Left
            114: 'SDL_SCANCODE_RIGHT', # Right
            115: 'SDL_SCANCODE_END', # End
            116: 'SDL_SCANCODE_DOWN', # Down
            117: 'SDL_SCANCODE_PAGEDOWN', #Pag down
            118: 'SDL_SCANCODE_INSERT', # Insert
            119: 'SDL_SCANCODE_DELETE', # Del
            #120: # Macro
            121: 'SDL_SCANCODE_AUDIOMUTE', # Mute, or it was SDL_SCANCODE_MUTE?
            122: 'SDL_SCANCODE_VOLUMEDOWN', # Vol -
            123: 'SDL_SCANCODE_VOLUMEUP', # Vol +
            #124: '', # SC System Power Down
            #125: '', # KP Equal
            #126: '', # KP Plus Minus
            127: 'SDL_SCANCODE_PAUSE', # Pause/interrupt?
            #128: '', # SCALE? AL Compiz Scale (Expose)
            129: 'SDL_SCANCODE_KP_COMMA', # KP COMMA
            #130: '', # HANGEUL
            #131: '', # HANJA
            #132: '', # YEN
            133: 'SDL_SCANCODE_LGUI', # Super to the left
            135: 'SDL_SCANCODE_RGUI', # Super/menu? to the right
            #136: '', # COMPOSE
            #137: '', # AC Stop
            #138: '', # AC Properties
            #139: '', # AC Undo
            #140: '', # Front
            #141: '', # AC Copy
            #142: '', # AC Open
            #143: '', # AC Paste
            #144: '', # AC Search
            #145: '', # AC Cut
            #146: '', # AL Integrated Help Center
            #147: '', # Menu (show menu)
            148: 'SDL_SCANCODE_CALCULATOR', # Calculator
            #149: '', # Setup?
            #150: '', # SC System Sleep
            #151: '', # System Wake Up
            #152: '', # AL Local Machine Browser
            #153: '', # SENDFILE
            #154: '', # DELETEFILE
            #155: '', # XFER
            #156: '', # PROG1
            #157: '', # PROG2
            #158: '', # WWW
            #159: '', # MSDOS
            #160: '', # AL Terminal Lock/Screensaver
            #161: '', # DIRECTION
            #162: '', # CYCLEWINDOWS
            163: 'SDL_SCANCODE_MAIL', # Email
            164: 'SDL_SCANCODE_AC_BOOKMARKS', # Bookmark
            166: 'SDL_SCANCODE_AC_BACK', # Back
            167: 'SDL_SCANCODE_AC_FORWARD', # Forward
            #168: '', # CLOSECD
            #169: '', # EJECTCD
            #170: '', # EJECTCLODECD
            171: 'SDL_SCANCODE_AUDIONEXT', # Next, or it was SDL_SCANCODE_AUDIOFASTFORWARD?
            172: 'SDL_SCANCODE_AUDIOPLAY', # Play/Pause
            173: 'SDL_SCANCODE_AUDIOPREV', # Previous
            174: 'SDL_SCANCODE_AUDIOSTOP', # Stop
            #175: '', # RECORD
            #176: 'SDL_SCANCODE_AUDIOREWIND', # REWIND
            #177: '', # Media Select Telephone
            #178: '', # ISO
            #179: '', # AL Consumer Control Configuration
            180: 'SDL_SCANCODE_AC_HOME', # Home
            #181: '', # AC Refresh
            #182: '', # AC Exit
            #183: '', # MOVE
            #184: '', # EDIT
            #185: '', # SCROLLUP
            #186: '', # SCROLLDOWN
            #187: '', # KPLEFTPAREN
            #188: '', # KPRIGHTPAREN
            #189: '', # AC New
            #190: '', # AC Redo/Repeat
            191: 'SDL_SCANCODE_F13', #F13
            192: 'SDL_SCANCODE_F14', #F14
            193: 'SDL_SCANCODE_F15', #F15
            194: 'SDL_SCANCODE_F16', #F16
            195: 'SDL_SCANCODE_F17', #F17
            196: 'SDL_SCANCODE_F18', #F18
            197: 'SDL_SCANCODE_F19', #F19
            198: 'SDL_SCANCODE_F20', #F20
            199: 'SDL_SCANCODE_F21', #F21
            200: 'SDL_SCANCODE_F22', #F22
            201: 'SDL_SCANCODE_F23', #F23
            202: 'SDL_SCANCODE_F24', #F24
            #203: '', #
            #204: '', #
            #205: '', #
            #206: '', #
            #207: '', #
            #208: '', # PLAYCD
            #209: '', # PAUSECD
            #210: '', # PROG3
            #211: '', # PROG4
            #212: '', # AL Dashboard
            #213: 'SDL_SCANCODE_SLEEP', # Sleep/suspend
            #214: '', # AC Close
            #215: '', # PLAY
            #216: '', # FASTFORWARD
            #217: '', # BASSBOOST
            #218: '', # AC Print
            #219: '', # HP
            #220: '', # CAMERA
            #221: '', # SOUND
            #222: '', # QUESTION
            #223: '', # EMAIL
            #224: '', # CHAT
            225: 'SDL_SCANCODE_AC_SEARCH', # Search
            #226: '', # CONNECT
            #227: '', # AL Checkbook/Finance
            #228: '', # SPORT
            #229: '', # SHOP
            #230: '', # ALTERASE
            #231: '', # AC Cancel
            #232: '', # BRIGHTNESSDOWN
            #233: '', # BRIGHTNESSUP
            234: 'SDL_SCANCODE_MEDIASELECT', # Media
            #235: '', # SWITCHVIDEOMODE
            #236: '', # KBDILLUMTOGGLE
            #237: '', # KBDILLUMDOWN
            #238: '', # KBDILLUMUP
            #239: '', # AC Send
            #240: '', # AC Reply
            #241: '', # AC Forward Msg
            #242: '', # AC Save
            #243: '', # DOCUMENTS
            #244: '', # BATTERY
            #245: '', # BLUETOOTH
            #246: '', # WLAN
            #247: '', # UWB
            #248: '', # UNKNOWN
            #249: '', # VIDEO_NEXT
            #250: '', # VIDEO_PREV
            #251: '', # BRIGHTNESS_CYCLE
            #252: '', # BRIGHTNESS_ZERO
            #253: '', # DISPLAY_OFF
            #254: '', # WWAN/WIMAX
            #255: '', # RFKILL
            #256: '', # MICMUTE
        }
    elif platform == "Windows":
        switch = {
            ### <gtk keycode value>: <sdl scancode value>, #<character present on US keyboard>
            0: 'SDL_SCANCODE_UNKNOWN',

            8: 'SDL_SCANCODE_BACKSPACE', # Return/backspace
            9: 'SDL_SCANCODE_TAB', # TAB
            13: 'SDL_SCANCODE_RETURN', # # Enter/Return

            16: 'SDL_SCANCODE_LSHIFT', # L-shift
            17: 'SDL_SCANCODE_LCTRL', #L-ctrl , Alt Gr???
            18: 'SDL_SCANCODE_LALT', # L-alt
            19: 'SDL_SCANCODE_PAUSE', # Pause/interrupt?

            20: 'SDL_SCANCODE_CAPSLOCK', # Caps lock

            27: 'SDL_SCANCODE_ESCAPE', # Escape

            32: 'SDL_SCANCODE_SPACE', # Space
            33: 'SDL_SCANCODE_PAGEUP', # Pag up
            34: 'SDL_SCANCODE_PAGEDOWN', #Pag down
            35: 'SDL_SCANCODE_END', # End
            36: 'SDL_SCANCODE_HOME', # Start
            37: 'SDL_SCANCODE_LEFT', # Left
            38: 'SDL_SCANCODE_UP', # Up
            39: 'SDL_SCANCODE_RIGHT', # Right
            40: 'SDL_SCANCODE_DOWN', # Down

            45: 'SDL_SCANCODE_INSERT', # Insert
            46: 'SDL_SCANCODE_DELETE', # Del

            48: 'SDL_SCANCODE_0', # 0
            49: 'SDL_SCANCODE_1', # 1
            50: 'SDL_SCANCODE_2', # 2
            51: 'SDL_SCANCODE_3', # 3
            52: 'SDL_SCANCODE_4', # 4
            53: 'SDL_SCANCODE_5', # 5
            54: 'SDL_SCANCODE_6', # 6
            55: 'SDL_SCANCODE_7', # 7
            56: 'SDL_SCANCODE_8', # 8
            57: 'SDL_SCANCODE_9', # 9

            65: 'SDL_SCANCODE_A', # A
            66: 'SDL_SCANCODE_B', # B
            67: 'SDL_SCANCODE_C', # C
            68: 'SDL_SCANCODE_D', # D
            69: 'SDL_SCANCODE_E', # E
            70: 'SDL_SCANCODE_F', # F
            71: 'SDL_SCANCODE_G', # G
            72: 'SDL_SCANCODE_H', # H
            73: 'SDL_SCANCODE_I', # I
            74: 'SDL_SCANCODE_J', # J
            75: 'SDL_SCANCODE_K', # K
            76: 'SDL_SCANCODE_L', # L
            77: 'SDL_SCANCODE_M', # M
            78: 'SDL_SCANCODE_N', # N
            79: 'SDL_SCANCODE_O', # O
            80: 'SDL_SCANCODE_P', # P
            81: 'SDL_SCANCODE_Q', # Q
            82: 'SDL_SCANCODE_R', # R
            83: 'SDL_SCANCODE_S', # S
            84: 'SDL_SCANCODE_T', # T
            85: 'SDL_SCANCODE_U', # U
            86: 'SDL_SCANCODE_V', # V
            87: 'SDL_SCANCODE_W', # W
            88: 'SDL_SCANCODE_X', # X
            89: 'SDL_SCANCODE_Y', # Y
            90: 'SDL_SCANCODE_Z', # Z
            91: 'SDL_SCANCODE_LGUI', # Super to the left

            93: 'SDL_SCANCODE_RGUI', # Super/menu? to the right

            95: 'SDL_SCANCODE_SLEEP', # Sleep/suspend
            96: 'SDL_SCANCODE_KP_0', # KP 0
            97: 'SDL_SCANCODE_KP_1', # KP 1
            98: 'SDL_SCANCODE_KP_2', # KP 2
            99: 'SDL_SCANCODE_KP_3', # KP 3
            100: 'SDL_SCANCODE_KP_4', # KP 4
            101: 'SDL_SCANCODE_KP_5', # KP 5
            102: 'SDL_SCANCODE_KP_6', # KP 6
            103: 'SDL_SCANCODE_KP_7', # KP 7
            104: 'SDL_SCANCODE_KP_8', # KP 8
            105: 'SDL_SCANCODE_KP_9', # KP 9
            106: 'SDL_SCANCODE_KP_MULTIPLY', # <*>
            107: 'SDL_SCANCODE_KP_PLUS', # <KP + (plus)>
            109: 'SDL_SCANCODE_KP_MINUS', # <KP -(minus)>
            110: 'SDL_SCANCODE_KP_PERIOD', # <KP . (period)>
            111: 'SDL_SCANCODE_KP_DIVIDE', # <KP / (divide)>
            112: 'SDL_SCANCODE_F1', # F1
            113: 'SDL_SCANCODE_F2', # F2
            114: 'SDL_SCANCODE_F3', # F3
            115: 'SDL_SCANCODE_F4', # F4
            116: 'SDL_SCANCODE_F5', # F5
            117: 'SDL_SCANCODE_F6', # F6
            118: 'SDL_SCANCODE_F7', # F7
            119: 'SDL_SCANCODE_F8', # F8
            120: 'SDL_SCANCODE_F9', # F9
            121: 'SDL_SCANCODE_F10', #F10
            122: 'SDL_SCANCODE_F11', #F11
            123: 'SDL_SCANCODE_F12', #F12

            144: 'SDL_SCANCODE_NUMLOCKCLEAR', # Num lock

            161: 'SDL_SCANCODE_RSHIFT', # R-shift

            163: 'SDL_SCANCODE_RCTRL', # R-ctrl
            165: 'SDL_SCANCODE_RALT', # Alt gr/Ralt

            183: 'SDL_SCANCODE_CALCULATOR', # Calculator

            186: 'SDL_SCANCODE_LEFTBRACKET', # <[> <è>
            187: 'SDL_SCANCODE_RIGHTBRACKET', # <]> <+>
            188: 'SDL_SCANCODE_COMMA', # <,>
            189: 'SDL_SCANCODE_SLASH', # </> <->
            190: 'SDL_SCANCODE_PERIOD', # <.>
            191: 'SDL_SCANCODE_BACKSLASH', # <\> <ù>
            192: 'SDL_SCANCODE_SEMICOLON', # <;> <ò>

            219: 'SDL_SCANCODE_MINUS', # < - (minus)> <'>
            220: 'SDL_SCANCODE_GRAVE', # ` (grave), \
            221: 'SDL_SCANCODE_EQUALS', # < = (equal)> <ì>
            222: 'SDL_SCANCODE_APOSTROPHE', # <'> <à>

            226: 'SDL_SCANCODE_NONUSBACKSLASH', # <> '<'

        }

    return Scancodes[switch.get(param, 'SDL_SCANCODE_UNKNOWN')]
