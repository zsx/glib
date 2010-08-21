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
STATFS_CODE='''
#include <unistd.h>
#ifdef HAVE_SYS_PARAM_H
#include <sys/param.h>
#endif
#ifdef HAVE_SYS_VFS_H
#include <sys/vfs.h>
#endif
#ifdef HAVE_SYS_MOUNT_H
#include <sys/mount.h>
#endif
#ifdef HAVE_SYS_STATFS_H
#include <sys/statfs.h>
#endif

int main()
{
	struct statfs st;
	%s
	return 0;
}
'''

LONG_LONG_FORMAT_CODE='''
#include <stdlib.h>
#include <stdio.h>
int main()
{
  long long b, a = -0x3AFAFAFAFAFAFAFALL;
  char buffer[1000];
  sprintf (buffer, "%%%su", a);
  sscanf (buffer, "%%%su", &b);
  exit (b!=a);
}
'''


@conf
def check_libiconv(self, iconv):
	if iconv == 'maybe':
		found_iconv = False
		if self.check_cc(function_name='iconv_open', header_name='iconv.h', msg = 'Checking for iconv_open in C library', mandatory=False, uselib_store='ICONV'):
			found_iconv = True
		elif self.check_cc(function_name='libiconv_open', header_name='iconv.h', lib='iconv', msg='Checking for libiconv_open in GNU libiconv', mandatory=False, defines=['USE_LIBICONV_GNU'], uselib_store='ICONV'):
			found_iconv = True
		elif self.check_cc(function_name='iconv_open', header_name='iconv.h', lib='iconv', msg='Checking for iconv_open in the system library iconv', mandatory=False, defines='USE_LIBICONV_NATIVE', uselib_store='ICONV'):
			found_iconv = True
		if not found_iconv:
			self.fatal('No iconv() implementation found in C library or libiconv')
	elif iconv == 'no':
		self.check_cc(function_name='iconv_open', header_name='iconv.h', msg = 'Checking for iconv_open in C library', uselib_store='ICONV')
	elif iconv in ('yes', 'gnu'):
		self.check_cc(function_name='libiconv_open', header_name='iconv.h', lib='iconv', msg='Checking for libiconv_open in GNU libiconv', defines=['USE_LIBICONV_GNU'], uselib_store='ICONV')
	elif iconv == 'native':
		self.check_cc(function_name='iconv_open', header_name='iconv.h', lib='iconv', msg='Checking for iconv_open in the system library iconv', defines='USE_LIBICONV_NATIVE', uselib_store='ICONV')
	else:
		self.fatal('Unknown parameter to --with-libiconv')

@conf
def is_gnu_library_2_1(self):
	try:
		self.check_cc(fragment=GNU_2_1_CODE, msg="Checking whether glibc 2.1", errmsg='No')
	except ConfigurationError:
		return False
	else:	
		return True

@conf
def check_statfs_args(self, **kw):
	self.start_msg('Checking for number of arguments to statfs()')
	kw.update({'fragment': STATFS_CODE % 'statfs(NULL, &st);'})
	self.validate_c(kw)
	try:
		self.run_c_code(**kw)
		self.define('STATFS_ARGS', 2)
		self.end_msg('2')
	except:
		try:
			kw.update({'fragment': STATFS_CODE % 'statfs(NULL, &st, sizeof(st), 0);'})
			self.run_c_code(**kw)
			self.define('STATFS_ARGS', 4)
			self.end_msg('4')
		except:	
			self.undefine('STATFS_ARGS')
			self.end_msg('Error', 'YELLOW')
			self.fatal('unable to determine number of arguments to statfs()')

@conf
def check_long_long_format(self, **kw):
	if getattr(self.env, 'cross_compile', False):
		raise self.fatal("cross_compiling, can't determine long long format")
	self.start_msg('Checking for format to pritnf and scanf a guint64')
	fmt = None
	for x in ('ll', 'I64'):
		kw.update({'fragment': LONG_LONG_FORMAT_CODE % (x, x), 'execute':True})
		self.validate_c(kw)
		try:
			self.run_c_code(**kw)
			fmt = x
			break
		except:
			pass

	if not fmt:
		self.define('HAVE_LONG_LONG_FORMAT', 1)
	else:
		self.undefine('HAVE_LONG_LONG_FORMAT')
		self.undefine('HAVE_INT64_AND_I64')

	if fmt == 'I64':
		self.define('HAVE_INT64_AND_I64', 1)

	self.end_msg(fmt)
	return fmt
	
