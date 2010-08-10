#!/usr/bin/env python
# encoding: utf-8

from waflib.Configure import conf
from waflib.Errors import ConfigurationError

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
