#!/usr/bin/env python
# encoding: utf-8
import re, sys
from waflib.Context import STDOUT, STDERR
from waflib.Configure import conf, ConfigurationError
from waflib.TaskGen import feature, before
from waflib import Utils

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
@conf
def check_cpp(self, **kw):
	'''
	preprocess code in kw['fragment']
	define kw['define_name'] if no exceptions
	'''
	if sys.platform == 'win32':
		nul = 'NUL'
	else:
		nul = '/dev/null'
	try:
		for x in ('rule', 'features', 'target'):
			if x in kw:
				del kw[x]
		self.check_cc(rule = '"${CC}" -E ${CPPFLAGS} ${SRC} >' + nul, target=[], features=[], **kw)
	except :
		if 'define_name' in kw:
			self.undefine(kw['define_name'])
		raise

@conf
def check_header(self, h, **kw):

	if isinstance(h, str):
		code = '#include <%s>' % h
	else:
		code = '\n'.join(map(lambda x: '#include <%s>' % x, h))

	if 'msg' not in kw:
		kw['msg'] = 'checking for %r' % h
	if 'errmsg' not in kw:
		kw['errmsg'] = 'not found'
	if 'define_name' not in kw:
		kw['define_name'] = 'HAVE_%s' % Utils.quote_define_name(h)
	self.check_cpp(fragment = code, **kw)
	

@conf
def check_stdc_headers(self):
	def test_stdc_headers(tk):
		def write_test_file(task):
			task.outputs[0].write(task.generator.code)

		def write_find_symbols(task):
			task.outputs[0].write(task.generator.code)
			bld = task.generator.bld
			if bld.env.CC_NAME == 'msvc':
				cpp = bld.env['CC'] + ['/E']
			else:
				cpp = bld.env['CC'] + ['-E']

			if bld.cmd_and_log(cpp + [task.outputs[0].abspath()], quiet=STDOUT).find(task.generator.symbol) < 0:
				bld.fatal("symbols %r is not found" % task.generator.symbol)

		bld = tk.generator.bld
		
		bld(rule=write_test_file, target='stdc_code.c', code=STDC_CODE1) 
		bld(rule=write_test_file, target='stdc_irix.c', code=STDC_IRIX_4_0_5)

		bld(features='cprogram', sources='stdc_code.c', target='test_stdc') 

		#SunOS 4.x string.h does not declare mem*, contrary to ANSI.
		bld(rule=write_find_symbols, target='stdc_sunos.c', code='#include <string.h>', symbol='memchr')

		#ISC 2.0.2 stdlib.h does not declare free, contrary to ANSI.
		bld(rule=write_find_symbols, target='stdc_isc.c', code='#include <stdlib.h>', symbol='free')

		bld(features='cprogram', sources='stdc_isc.c', target='test_isc')

	try:
		self.check(compile_filename=[],
			target = [],
			features = [],
			rule = test_stdc_headers,
			msg = 'Checking for ANSI header files',
			fragment='',
			define_name='STDC_HEADERS')
	except:
		self.undefine('STDC_HEADERS')
		raise

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

	try:
		self.check_cc(fragment=ALLOCA_CODE, msg='checking for alloca', define_name='HAVE_ALLOCA')
	except ConfigurationError:
		# The SVR3 libPW and SVR4 libucb both contain incompatible functions
		# that cause trouble.  Some versions do not even contain alloca or
		# contain a buggy version.  If you still want to use their alloca,
		# use ar to extract alloca.o from them instead of compiling alloca.c.
		# ALLOCA=\${LIBOBJDIR}alloca.$ac_objext
		#self.define('C_ALLOCA', 1)
		raise
	try:
		self.check_cpp(fragment='#if ! defined CRAY || defined CRAY2\n#error "Not CRAY"\n#endif\n', msg="checking whether 'alloca.c' needs Cray hooks", errmsg='No')
	except ConfigurationError:
		#Not Cray
		self.undefine('CRAY_STACKSEG_END')
	else:
		# FIXME, untested
		for func in ('_getb67', 'GETB67', 'getb67'):
			try:
				self.check_cc(function_name=func)
				self.define('CRAY_STACKSEG_END', func)
				break	
			except:
				pass
		else:
			self.fatal("None of _getb67, GETB67 or getb67 found on Cray")

@conf
def is_gnu_library_2_1(self):
	try:
		self.check_cc(fragment=GNU_2_1_CODE, msg="checking whether glibc 2.1", errmsg='No')
	except ConfigurationError:
		return False
	else:	
		return True
@conf
def check_const(self):
	try:
		self.check_cc(fragment='int main() {const int a=1; return 0;}', msg='Checking whether compiler supports const', errmsg='No', define_name='HAVE_CONST')
	except:
		self.undefine('HAVE_CONST')
	
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
	cfg.check_allca()
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
	'.split():
		cfg.check_header(x, mandatory=False)
		'''
		cfg.check_cc(header_name=x, mandatory=False)
		'''
	for x in 'mmap posix_memalign memalign valloc fsync pipe2 \
	atexit on_exit timegm gmtime_r \
	'.split():
		cfg.check_cc(function_name = x, fragment='int %s();\n int main(){void *p = (void*)%s; return 0;}' % (x, x), mandatory=False)
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
