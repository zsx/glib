# vim: ft=python expandtab

Import('env prefix')

env_glib = env.Clone()

GLIB_MAJOR_VERSION=2
GLIB_MINOR_VERSION=21
GLIB_MICRO_VERSION=6
GLIB_INTERFACE_AGE=0
GLIB_BINARY_AGE=GLIB_MINOR_VERSION * 100 + GLIB_MICRO_VERSION
GLIB_VERSION="%d.%d.%d" % (GLIB_MAJOR_VERSION, GLIB_MINOR_VERSION, GLIB_MICRO_VERSION)

env_glib['DOT_IN_SUBS'] = {'@PACKAGE_VERSION@': GLIB_VERSION,
			   '@VERSION@': GLIB_VERSION,
			   '@GLIB_MAJOR_VERSION@': str(GLIB_MAJOR_VERSION),
			   '@GLIB_MINOR_VERSION@': str(GLIB_MINOR_VERSION),
			   '@GLIB_MICRO_VERSION@': str(GLIB_MICRO_VERSION),
                           '@GLIB_VERSION@': GLIB_VERSION,
                           '@GLIB_INTERFACE_AGE@': str(GLIB_INTERFACE_AGE),
                           '@GLIB_BINARY_AGE@': str(GLIB_BINARY_AGE),
                           '-@LT_CURRENT_MINUS_AGE@': '',
			   '@prefix@': prefix,
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
ipc = []
pcs = ('glib-2.0.pc',
       'gio-2.0.pc',
       'gio-unix-2.0.pc',
       'gmodule-2.0.pc',
       'gmodule-export-2.0.pc',
       'gmodule-no-export-2.0.pc',
       'gthread-2.0.pc',
       'gobject-2.0.pc')

for pc in pcs:
    env_glib.DotIn(pc, pc + '.in')
    ipc.append(env_glib.Install(prefix + '/lib/pkgconfig', pc))

env_glib.DotIn('config.h', 'config.h.win32.in')
env_glib.DotIn('glibconfig.h', 'glibconfig.h.win32.in')
env_glib.DotIn('glib-gettextize', 'glib-gettextize.in')

iheader = env_glib.Install(prefix + '/lib/include', 'glibconfig.h')
ibin = env_glib.Install(prefix + '/bin', 'glib-gettextize')

subdirs = ['glib/SConscript',
           'gmodule/SConscript',
           'gthread/SConscript',
           'gobject/SConscript',
           'gio/SConscript',
           'win32/libintl-proxy/SConscript']
if ARGUMENTS.get('build_test', 0):
    subdirs += ['tests/SConscript']

SConscript(subdirs, exports=['env_glib', 'prefix'])

env_glib.Depends('glib/SConscript', 'config.h')

Alias('install', [iheader, ibin] + ipc)
