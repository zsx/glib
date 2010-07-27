#!/usr/bin/env python
# encoding: utf-8
import re
from waflib.Context import STDOUT, STDERR
from waflib.Configure import conf, ConfigurationError
from waflib.TaskGen import feature, before

glib_major_version = 2
glib_minor_version = 25
glib_micro_version = 12
#the following to variables are required
VERSION = '%d.%d.%d.' % (glib_major_version, glib_minor_version, glib_micro_version)
APPNAME = 'glib'

STDC_CODE1='''
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <float.h>

int
main ()
{
  return 0;
}
'''

STDC_IRIX_4_0_5='''
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

ALLOCA_CODE='''
#ifdef __GNUC__
# define alloca __builtin_alloca
#else
# ifdef _MSC_VER
#  include <malloc.h>
#  define alloca _alloca
# else
#  ifdef HAVE_ALLOCA_H
#   include <alloca.h>
#  else
#   ifdef _AIX
 #pragma alloca
#   else
#    ifndef alloca /* predefined by HP cc +Olibcalls */
char *alloca ();
#    endif
#   endif
#  endif
# endif
#endif

int
main ()
{
	char *p = (char *) alloca (1);
	if (p) return 0;
	return 0;
}
'''

GNU_2_1_CODE='''
#include <features.h>
#ifdef __GNU_LIBRARY__
 #if (__GLIBC__ == 2 && __GLIBC_MINOR__ >= 1) || (__GLIBC__ > 2)
  #error "Not glibc 2.1"
 #endif
#else
  #error "Not a glibc library"
#endif

int main()
{
	return 0;
}
'''

@feature('test_stdc_headers')
@before('process_source')
def test_stdc_headers(self):
	def write_test_file(task):
		task.outputs[0].write(task.generator.code)

	def write_find_symbols(task):
		task.outputs[0].write(task.generator.code)
		bld = task.generator.bld
		if bld.env.CC_NAME == 'msvc':
			cpp = bld.env['CC'] + ['/E']
		else:
			cpp = bld.env['CC'] + ['-E']

		if bld.cmd_and_log(cpp + [task.outputs[0].abspath()]).find(task.generator.symbol) < 0:
			bld.fatal("symbols %r is not found" % task.generator.symbol)

	bld = self.bld
	
	bld(rule=write_test_file, target='stdc_code.c', code=STDC_CODE1) 
	bld(rule=write_test_file, target='stdc_irix.c', code=STDC_IRIX_4_0_5)

	bld(features='cprogram', sources='stdc_code.c', target='test_stdc') 

	#SunOS 4.x string.h does not declare mem*, contrary to ANSI.
	bld(rule=write_find_symbols, target='stdc_sunos.c', code='#include <string.h>', symbol='memchr')

	#ISC 2.0.2 stdlib.h does not declare free, contrary to ANSI.
	bld(rule=write_find_symbols, target='stdc_isc.c', code='#include <stdlib.h>', symbol='free')

	bld(features='cprogram', sources='stdc_isc.c', target='test_isc') 

@conf
def check_stdc_headers(self):
	self.check(compile_filename=[],
		msg = 'Checking for ANSI header files',
		features = 'test_stdc_headers')
	self.define('STDC_HEADERS', 1)
	return True

@conf
def check_libiconv(self, iconv):
	if iconv == 'maybe':
		found_iconv = False
		if self.check_cc(function_name='iconv_open', header_name='iconv.h', msg = 'checking for iconv_open in C library', mandatory=False, uselib_store='ICONV'):
			found_iconv = True
		elif self.check_cc(function_name='libiconv_open', header_name='iconv.h', lib='iconv', msg='checking for libiconv_open in GNU libiconv', mandatory=False, defines=['USE_LIBICONV_GNU'], uselib_store='ICONV'):
			found_iconv = True
		elif self.check_cc(function_name='iconv_open', header_name='iconv.h', lib='iconv', msg='checking for iconv_open in the system library iconv', mandatory=False, defines='USE_LIBICONV_NATIVE', uselib_store='ICONV'):
			found_iconv = True
		if not found_iconv:
			self.fatal('No iconv() implementation found in C library or libiconv')
	elif iconv == 'no':
		self.check_cc(function_name='iconv_open', header_name='iconv.h', msg = 'checking for iconv_open in C library', uselib_store='ICONV')
	elif iconv in ('yes', 'gnu'):
		self.check_cc(function_name='libiconv_open', header_name='iconv.h', lib='iconv', msg='checking for libiconv_open in GNU libiconv', defines=['USE_LIBICONV_GNU'], uselib_store='ICONV')
	elif iconv == 'native':
		self.check_cc(function_name='iconv_open', header_name='iconv.h', lib='iconv', msg='checking for iconv_open in the system library iconv', defines='USE_LIBICONV_NATIVE', uselib_store='ICONV')
	else:
		self.fatal('Unknown parameter to --with-libiconv')

@conf
def check_allca(self):
	# The Ultrix 4.2 mips builtin alloca declared by alloca.h only works
	# for constant arguments.  Useless!
	self.check_cc(fragment='#include <alloca.h>\nint main(void){char *p = (char *) alloca (2 * sizeof (int));if (p) return 0; return 1;}', msg='checking for alloca.h', define_name='HAVE_ALLOCA_H', mandatory=False)

	if not self.check_cc(fragment=ALLOCA_CODE, msg='checking for alloca', define_name='HAVE_ALLOCA'):
		# The SVR3 libPW and SVR4 libucb both contain incompatible functions
		# that cause trouble.  Some versions do not even contain alloca or
		# contain a buggy version.  If you still want to use their alloca,
		# use ar to extract alloca.o from them instead of compiling alloca.c.
		# ALLOCA=\${LIBOBJDIR}alloca.$ac_objext
		#self.define('C_ALLOCA', 1)
		raise Exception('NotImplemented')
	try:
		self.check_cc(fragment='#if ! defined CRAY || defined CRAY2\n#error "Not CRAY"\n#endif\nint main(){ return 0;}', msg="checking whether 'alloca.c' needs Cray hooks", errmsg='No')
	except ConfigurationError:
		#Not Cray
		pass
	else:
		raise Exception('NotImplemented')
		''' 
		for func in ('_getb67', 'GETB67', 'getb67'):
			if self.check_cc(function_name=func):
				self.define('CRAY_STACKSEG_END', func)
				break	
		else:
			return False
		'''
@conf
def is_gnu_library_2_1(self):
	try:
		self.check_cc(fragment=GNU_2_1_CODE, msg="checking whether glibc 2.1", errmsg='No')
	except ConfigurationError:
		return False
	else:	
		return True
	
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
	cfg.add_option('--enable-iconv-cache', action='store_true', default=None, dest='iconv_cache', help="cache iconv descriptors [default: auto]") 
	opt.tool_options('compiler_c')

def configure(cfg):
	cfg.check_tool('compiler_c')
	cfg.check_large_file()
	cfg.check_cfg(atleast_pkgconfig_version='0.16')
	cfg.find_program('perl', var='PERL')
	cfg.check_tool('python')
	cfg.check_python_version(minver=(2, 4))
	
	#iconv detection
	if cfg.get_dest_binfmt() == 'pe':
		cfg.options.libiconv = 'native'
	else:
		cfg.check_libiconv(cfg.options.libiconv)

	# DU4 native cc currently needs -std1 for ANSI mode (instead of K&R)
	if not cfg.check_cc(fragment='#include <math.h>\nint main (void) {return (log(1) != log(1.));}', msg='checking for extra flags for ansi library types', okmsg='None', uselib_store='ANSI', mandatory=False):
		if not cfg.check_cc(fragment='#include <math.h>\nint main (void) {return (log(1) != log(1.));}', lib='m', msg='checking for extra flags for ansi library types', okmsg='None', uselib_store='ANSI', mandatory=False):
			cfg.check_cc(fragment='#include <math.h>\nint main (void) {return (log(1) != log(1.));}', lib='m', ccflags='-std1', msg='checking for -std1 for ansi library types', okmsg='-std1', errmsg="No ANSI protypes found in library (-std1 didn't work)", uselib_store='ANSI', mandatory=False)

	# NeXTStep cc seems to need this
	if not cfg.check_cc(fragment='#include <dirent.h>\nint main (void) {DIR *dir;\nreturn 0;}', msg='checking for extra flags for posix compliance', okmsg='None', uselib_store='POSIX', mandatory=False):
		cfg.check_cc(fragment='#include <dirent.h>\nint main (void) {DIR *dir;\nreturn 0;}', ccflags='-posix', msg='checking for -posix for posix compliance', errmsg="Could not determine POSIX flag (-posix didn't work)", uselib_store='POSIX', mandatory=False)
	
	cfg.check_cc(function_name='vprintf', header_name=['stdarg.h', 'stdio.h'])
	cfg.check_allca()
	cfg.check_stdc_headers()

	if cfg.options.iconv_cache == None and cfg.get_dest_binfmt() != 'pe' and not cfg.is_gnu_library_2_1():
		cfg.options.iconv_cache = True
	if cfg.options.iconv_cache:
		cfg.define('NEED_ICONV_CACHE', 1)
	
	try:
		cfg.check_cfg(package='zlib')
	except ConfigurationError:
		cfg.check_cc(function_name='inflate', lib='z', header_name='zlib.h', uselib_store='ZLIB')

	if not cfg.options.mem_pools:	
		cfg.define('DISABLE_MEM_POOLS', 1)
	if cfg.options.gc_friendly:
		cfg.define('ENABLE_GC_FRIENDLY_DEFAULT', 1)
	for x in 'dirent.h float.h limits.h pwd.h grp.h sys/param.h sys/poll.h sys/resource.h \
sys/time.h sys/times.h sys/wait.h unistd.h values.h \
sys/select.h sys/types.h stdint.h inttypes.h sched.h malloc.h \
sys/vfs.h sys/mount.h sys/vmount.h sys/statfs.h sys/statvfs.h \
mntent.h sys/mnttab.h sys/vfstab.h sys/mntctl.h sys/sysctl.h fstab.h \
sys/uio.h\
stddef.h stdlib.h string.h \
'.split():
		cfg.check_cc(header_name=x, mandatory=False)
	
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
