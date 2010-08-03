#!/usr/bin/env python
# encoding: utf-8

from waflib.Configure import conf, ConfigurationError

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
