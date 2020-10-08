project('gom64p', 'c',
    version: '0.0.1',
    meson_version: '>= 0.50.0',)

# Importing modules
gnome = import('gnome')
i18n  = import('i18n')
python = import('python')

# Module objects
py_installation = python.find_installation('python3')

# Make sure Python is installed and found
if not py_installation.found()
    error('No valid python3 binary found')
endif

# Constants
PACKAGE_URL = 'https://github.com/Mastergatto/gom64p'
PACKAGE_URL_BUG = 'https://github.com/Mastergatto/gom64p/issues'
PROJECT_RDNN_NAME = 'net.Mastergatto.gom64p'


# NAME_SUFFIX is used in the about dialog
if get_option('profile') == 'development'
  PROFILE = '.Devel'
  NAME_SUFFIX = ' (Development Snapshot)'
else
  PROFILE = ''
  NAME_SUFFIX = ''
endif

APPLICATION_ID = 'net.Mastergatto.gom64p@0@'.format(PROFILE)
PYTHON_DIR = py_installation.get_path('purelib')
PKGDATA_DIR = join_paths(get_option('prefix'), get_option('datadir'), APPLICATION_ID)
PKGLIB_DIR = join_paths(get_option('prefix'), get_option('libdir'), APPLICATION_ID)



message('Looking for dependencies')
dependency('gobject-introspection-1.0', version: '>= 1.35.0')
dependency('gtk+-3.0', version: '>= 3.22.1')
dependency('pygobject-3.0', version: '>= 3.29.1')

#subdir('data/ui')
#subdir('data/icons')
subdir('data')
#subdir('help')
#subdir('po')

install_subdir(
    'gom64p',
    install_dir: py_installation.get_install_dir()
)



# Install the executable file
bin_config = configuration_data()
bin_config.set('application_id', APPLICATION_ID)
bin_config.set('rdnn_name', PROJECT_RDNN_NAME)
bin_config.set('pkgdatadir', PKGDATA_DIR)
bin_config.set('localedir', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))
bin_config.set('pythondir', PYTHON_DIR)
bin_config.set('schemasdir', PKGDATA_DIR)

bin_config.set('local_build', 'False')
bin_config.set('PYTHON', py_installation.path())

configure_file(
    input: 'gom64p.in',
    output: 'gom64p',
    configuration: bin_config,
    install_mode: 'rwxr-xr-x',
    install: true,
    install_dir: get_option('bindir')
)

# Install the builddir executable
local_config = configuration_data()
local_config.set('application_id', APPLICATION_ID)
local_config.set('rdnn_name', PROJECT_RDNN_NAME)
local_config.set('pkgdatadir', join_paths(meson.build_root(), 'data'))
local_config.set('localedir', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))
local_config.set('pythondir', meson.source_root())
local_config.set('schemasdir', join_paths(meson.build_root(), 'data'))

local_config.set('local_build', 'True')
local_config.set('PYTHON', py_installation.path())

configure_file(
    input: 'gom64p.in',
    output: 'local-gom64p',
    configuration: local_config
)

meson.add_postconf_script('build-aux/meson/post_conf.py')
meson.add_install_script('build-aux/meson/post_install.py')
