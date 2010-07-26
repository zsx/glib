#!/usr/bin/env python
# encoding: utf-8
import re
from waflib.Context import STDOUT, STDERR

glib_major_version = 2
glib_minor_version = 25
glib_micro_version = 12
#the following to variables are required
VERSION = '%d.%d.%d.' % (glib_major_version, glib_minor_version, glib_micro_version)
APPNAME = 'glib'

STDC_CODE1='''
/* end confdefs.h.  */
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <float.h>

int
main ()
{

  %s;
  return 0;
}
'''
STDC_CODE2='''
#include <ctype.h>
#include <stdlib.h>
#if ((' ' & 0x0FF) == 0x020)
# define ISLOWER(c) ('a' <= (c) && (c) <= 'z')
# define TOUPPER(c) (ISLOWER(c) ? 'A' + ((c) - 'a') : (c))
#else
# define ISLOWER(c) \
		   (('a' <= (c) && (c) <= 'i') \
		     || ('j' <= (c) && (c) <= 'r') \
		     || ('s' <= (c) && (c) <= 'z'))
# define TOUPPER(c) (ISLOWER(c) ? ((c) | 0x40) : (c))
#endif

#define XOR(e, f) (((e) && !(f)) || (!(e) && (f)))
int
main ()
{
  int i;
  for (i = 0; i < 256; i++)
    if (XOR (islower (i), ISLOWER (i))
	|| toupper (i) != TOUPPER (i))
      return 2;
  return 0;
}
'''
def options(opt):
	glib_debug_default = 'minimum' 
	if glib_minor_version % 2:
		 glib_debug_default = 'yes'
	cfg = opt.parser.get_option_group('--prefix')
	bld = opt.parser.get_option_group('-p')

	bld.add_option('--debug', action='store', default=glib_debug_default, dest='debug', metavar='yes/no/minimum', help='turn on debugging [default: %s]' % glib_debug_default)
	cfg.add_option('--enable-gc-friendly', action='store_true', default=False, dest='gc_friendly', help='turn on garbage collector friendliness') 
	cfg.add_option('--disable-mem-pools', action='store_false', default=True, dest='mem_pools', help='disable all glib memory pools') 
	cfg.add_option('--disable-threads', action='store_false', default=True, dest='threads', help='Disable basic thread support (will override --with-threads)') 
	cfg.add_option('--disable-rebuilds', action='store_false', default=True, dest='rebuilds', help='disable all source autogeneration rules') 
	bld.add_option('--disable-visibility', action='store_false', default=True, dest='visibility', help="don't use ELF visibility attributes") 
	cfg.add_option('--with-runtime-libdir', metavar='RELPATH', action='store', default='', dest='runtime_libdir', help="Install runtime libraries relative to libdir") 
	cfg.add_option('--with-threads', metavar='none/posix/dce/win32', action='store', default='', dest='want_threads', help="specify a thread implementation to use") 
	cfg.add_option('--with-libiconv', metavar='no/yes/maybe/gnu/native', action='store', default='maybe', dest='libiconv', help="use the libiconv library") 
	opt.tool_options('compiler_c')

def configure(cfg):
	cfg.check_tool('compiler_c')
	cfg.check_large_file()
	cfg.check_cfg(atleast_pkgconfig_version='0.16')
	cfg.find_program('perl', var='PERL')
	cfg.check_tool('python')
	cfg.check_python_version(minver=(2, 4))
	
	#iconv detection
	if cfg.get_dest_binfmt == 'pe':
		cfg.options.libiconv = 'native'
	else:
		if cfg.options.libiconv == 'maybe':
			found_iconv = False
			if cfg.check_cc(function_name='iconv_open', header_name='iconv.h', msg = 'checking for iconv_open in C library', mandatory=False, uselib_store='ICONV'):
				found_iconv = True
			elif cfg.check_cc(function_name='libiconv_open', header_name='iconv.h', lib='iconv', msg='checking for libiconv_open in GNU libiconv', mandatory=False, defines=['USE_LIBICONV_GNU'], uselib_store='ICONV'):
				found_iconv = True
			elif cfg.check_cc(function_name='iconv_open', header_name='iconv.h', lib='iconv', msg='checking for iconv_open in the system library iconv', mandatory=False, defines='USE_LIBICONV_NATIVE', uselib_store='ICONV'):
				found_iconv = True
			if not found_iconv:
				cfg.fatal('No iconv() implementation found in C library or libiconv')
		elif cfg.options.libiconv == 'no':
			cfg.check_cc(function_name='iconv_open', header_name='iconv.h', msg = 'checking for iconv_open in C library', uselib_store='ICONV')
		elif cfg.options.libiconv in ('yes', 'gnu'):
			cfg.check_cc(function_name='libiconv_open', header_name='iconv.h', lib='iconv', msg='checking for libiconv_open in GNU libiconv', defines=['USE_LIBICONV_GNU'], uselib_store='ICONV')
		elif cfg.options.libiconv == 'native':
			cfg.check_cc(function_name='iconv_open', header_name='iconv.h', lib='iconv', msg='checking for iconv_open in the system library iconv', defines='USE_LIBICONV_NATIVE', uselib_store='ICONV')

	# DU4 native cc currently needs -std1 for ANSI mode (instead of K&R)
	if not cfg.check_cc(fragment='#include <math.h>\nint main (void) {return (log(1) != log(1.));}', lib='m', msg='checking for extra flags for ansi library types', okmsg='None', uselib_store='ANSI', mandatory=False):
		if not cfg.check_cc(fragment='#include <math.h>\nint main (void) {return (log(1) != log(1.));}', lib='m', ccflags='-std1', msg='checking for -std1 for ansi library types', okmsg='-std1', uselib_store='ANSI', mandatory=False):
			conf.warn("No ANSI protypes found in library (-std1 didn't work)")
	# NeXTStep cc seems to need this
	if not cfg.check_cc(fragment='#include <dirent.h>\nint main (void) {DIR *dir;\nreturn 0;}', msg='checking for extra flags for posix compliance', okmsg='None', uselib_store='POSIX', mandatory=False):
		cfg.check_cc(fragment='#include <dirent.h>\nint main (void) {DIR *dir;\nreturn 0;}', ccflags='-posix', msg='checking for -std1 for ansi library types', errmsg="Could not determine POSIX flag (-posix didn't work)", uselib_store='POSIX', mandatory=False)
	
	cfg.check_cc(function_name='vprintf', header_name=['stdarg.h', 'stdio.h'])
	cfg.check_cc(fragment='#include <alloca.h>\nint main(void){ alloca(0); return 0;}', msg='checking for alloca')

	if cfg.check_cc(fragment=STDC_CODE1 % '', msg='checking for ANSI C header files', mandatory=False):
		# SunOS 4.x string.h does not declare mem*, contrary to ANSI.
		if cfg.check_cc(fragment='#include <string.h>\n' + STDC_CODE1 % 'memchr(NULL, 0, 0)', mandatory=False):
		
	cfg.write_config_header('config.h')
	print ("env = %s" % cfg.env)
	print ("options = ", cfg.options)

def build(bld):
	if bld.options.debug == 'yes':
		GLIB_DEBUG_DEFINES = ['G_ENABLE_DEBUG']
	else:
		GLIB_DEBUG_DEFINES = ['G_DISABLE_CAST_CHECKS']
		if bld.options.debug == 'no':
			GLIB_DEBUG_DEFINES.extend (['G_DISABLE_ASSERT', 'G_DISABLE_CHECKS'])
	bld.env.DEFINES = GLIB_DEBUG_DEFINES
	pass
