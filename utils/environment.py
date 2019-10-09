#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
from gi.repository import GLib
import platform, pathlib, os
import ctypes.util as cu

import logging as log

###############
##   CLASS   ##
###############

class Environment:
    def __init__(self):
        self.parent = None
        self.system = platform.system()
        self.current_path = None
        self.frontend_config_dir = None
        self.cache_dir = None

    def query(self):
        return self.system

    def set_current_path(self):
        self.current_path = os.getcwd()
        return self.current_path

    def set_directories(self):
        # Sets up the paths for gom64p to store own config and data
        if self.system == "Darwin":
            if not os.getenv('XDG_CONFIG_HOME'):
                config_dir = f'{os.path.expanduser("~/Library/Application Support/")}gom64p/'
            else:
                config_dir = f'{os.getenv("XDG_CONFIG_HOME")}/gom64p/'
            if not os.getenv('XDG_CACHE_HOME'):
                cache_dir = f'{os.path.expanduser("~/Library/Caches/")}gom64p/'
            else:
                cache_dir = f'{os.getenv("XDG_CACHE_HOME")}/gom64p/'
        else:
            config_dir = f'{GLib.get_user_config_dir()}{os.sep}gom64p/'
            cache_dir = f'{GLib.get_user_cache_dir()}{os.sep}gom64p/'

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

    def set(self, parent):
        self.parent = parent
        args = parent.args

        lib = parent.frontend_conf.get('m64plib')
        plugindir = parent.frontend_conf.get('PluginsDir')
        m64p_configdir = parent.frontend_conf.get('ConfigDir')
        datadir = parent.frontend_conf.get('DataDir')

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
        parent.parameters['gfx'] = parent.frontend_conf.get('GfxPlugin')
        parent.parameters['audio'] = parent.frontend_conf.get('AudioPlugin')
        parent.parameters['input'] = parent.frontend_conf.get('InputPlugin')
        parent.parameters['rsp'] = parent.frontend_conf.get('RSPPlugin')

    def set_library_path(self):
        if self.system == 'Windows':
            #note: the windows build it is just a bunch of files thrown into a .zip
            #For now let's tell to the frontend that the user has to manually point the libraries.
            #return 1
            pass
        elif self.system == 'Linux':
            library = self.find_library_so('mupen64plus')

            if library != None:
                return library

        elif self.system == 'Darwin':
            # Does Mac OS X support python 3?
            # TODO: Untested
            library = cu.find_library("mupen64plus")
            print(library)
        else:
            log.warning("Platform not supported.")

    def set_plugins_dir_path(self):
        if self.system == 'Windows':
            #note: the windows build it is just a bunch of files thrown into a .zip
            #For now let's tell to the frontend that the user has to manually point the libraries.
            #return 1
            pass
        elif self.system == 'Linux':
            library = self.find_library_so('mupen64plus')

            if library != None:
                path = pathlib.Path(library)
                # This goes up in the hierarchy
                parent = path.parent
                # Let's hope that all distros follow same logic
                plugins_directory = str(parent) + "/mupen64plus/"
                return plugins_directory
        elif self.system == 'Darwin':
            # Does Mac OS X support python 3?
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
            machine = os.uname().machine + '-32'
        else:
            machine = os.uname().machine + '-64'
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
        uname = os.uname()[4]
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
