#!/usr/bin/python3
# coding=utf-8
# © 2018 Mastergatto
# This code is covered under GPLv2+, see LICENSE
#####################

#############
## MODULES ##
#############
import platform, pathlib
import ctypes.util as cu

import global_module as g

###############
##   CLASS   ##
###############

class Platform:
    def __init__(self):
        system = platform.system()
        #print(system)

        if system == 'Windows':
            #note: the windows build it is just a bunch of files thrown into a .zip
            #For now let's tell to the frontend that the user has to manually point the libraries.
            #return 1
            pass
        elif system == 'Linux':
            if g.parameters['m64plib'] == '':
                library = self.find_library_so('mupen64plus')
                #print(library)

                if library != None:
                    g.parameters['m64plib'] = library
                    path = pathlib.Path(library)
                    parent = path.parent
                    # Let's hope that all distros follow same logic
                    plugins_directory = str(parent) + "/mupen64plus/"
                    if g.parameters['pluginsdir'] == '':
                        g.parameters['pluginsdir'] = plugins_directory

        elif system == 'Darwin':
            #Does Mac OS X support python 3?
            # For now, Mac OS X is unsupported.
            library = cu.find_library("mupen64plus")
            print(library)
        else:
            print("Platform not supported.")


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
