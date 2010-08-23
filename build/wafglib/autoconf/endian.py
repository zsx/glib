#!/usr/bin/env python
# encoding: utf-8

import sys
from waflib.Configure import conf
from waflib.Errors import ConfigurationError
from waflib.TaskGen import feature, before, after
from waflib import Utils
from waflib import Task

__all__ = ['check_endian']

BIGENDIAN_CODE_TEMPLATE='''
%s
#error bogus endian macros or non-big endian
#endif
int
main ()
{
	return 0;
}
'''

BIGENDIAN_GUESS_CODE='''
short int ascii_mm[] = { 0x4249, 0x4765, 0x6E44, 0x6961, 0x6E53, 0x7953, 0 };
short int ascii_ii[] = { 0x694C, 0x5454, 0x656C, 0x6E45, 0x6944, 0x6E61, 0 };
int use_ascii (int i) 
{ 
	return ascii_mm[i] + ascii_ii[i];
}
short int ebcdic_ii[] = { 0x89D3, 0xE3E3, 0x8593, 0x95C5, 0x89C4, 0x9581, 0 };
short int ebcdic_mm[] = { 0xC2C9, 0xC785, 0x95C4, 0x8981, 0x95E2, 0xA8E2, 0 };
int use_ebcdic (int i) 
{
	return ebcdic_mm[i] + ebcdic_ii[i];
}
extern int foo;

int
main ()
{
	return use_ascii (foo) == use_ebcdic (foo);
	return 0;
}
'''

class guess_endian_task(Task.Task):
	def run(self):
		dest = self.inputs[0]
		f = open(dest.abspath(), 'rb')
		content = f.read()
		content = filter(lambda x: x.isalpha(), content)
		f.close()
		content = content.decode()
		bld = self.generator.bld
		if content.find('BIGenDianSyS') >= 0:
			bld.retval = 'big'
		if content.find('LiTTleEnDian') >= 0:
			if getattr(bld, 'retval', None):
				# finding both strings is unlikely to happen, but who knows?
				bld.fatal('Unable to determine the byte order\n%s'% Utils.ex_stack())
			else:
				bld.retval = 'little'
		if not hasattr(bld, 'retval') or bld.retval not in ('big', 'little'):
			bld.fatal('Unable to determine the byte order\n%s'% Utils.ex_stack())

@feature('bigendian')
@after('process_source')
def guess_bigendian(self):
	self.create_task('guess_endian', self.compiled_tasks[0].outputs)

@conf
def check_endian(self, **kw):
	def big():
		self.define('WORDS_BIGENDIAN', 1)
		self.end_msg('big')
		return 'big'
	def little():
		self.undefine('WORDS_BIGENDIAN')
		self.end_msg('little')
		return 'little'
	def guess():
		# Try to guess by grepping values from an object file.
		kw.update({'fragment': BIGENDIAN_GUESS_CODE, 
			   'compiler': 'c',
			   'features': 'c bigendian'})
		self.validate_c(kw)
		byteorder = self.run_c_code(**kw)
		if byteorder == 'big':
			return big()
		else: #anything other than 'little' already raised an exception in feature bigendian, so we know it's little endian for sure
			return little()

	#entry	
	self.start_msg('Checking for byte ordering')
	if not getattr(self.env, 'cross_compile', False):
		if sys.byteorder == 'big':
			return big()
		elif sys.byteorder == 'little':
			return little()
		else:
			fatal('sys.byteorder = ' + sys.byteorder)
	#adepted from autoconf
	# See if sys/param.h defines the BYTE_ORDER macro.
	try:
		kw.update({'fragment': '#include <sys/types.h>\n#include <sys/param.h>\n' + BIGENDIAN_CODE_TEMPLATE % ('#if !(defined(BYTE_ORDER) && defined (BIG_ENDIAN) && defined (LITTLE_ENDIAN) && BYTE_ORDER && BIG_ENDIAN && LITTLE_ENDIAN)'), 'features': 'c'})
		self.validate_c(kw)
		self.run_c_code(**kw)
		try:
			# It does; now see whether it defined to BIG_ENDIAN or not.
			kw.update({'fragment': '#include <sys/types.h>\n#include <sys/param.h>\n' + BIGENDIAN_CODE_TEMPLATE % '#if BYTE_ORDER != BIG_ENDIAN', 'features': 'c'})
			self.validate_c(kw)
			self.run_c_code(**kw)
			return big()
		except ConfigurationError:
			try:
				kw.update({'fragment': '#include <sys/types.h>\n#include <sys/param.h>\n' + BIGENDIAN_CODE_TEMPLATE % '#if BYTE_ORDER != LITTLE_ENDIAN', 'features': 'c'})
				self.validate_c(kw)
				self.run_c_code(**kw)
				return little()
			except ConfigurationError:
				self.fatal('sys/param.h defined a weird byteorder: non big and non-little')
	except ConfigurationError:
		# See if <limits.h> defines _LITTLE_ENDIAN or _BIG_ENDIAN (e.g., Solaris).
		try:
			kw.update({'fragment': '#include <limits.h>\n' + BIGENDIAN_CODE_TEMPLATE % '#if ! (defined (_LITTLE_ENDIAN) || defined(_BIG_ENDIAN))', 'features': 'c'})
			self.validate_c(kw)
			self.run_c_code(**kw)
			# It does; now see whether it defined to _BIG_ENDIAN or not.
			try:
				kw.update({'fragment': '#include <limits.h>\n' + BIGENDIAN_CODE_TEMPLATE % 'if ! defined (_BIG_ENDIAN)', 'features': 'c'})
				self.validate_c(kw)
				self.run_c_code(**kw)
				return big()
			except ConfigurationError:
				try:
					kw.update({'fragment': '#include <limits.h>\n' + BIGENDIAN_CODE_TEMPLATE % 'if ! defined (_LITTLE_ENDIAN)', 'features': 'c'})
					self.validate_c(kw)
					self.run_c_code(**kw)
					return little()
				except ConfigurationError:
					self.fatal('limits.h defined a weird byteorder: non big and non-little')
		except ConfigurationError:
			# See if <endian.h> defines __BYTE_ORDER
			try:
				kw.update({'fragment': '#include <endian.h>\n' + BIGENDIAN_CODE_TEMPLATE % '#if ! (defined(__BYTE_ORDER) && defined (__BIG_ENDIAN) && defined (__LITTLE_ENDIAN))', 'features': 'c'})
				self.validate_c(kw)
				self.run_c_code(**kw)
				try:
					kw.update({'fragment': '#include <endian.h>\n' + BIGENDIAN_CODE_TEMPLATE % '#if __BYTE_ORDER != __BIG_ENDIAN', 'features': 'c'})
					self.validate_c(kw)
					self.run_c_code(**kw)
					return big()
				except ConfigurationError:
					try:
						kw.update({'fragment': '#include <endian.h>\n' + BIGENDIAN_CODE_TEMPLATE % '#if __BYTE_ORDER != __LITTLE_ENDIAN', 'features': 'c'})
						self.validate_c(kw)
						self.run_c_code(**kw)
						return little()
					except ConfigurationError:
						self.fatal('endian.h defined a weird byteorder: non big and non-little')
			except ConfigurationError:
				return guess()
