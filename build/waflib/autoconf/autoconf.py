#!/usr/bin/env python
# encoding: utf-8

import re, sys
from waflib.Context import STDOUT, STDERR
from waflib.Configure import conf, ConfigurationError
from waflib.TaskGen import feature, before
from waflib import Utils
from defaults import INCLUDES_DEFAULT

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

STRUCT_MEMBER_CODE='''
int
main()
{
static struct %s ac_aggr;
if (ac_aggr.%s)
  return 0;
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
def check_member(self, m, **kw):
	self.start_msg('Checking for struct member ' + m)
	dot = m.find('.')
	kw['fragment'] = kw.get('headers', INCLUDES_DEFAULT) + STRUCT_MEMBER_CODE % (m[:dot], m[dot + 1:])
	kw['define_name'] = 'HAVE_STRUCT_' + m.replace('.', '_').upper()
	self.validate_c(kw)
	ret = None
	try:
		ret = self.run_c_code(**kw)
	except:
		self.undefine(kw['define_name'])
		self.end_msg('None', 'YELLOW')
		raise
		if 'mandatory' not in kw or kw['mandatory']:
			self.fatal(t + "doesn't exist") 
	else:
		kw['success'] = ret
		self.end_msg('yes')
		self.post_check(**kw)

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
def check_const(self):
	try:
		self.check_cc(fragment='int main() {const int a=1; return 0;}', msg='Checking whether compiler supports const', errmsg='No', define_name='HAVE_CONST')
	except:
		self.undefine('HAVE_CONST')
