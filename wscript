#!/usr/bin/env python
# encoding: utf-8

top = '.'
out = 'debug'

import re, sys, os
from waflib.Context import STDOUT, STDERR
from waflib.Configure import conf, ConfigurationError
from waflib.TaskGen import feature, before
from waflib import Utils
#from build.waflib import *
sys.path.insert(0, 'build')
#sys.path.insert(0, 'build')
if sys.version_info[0] < 3 and sys.version_info[1] < 5: #relative import for python older than 2.5
	#FIXME: Untested
	import __builtin__

	bimport = __builtin__.__import__
	dots = re.compile(r'^(\.+)(.*)')
	def import2(name, globals={}, locals={}, fromlist=[], level=-1):
		mo = dots.match(name) #relative import
		if mo:
			name = mo.group(2)
			if len(mo.group(1)) > 1:
				level = len(mo.group(1)) - 1
		return bimport(name, globals, locals, fromlist, level)
	__builtin__.__import__ = import2

from wafglib import *

if sys.version_info[0] < 3 and sys.version_info[1] < 5: #relative import for python older than 2.5
	__builtin__.__import__ = bimport

glib_major_version = 2
glib_minor_version = 25
glib_micro_version = 12
#the following to variables are required
VERSION = '%d.%d.%d.' % (glib_major_version, glib_minor_version, glib_micro_version)
APPNAME = 'glib'

GMEM_CODE='''
#include <stdlib.h>
int
main()
{
    void* (*my_calloc_p)  (size_t, size_t) = calloc;
    void* (*my_malloc_p)  (size_t)         = malloc;
    void  (*my_free_p)    (void*)          = free;
    void* (*my_realloc_p) (void*, size_t)  = realloc;
    my_calloc_p = 0;
    my_malloc_p = 0;
    my_free_p = 0;
    my_realloc_p = 0;
    return 0;
}
'''
STACK_GROWS_CODE='''
volatile int *a = 0, *b = 0;
void foo (void);
int main () { volatile int y = 7; a = &y; foo (); return b > a; }
void foo (void) { volatile int x = 5; b = &x; }
'''

G_CAN_INLINE_CODE='''
#if defined (G_HAVE_INLINE) && defined (__GNUC__) && defined (__STRICT_ANSI__)
#  undef inline
#  define inline __inline__
#elif !defined (G_HAVE_INLINE)
#  undef inline
#  if defined (G_HAVE___INLINE__)
#    define inline __inline__
#  elif defined (G_HAVE___INLINE)
#    define inline __inline
#  endif
#endif

int glib_test_func2 (int);

static inline int
glib_test_func1 (void) {
  return glib_test_func2 (1);
}

int
main (void) {
  int i = 1;
}
'''

INCLUDE_STAT='''
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#ifdef HAVE_SYS_STATFS_H
#include <sys/statfs.h>
#endif
#ifdef HAVE_SYS_PARAM_H
#include <sys/param.h>
#endif
#ifdef HAVE_SYS_MOUNT_H
#include <sys/mount.h>
#endif
'''

SIZE_T_CODE='''#if defined(_AIX) && !defined(__GNUC__)
#pragma options langlvl=stdc89
#endif
#include <stddef.h>
int main ()
{
  size_t s = 1;
  unsigned %s *size_int = &s;
  return (int)*size_int;
}'''

RES_QUERY_CODE='''
#include <sys/types.h>
#include <netinet/in.h>
#include <arpa/nameser.h>
#include <resolv.h>

int
main ()
{
	res_query("test", 0, 0, (void *)0, 0);
	return 0;
}
'''

@conf
def check_funcs(self, funcs, **kw):
	for x in Utils.to_list(funcs):
		self.check_cc(function_name = x, fragment='int %s();\n int main(){void *p = (void*)%s; return 0;}' % (x, x), **kw)

@conf
def check_funcs_can_fail(self, funcs, **kw):
	kw['mandatory'] = False
	for x in Utils.to_list(funcs):
		self.check_cc(function_name = x, fragment='int %s();\n int main(){void *p = (void*)%s; return 0;}' % (x, x), **kw)

@conf
def check_headers_can_fail(self, headers, **kw):
	kw['mandatory'] = False
	for x in Utils.to_list(headers):
		self.check_header(x, **kw)

def options(opt):
	glib_debug_default = 'minimum' 
	if glib_minor_version % 2:
		 glib_debug_default = 'yes'
	cfg = opt.parser.get_option_group('--prefix')
	bld = opt.parser.get_option_group('-p')

	cfg.add_option('--host', action='store', default=None, help='cross-compile to build programs to run on HOST')
	cfg.add_option('--build', action='store', default=None, help=' configure for building on BUILD')
	bld.add_option('--debug', action='store', default=glib_debug_default, dest='debug', metavar='yes/no/minimum', help='turn on debugging [default: %s]' % glib_debug_default)
	#bld.add_option('--cross-compile', action='store_true', default=False, dest='cross_compile', help='cross compile')
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
	try:
		cfg.check_cc(fragment='int main(){return 0;}', execute=True, msg='checking whether cross-compiling', okmsg='no', errmsg='yes')
		cfg.env.cross_compile=False
	except:
		cfg.env.cross_compile=True
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
	try:
		cfg.check_cc(fragment='#include <math.h>\nint main (void) {return (log(1) != log(1.));}', msg='checking for extra flags for ansi library types', okmsg='None')
	except ConfigurationError:
		try:
			cfg.check_cc(fragment='#include <math.h>\nint main (void) {return (log(1) != log(1.));}', lib='m', msg='checking for extra flags for ansi library types', okmsg='None', uselib_store='ANSI')
		except ConfigurationError:
			cfg.check_cc(fragment='#include <math.h>\nint main (void) {return (log(1) != log(1.));}', lib='m', ccflags='-std1', msg='checking for -std1 for ansi library types', okmsg='-std1', errmsg="No ANSI protypes found in library (-std1 didn't work)", uselib_store='ANSI', mandatory=False)

	# NeXTStep cc seems to need this
	try:
		cfg.check_cc(fragment='#include <dirent.h>\nint main (void) {DIR *dir;\nreturn 0;}', msg='checking for extra flags for posix compliance', okmsg='None', uselib_store='POSIX')
	except ConfigurationError:
		cfg.check_cc(fragment='#include <dirent.h>\nint main (void) {DIR *dir;\nreturn 0;}', ccflags='-posix', msg='checking for -posix for posix compliance', errmsg="Could not determine POSIX flag (-posix didn't work)", uselib_store='POSIX', mandatory=False)
	
	cfg.check_cc(function_name='vprintf', header_name=['stdarg.h', 'stdio.h'])
	cfg.check_alloca()
	cfg.check_stdc_headers()

	if cfg.options.iconv_cache == None and cfg.get_dest_binfmt() != 'pe' and not cfg.is_gnu_library_2_1():
		cfg.options.iconv_cache = True
	cfg.define_cond('NEED_ICONV_CACHE', cfg.options.iconv_cache)
	
	try:
		cfg.check_cfg(package='zlib')
	except :
		cfg.check_cc(function_name='inflate', lib='z', header_name='zlib.h', uselib_store='ZLIB')

	cfg.define_cond('DISABLE_MEM_POOLS', not cfg.options.mem_pools)
	cfg.define_cond('ENABLE_GC_FRIENDLY_DEFAULT', cfg.options.gc_friendly)
	cfg.check_header(['Carbon/Carbon.h', 'CoreServices/CoreServices.h'], define_name='HAVE_CARBON', uselib_store='CARBON', mandatory=False)
	for x in 'dirent.h float.h limits.h pwd.h grp.h sys/param.h sys/poll.h sys/resource.h \
	sys/time.h sys/times.h sys/wait.h unistd.h values.h \
	sys/select.h sys/types.h stdint.h inttypes.h sched.h malloc.h \
	sys/vfs.h sys/mount.h sys/vmount.h sys/statfs.h sys/statvfs.h \
	mntent.h sys/mnttab.h sys/vfstab.h sys/mntctl.h sys/sysctl.h fstab.h \
	sys/uio.h \
	stddef.h stdlib.h string.h \
	sys/stat.h \
	'.split():
		cfg.check_header(x, mandatory=False)
		'''
		cfg.check_cc(header_name=x, mandatory=False)
		'''
	cfg.check_funcs_can_fail('mmap posix_memalign memalign valloc fsync pipe2')
	cfg.check_funcs_can_fail('atexit on_exit timegm gmtime_r')
	cfg.check_const()
	cfg.check_cc(fragment=GMEM_CODE, define_name='SANE_MALLOC_PROTOS', msg='Checking whether malloc() and friends prototypes are gmem.h compatible', errmsg='No', mandatory=False)
	try:
		cfg.check_cc(fragment=STACK_GROWS_CODE, msg='Checking for growing stack pointer', errmsg='No', execute=True)
	except:
		glib_stack_grows=False
	else:
		glib_stack_grows=True
	
	for i in ('__inline', '__inline__', 'inline'):
		cfg.check_cc(fragment='%s int foo(){return 0;}\nint main(){return foo();}' % i, msg='Checking for ' + i, errmsg='No', define_name='G_HAVE_' + i.upper(), mandatory=False)
	cfg.check_cc(fragment=G_CAN_INLINE_CODE, msg='Checking whether inline functions in headers work', errmsg='No')
	cfg.check_cc(fragment='''
		#define STMT_START do
		#define STMT_END while(0)
		#define STMT_TEST STMT_START { i = 0; } STMT_END
		int main(void) { int i = 1; STMT_TEST; return i; }''',
		msg='Checking for do while(0) macros', define_name='HAVE_DOWHILE_MACROS')

	size_length = {}
	for x in ('char', 'short', 'int', 'long', 'void *', 'long long', '__int64'):
		size_length[x] = cfg.check_sizeof(x, mandatory = False)

	for x in 'stat.st_mtimensec stat.st_mtim.tv_nsec stat.st_atimensec stat.st_atim.tv_nsec stat.st_ctimensec stat.st_ctim.tv_nsec'.split(' '):
		cfg.check_member(x, mandatory = False)
	for x in 'stat.st_blksize stat.st_blocks statfs.f_fstypename statfs.f_bavail'.split():
		cfg.check_member(x, headers = INCLUDE_STAT, mandatory = False)
	
	try:
		cfg.check_cc(fragment='#include <langinfo.h>\nint main () { char* cs = nl_langinfo(CODESET); return 0; }', define_name='HAVE_LANGINFO_CODESET', msg='checking for nl_langinfo and CODESET')
	except ConfigurationError:
		cfg.undefine('HAVE_LANGINFO_CODESET')
	try:
		cfg.check_funcs('setlocale')
	except ConfigurationError:
		cfg.undefine('HAVE_SETLOCALE')
	
	cfg.start_msg('checking for appropriate definition for size_t')
	size_t = cfg.check_sizeof('size_t')
	glib_size_type = None
	for t in ('short', 'int', 'long', 'long long', '__int64'): 
		if size_length[t] == size_t:
			glib_size_type = t
			break
	if glib_size_type == None:
		cfg.fatal('No type matching size_t in size')

	# If int/long are the same size, we see which one produces
	# warnings when used in the location as size_t. (This matters
	# on AIX with xlc)
	if size_length['int'] == size_length['long'] and glib_size_type == 'int':
		try:
			cfg.check_cc(fragment=SIZE_T_CODE % 'int')
			glib_size_type = 'int'
		except ConfigurationError:
			cfg.check_cc(fragment=SIZE_T_CODE % 'long')
			glib_size_type = 'long'
	cfg.end_msg(glib_size_type)

	# Check for some functions
	cfg.check_funcs_can_fail('lstat strerror strsignal memmove vsnprintf stpcpy strcasecmp strncasecmp poll getcwd vasprintf setenv unsetenv getc_unlocked readlink symlink fdwalk memmem')
	cfg.check_funcs_can_fail('chown lchmod lchown fchmod fchown link statvfs statfs utimes getgrgid getpwuid')
	cfg.check_funcs_can_fail('getmntent_r setmntent endmntent hasmntopt getmntinfo')
	# Check for high-resolution sleep functions
	cfg.check_funcs_can_fail('nanosleep nsleep')
	cfg.check_funcs_can_fail('splice')
	cfg.check_header('crt_externs.h', mandatory=False)
	cfg.check_funcs_can_fail('_NSGetEnviron')
	if cfg.get_dest_binfmt() == 'pe':
		glib_inet_includes = "#include <winsock2.h>"
	else:
		glib_inet_includes="#include <sys/types.h>\n#include <sys/socket.h>"
	cfg.compute_int('AF_INET', headers=glib_inet_includes, guess=2)
	cfg.compute_int('AF_INET6', headers=glib_inet_includes, guess=10)
	# winsock defines this even though it doesn't support it
	cfg.compute_int('AF_UNIX', headers=glib_inet_includes, guess=1)

	cfg.compute_int('MSG_PEEK', headers=glib_inet_includes, guess=2)
	cfg.compute_int('MSG_OOB', headers=glib_inet_includes, guess=1)
	cfg.compute_int('MSG_DONTROUTE', headers=glib_inet_includes, guess=4)
	cfg.check_funcs_can_fail('getprotobyname_r endservent')
	cfg.check_headers_can_fail('netdb.h wspiapi.h')
	
	#Non win32 native
	cfg.check_funcs_can_fail('strndup setresuid setreuid')
	cfg.check_headers_can_fail('sys/prctl.h arpa/nameser_compat.h')
	
	try:
		cfg.check_cc(fragment=RES_QUERY_CODE, uselib_store='ASYNCS_LIBADD', msg='checking for res_query')
	except ConfigurationError:
		try:
			cfg.check_cc(fragment=RES_QUERY_CODE, lib='resolv', uselib_store='ASYNCS_LIBADD', msg='checking res_query in resolv')
		except ConfigurationError:
			cfg.check_cc(fragment=RES_QUERY_CODE, lib='bind', uselib_store='ASYNCS_LIBADD', msg='checking res_query in bind')

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
