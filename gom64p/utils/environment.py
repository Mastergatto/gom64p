#!/usr/bin/env python3
# coding=utf-8
# © 2019 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import Gtk, GLib, Gdk
import platform, pathlib, os
import ctypes.util as cu

import logging as log

###############
##   CLASS   ##
###############

class Environment:
    def __init__(self, parent):
        self.parent = parent
        self.current_path = None
        self.frontend_config_dir = None
        self.cache_dir = None
        self.wm = None
        self.modes = []
        self.current_mode = None

        self.py_version = None
        self.py_implementation = None

        self.platform = {
            "system": None,
            "release": None,
            "version": None,
            "machine": None,
            "processor": None
        }

    def get_python_info(self):
        self.py_version = platform.python_version()
        self.py_implementation = platform.python_implementation()

    def get_uname(self):
        uname = platform.uname()

        if uname.system == "Darwin":
            self.platform["system"] = "macOS"
        else:
            self.platform["system"] = uname.system
        self.platform["release"] = uname.release
        self.platform["version"] = uname.version
        self.platform["machine"] = uname.machine
        self.platform["processor"] = platform.processor()

    def query(self):
        self.get_uname()
        #print(platform.system_alias(self.platform["system"], self.platform["release"], self.platform["version"]))
        self.get_python_info()
        self.get_wm()

        log.info(f"Machine: {self.platform['system']} {self.platform['release']} {self.platform['machine']}")
        if self.platform["system"] == "Linux":
            try:
                with open("/etc/os-release", "r") as f:
                    for line in f.readlines():
                        if line.startswith("NAME"):
                            out = line[6:][:-2]
                log.info(f"Distro: {out}")
            except:
                log.info(f"Distro: N/A")
        log.info(f"Window Manager: {self.wm}")
        log.info(f"GTK version: {Gtk.MAJOR_VERSION}.{Gtk.MINOR_VERSION}.{Gtk.MICRO_VERSION}")
        log.info(f"Python: {self.py_implementation} {self.py_version}")

    def get_current_path(self):
        self.current_path = os.getcwd()
        return self.current_path

    def get_modes(self):
        if self.platform["system"] == "Windows":
            #TODO
            import win32api
            print(len(win32api.EnumDisplayMonitors()))
        elif self.platform["system"] == "macOS":
            pass
        else:
            import subprocess
            raw_output = subprocess.run('ls -1 /sys/class/drm/*/modes', shell=True, encoding="utf-8", capture_output=True)
            output = raw_output.stdout.split('\n')[:-1]
            for i in output:
                raw_modes = subprocess.check_output(['cat', i])
                modes = raw_modes.decode("utf-8").split('\n')
                for j, k in list(enumerate(modes)):
                    if modes[j] not in self.modes:
                        if modes[j] != '':
                            self.modes.append(k)

    def get_current_mode(self, all_monitors=False):
        "To be called after the main window has been realized."
        modes = []
        display = Gdk.Display.get_default()
        if all_monitors == True:
            n_monitors = display.get_n_monitors()
            log.info(f'There are {n_monitors} monitor(s).')
            for monitor in range(n_monitors):
                monitor_handle = display.get_monitor(monitor)
                geometry = monitor_handle.get_geometry()
                rate = int(round(monitor_handle.get_refresh_rate()/1000, 0))
                log.info(f'Monitor { monitor }: {geometry.width}x{geometry.height}, {rate} Hz')
                modes.append((monitor, geometry.width, geometry.height, rate))
        else:
            cur_mon = display.get_monitor_at_surface(self.parent.get_root().get_surface())
            geometry = cur_mon.get_geometry()
            rate = int(round(cur_mon.get_refresh_rate()/1000, 0))
            self.current_mode = {"width": geometry.width, "height": geometry.height, "refresh": rate}
            log.info(f'Monitor: {self.current_mode["width"]}x{self.current_mode["height"]}, {rate} Hz')

    def set_directories(self):
        # Sets up the paths for gom64p to store own config and data
        if self.platform["system"] == "macOS":
            if not os.getenv('XDG_CONFIG_HOME'):
                config_dir = f'{os.path.expanduser("~/Library/Application Support/")}gom64p/'
            else:
                config_dir = f'{os.getenv("XDG_CONFIG_HOME")}/gom64p/'
            if not os.getenv('XDG_CACHE_HOME'):
                cache_dir = f'{os.path.expanduser("~/Library/Caches/")}gom64p/'
            else:
                cache_dir = f'{os.getenv("XDG_CACHE_HOME")}/gom64p/'
        elif self.platform["system"] == "Windows":
            config_dir = f'{GLib.get_user_config_dir()}{os.sep}gom64p{os.sep}'
            cache_dir = f'{GLib.get_user_data_dir()}{os.sep}gom64p{os.sep}'
        else:
            config_dir = f'{GLib.get_user_config_dir()}{os.sep}gom64p{os.sep}'
            cache_dir = f'{GLib.get_user_cache_dir()}{os.sep}gom64p{os.sep}'

        self.frontend_config_dir = pathlib.Path(config_dir)
        if self.frontend_config_dir.is_dir() == False:
            log.warning(f'The directory doesn\'t exist! Creating one at: {self.frontend_config_dir}')
            self.frontend_config_dir.mkdir(mode=0o755)
        log.info(f'User configuration directory is: {self.frontend_config_dir}')

        self.cache_dir = pathlib.Path(cache_dir)
        if self.cache_dir.is_dir() == False:
            log.warning(f'The directory doesn\'t exist! Creating one at: {self.cache_dir}')
            self.cache_dir.mkdir(mode=0o755)
        log.info(f'User cache directory is: {self.cache_dir}')

    def get_wm(self):
        if self.platform["system"] == "macOS":
            self.wm = "Quartz"
        elif self.platform["system"] == "Windows":
            # Stay creative, Microsoft...
            self.wm = "DWM" # Desktop Window Manager
        else:
            # Linux
            if os.getenv('WAYLAND_DISPLAY'):
                self.wm = "Wayland"
            else:
                if os.getenv('DISPLAY'):
                    self.wm = "X11"
                else:
                    self.wm = "Unknown"
        return self.wm

    def set(self, parent):
        self.parent = parent
        args = parent.args

        lib = parent.frontend_conf.get("Frontend", "m64plib")
        plugindir = parent.frontend_conf.get("Frontend", "PluginsDir")
        m64p_configdir = parent.frontend_conf.get("Frontend", "ConfigDir")
        datadir = parent.frontend_conf.get("Frontend", "DataDir")

        # This frontend is fully compliant with latest api.
        parent.parameters['api_version'] = 0x020102

        # Sets the path for the library
        if args.lib:
            parent.parameters['m64plib'] = args.lib
        else:
            if lib:
                parent.parameters['m64plib'] = lib
            else:
                parent.parameters['m64plib'] = self.set_library_path()

        # Sets the path for the directory where config files are found
        if args.configdir:
            parent.parameters['configdir'] = args.configdir
        else:
            if m64p_configdir:
                parent.parameters['configdir'] = m64p_configdir
            else:
                parent.parameters['configdir'] = ""

        # Sets the path for the directory where plugins are found
        if args.plugindir:
            parent.parameters['pluginsdir'] = args.plugindir
        else:
            if plugindir:
                parent.parameters['pluginsdir'] = plugindir
            else:
                parent.parameters['pluginsdir'] = self.set_plugins_dir_path()

        # Sets the path for the directory where user generated data are found
        if args.datadir:
            parent.parameters['datadir'] = args.datadir
        else:
            if datadir:
                parent.parameters['datadir'] = datadir
            else:
                parent.parameters['datadir'] = ""

        # And now we set the path for each plugin
        parent.parameters['gfx'] = parent.frontend_conf.get("Frontend", "GfxPlugin")
        parent.parameters['audio'] = parent.frontend_conf.get("Frontend", "AudioPlugin")
        parent.parameters['input'] = parent.frontend_conf.get("Frontend", "InputPlugin")
        parent.parameters['rsp'] = parent.frontend_conf.get("Frontend", "RSPPlugin")

    def set_library_path(self):
        if self.platform["system"] == 'Windows':
            #note: the windows build it is just a bunch of files thrown into a .zip
            #For now let's tell to the frontend that the user has to manually point the libraries.
            #return 1
            pass
        elif self.platform["system"] == 'Linux':
            library = self.find_library_so("mupen64plus")

            if library != None:
                return library

        elif self.platform["system"] == "macOS":
            # TODO: Untested
            library = cu.find_library("mupen64plus")
            print(library)
        else:
            log.warning("Platform not supported.")

    def set_plugins_dir_path(self):
        if self.platform["system"] == "Windows":
            #note: the windows build it is just a bunch of files thrown into a .zip
            #For now let's tell to the frontend that the user has to manually point the libraries.
            #return 1
            pass
        elif self.platform["system"] == "Linux":
            library = self.find_library_so('mupen64plus')

            if library != None:
                path = pathlib.Path(library)
                # This goes up in the hierarchy
                parent = path.parent
                # Let's hope that all distros follow same logic
                plugins_directory = str(parent) + "/mupen64plus/"
                return plugins_directory
        elif self.platform["system"] == "macOS":
            # TODO: Untested
            library = cu.find_library("mupen64plus")
            if library != None:
                path = pathlib.Path(library)
                # This goes up in the hierarchy
                parent = path.parent
                # Let's hope that all distros follow same logic
                plugins_directory = str(parent) + "/mupen64plus/"
                return plugins_directory
        else:
            log.warning("Platform not supported.")

    def find_library_so(self, name):
        # This function is taken directly by Lib/ctypes/util.py, but with the modified variable regex.
        import struct, os, re, subprocess
        if struct.calcsize('l') == 4:
            machine = self.platform["machine"] + "-32"
        else:
            machine = self.platform["machine"] + "-64"
        mach_map = {
            'x86_64-64': 'libc6,x86-64',
            'ppc64-64': 'libc6,64bit',
            'sparc64-64': 'libc6,64bit',
            's390x-64': 'libc6,64bit',
            'ia64-64': 'libc6,IA-64',
            }
        abi_type = mach_map.get(machine, 'libc6')

        # XXX assuming GLIBC's ldconfig (with option -p)
        regex = r'lib%s\.[^\s]+\s\(%s(?:,\s.*)?\)\s=>\s(.*)'
        regex = os.fsencode(regex % (re.escape(name), abi_type))
        try:
            with subprocess.Popen(['/sbin/ldconfig', '-p'],
                                  stdin=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL,
                                  stdout=subprocess.PIPE,
                                  env={'LC_ALL': 'C', 'LANG': 'C'}) as p:
                res = re.search(regex, p.stdout.read())
                if res:
                    return os.fsdecode(res.group(1))
        except OSError:
            pass

    def find_library_so_alternative(self, name):
        # Found on stackoverflow
        import struct, os, re, subprocess
        # see ctypes.find_library code
        uname = self.platform["machine"]
        if uname.startswith("arm"):
            uname = "arm"
        if struct.calcsize('l') == 4:
            machine = uname + '-32'
        else:
            machine = uname + '-64'
        mach_map = {
            'x86_64-64': 'libc6,x86-64',
            'ppc64-64': 'libc6,64bit',
            'sparc64-64': 'libc6,64bit',
            's390x-64': 'libc6,64bit',
            'ia64-64': 'libc6,IA-64',
            'arm-32': 'libc6(,hard-float)?',
            }
        abi_type = mach_map.get(machine, 'libc6')
        # Note, we search libXXX.so.XXX, not just libXXX.so (!)
        expr = re.compile(r'^\s+lib%s\.so.[^\s]+\s+\(%s.*=>\s+(.*)$' % (re.escape(name), abi_type))
        p = subprocess.Popen(['ldconfig', '-N', '-p'], stdout=subprocess.PIPE)
        result = None
        for line in p.stdout:
            res = expr.match(line.decode())
            if res is None:
                continue
            if result is not None:
                raise RuntimeError('Duplicate library found for %s' % name)
            result = res.group(1)
        if p.wait():
            raise RuntimeError('"ldconfig -p" failed')
        if result is None:
            raise RuntimeError('Library %s not found' % name)
        return result
