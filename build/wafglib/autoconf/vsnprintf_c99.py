#!/usr/bin/env python
# encoding: utf-8

from waflib.Errors import ConfigurationError
from waflib.Configure import conf

__all__ = ['check_vsnprintf_c99']

VSNPRINTF_C99_CODE='''
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

int
doit(char * s, ...)
{
  char buffer[32];
  va_list args;
  int r;

  va_start(args, s);
  r = vsnprintf(buffer, 5, s, args);
  va_end(args);

  if (r != 7)
    return 1;

  /* AIX 5.1 and Solaris seems to have a half-baked vsnprintf()
     implementation. The above will return 7 but if you replace
     the size of the buffer with 0, it borks! */
  va_start(args, s);
  r = vsnprintf(buffer, 0, s, args);
  va_end(args);

  if (r != 7)
    return 1;

  return 0;
}

int
main(void)
{
  return doit("1234567");
}
'''

@conf
def check_vsnprintf_c99(self, **kw):
	if getattr(self.env, 'cross_compile', False):
		raise self.fatal('cross_compiling, no vsnprintf_c99')
	kw.update({'fragment':VSNPRINTF_C99_CODE, 'msg':'Checking for C99 vsnprintf', 'execute':True, 'define_name':'HAVE_C99_VSNPRINTF'})
	try:
		self.check_cc(**kw)
	except ConfigurationError:
		#self.undefine('HAVE_C99_VSNPRINTF')
		raise
