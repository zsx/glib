# vim: ft=python expandtab
import os
from site_init import *

opts = Variables()
opts.Add(PathVariable('PREFIX', 'Installation prefix', os.path.expanduser('~/FOSS'), PathVariable.PathIsDirCreate))
opts.Add(BoolVariable('DEBUG', 'Build with Debugging information', 0))
opts.Add(PathVariable('PERL', 'Path to the executable perl', r'C:\Perl\bin\perl.exe', PathVariable.PathIsFile))
opts.Add(BoolVariable('WITH_OSMSVCRT', 'Link with the os supplied msvcrt.dll instead of the one supplied by the compiler (msvcr90.dll, for instance)', 0))

env = Environment(variables = opts,
                  ENV=os.environ, tools = ['default', GBuilder])
GLIB_MAJOR_VERSION=2
GLIB_MINOR_VERSION=24
GLIB_MICRO_VERSION=1
GLIB_INTERFACE_AGE=1
GLIB_BINARY_AGE=GLIB_MINOR_VERSION * 100 + GLIB_MICRO_VERSION
GLIB_VERSION="%d.%d.%d" % (GLIB_MAJOR_VERSION, GLIB_MINOR_VERSION, GLIB_MICRO_VERSION)

env['PACKAGE_NAME'] = 'glib'
env['PACKAGE_VERSION'] = GLIB_VERSION
env['DOT_IN_SUBS'] = {'@PACKAGE_VERSION@': GLIB_VERSION,
		      '@VERSION@': GLIB_VERSION,
                      '@GLIB_MAJOR_VERSION@': str(GLIB_MAJOR_VERSION),
                      '@GLIB_MINOR_VERSION@': str(GLIB_MINOR_VERSION),
                      '@GLIB_MICRO_VERSION@': str(GLIB_MICRO_VERSION),
                      '@GLIB_VERSION@': GLIB_VERSION,
                      '@GLIB_INTERFACE_AGE@': str(GLIB_INTERFACE_AGE),
                      '@GLIB_BINARY_AGE@': str(GLIB_BINARY_AGE),
                      '@GETTEXT_PACKAGE@': "glib20",
                      '-@LT_CURRENT_MINUS_AGE@': '',
                      '@prefix@': env['PREFIX'],
                      '@exec_prefix@': '${prefix}/bin',
                      '@libdir@': '${prefix}/lib',
                      '@includedir@': '${prefix}/include',
                      '@ICONV_LIBS@': "-liconv",
                      '@INTLLIBS@': '-lintl-proxy',
                      '@GLIB_EXTRA_CFLAGS@': '',
                      '@G_MODULE_SUPPORTED@': '1',
                      '@G_MODULE_LDFLAGS@': '',
                      '@G_MODULE_LIBS@': '',
                      '@GIO_MODULE_DIR@': '${libdir}/gio/modules',
                      '@G_THREAD_LIBS@': '',
                      '@G_THREAD_CFLAGS@': '',
                      '@GLIB_WIN32_STATIC_COMPILATION_DEFINE@': ''}
pcs = ('glib-2.0.pc',
       'gio-2.0.pc',
       'gio-unix-2.0.pc',
       'gmodule-2.0.pc',
       'gmodule-export-2.0.pc',
       'gmodule-no-export-2.0.pc',
       'gthread-2.0.pc',
       'gobject-2.0.pc')

for pc in pcs:
    env.DotIn(pc, pc + '.in')
InstallDev('$PREFIX/lib/pkgconfig', pcs, env)

env.DotIn('config.h', 'config.h.win32.in')
env.DotIn('glibconfig.h', 'glibconfig.h.win32.in')
env.DotIn('glib-gettextize', 'glib-gettextize.in')

InstallDev('$PREFIX/lib/glib-2.0/include', 'glibconfig.h', env)
InstallDev('$PREFIX/bin', 'glib-gettextize', env)

env.AppendENVPath('PATH', '#glib;#win32/libintl-proxy')

GInitialize(env)

if env['WITH_OSMSVCRT']:
    env['LIB_SUFFIX'] = '-0'
    env.Append(CPPDEFINES=['MSVCRT_COMPAT_STAT', 'MSVCRT_COMPAT_IO'])

subdirs = ['glib/SConscript',
           'gmodule/SConscript',
           'gthread/SConscript',
           'gobject/SConscript',
           'gio/SConscript',
           'win32/libintl-proxy/SConscript']
if ARGUMENTS.get('build_test', 0):
    subdirs += ['tests/SConscript']

SConscript(subdirs, exports=['env'])
DumpInstalledFiles(env)
