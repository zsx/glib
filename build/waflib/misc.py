#!/usr/bin/env python
# encoding: utf-8

from waflib.Context import STDOUT, STDERR
from waflib.Configure import conf
from waflib.Errors import ConfigurationError
from waflib.TaskGen import feature, before
from waflib import Utils

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
def is_gnu_library_2_1(self):
	try:
		self.check_cc(fragment=GNU_2_1_CODE, msg="checking whether glibc 2.1", errmsg='No')
	except ConfigurationError:
		return False
	else:	
		return True
