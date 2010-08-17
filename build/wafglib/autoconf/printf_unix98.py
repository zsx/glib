#!/usr/bin/env python
# encoding: utf-8

from waflib.Errors import ConfigurationError
from waflib.Configure import conf

__all__ = ['check_printf_unix98']

PRINTF_UNIX98_CODE='''
#include <stdio.h>

int
main (void)
{
  char buffer[128];

  sprintf (buffer, "%2\$d %3\$d %1\$d", 1, 2, 3);
  if (strcmp ("2 3 1", buffer) == 0)
    exit (0);
  exit (1);
}
'''

@conf
def check_printf_unix98(self, **kw):
	if getattr(self.env, 'cross_compile', False):
		raise self.fatal('cross_compiling, no printf_unix98')
	kw.update({'fragment':PRINTF_UNIX98_CODE, 'msg':'checking whether printf supports positional parameters', 'define_name':'HAVE_UNIX98_PRINTF'})
	try:
		self.check_cc(**kw)
	except ConfigurationError:
		self.undefine('HAVE_UNIX98_PRINTF')
		raise
