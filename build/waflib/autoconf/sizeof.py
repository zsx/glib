#!/usr/bin/env python
# encoding: utf-8
from waflib.Configure import conf
from waflib.Errors import ConfigurationError
from defaults import INCLUDES_DEFAULT

COMPUTE_INT_CODE='''
int
main ()
{
	static int test_array [1 - 2 * !(%s)];
	test_array [0] = 0 ;
	return 0;
}
'''

@conf
def check_sizeof(self, t, lo = 1, hi=17, **kw):
	define_name = 'SIZEOF_' + t.upper().replace(' ', '_').replace('*', 'P')
	if self.options.cross_compile:
		return self.compute_sizeof(t, lo, hi, **kw)
	else:
		kw.update({'fragment': kw.get('headers', INCLUDES_DEFAULT) + 'int main() {printf("%%d", sizeof(%s));return 0;}' % t, 
			   'execute':True, 
                           'errmsg':'Unknown', 
                           'define_name':define_name, 
                           'define_ret':True, 
                           'quote':False})
		self.validate_c(kw)
		self.start_msg('Checking for sizeof ' + t)
		ret = None
		try:
			ret = self.run_c_code(**kw)
		except:
			self.undefine(define_name)
			self.end_msg('Unknown', 'YELLOW')
			raise
			if 'mandatory' not in kw or kw['mandatory']:
				self.fatal("can't determine size of " + t) 
		else:
			kw['success'] = ret
			self.end_msg(ret)
			self.post_check(**kw)
		return int(ret)

@conf
def compute_sizeof(self, t, lo=1, hi=17, **kw):
	def try_to_compile(kw):
		#self.check_cc(**kw)
		#print ('kw=\n%s' %  kw)
		self.validate_c(kw)
		#print ('kw=\n%s' %  kw)
		self.run_c_code(**kw)

	self.start_msg('Checking for sizeof ' + t)
	define_name = 'SIZEOF_' + t.upper().replace(' ', '_').replace('*', 'P')
	if lo > hi:
		self.undefine(define_name)
		self.end_msg('Unknown', 'YELLOW')
		self.fatal('lo(%d) must be smaller than hi(%d)' % (lo, hi))
	while lo < hi:
		cur = (lo + hi)//2
		#print ('lo = %d, hi = %d, cur = %d' % (lo, hi, cur))
		if cur == lo:
			break
		try:
			# The cast to long int works around a bug in the HP C Compiler
			# version HP92453-01 B.11.11.23709.GP, which incorrectly rejects
			# declarations like `int a3[[(sizeof (unsigned char)) >= 0]];'.
			# This bug is HP SR number 8606223364.
			#print ('compiling (%s)' %  cur)
			kw.update({'fragment': COMPUTE_INT_CODE % ('(long int) sizeof(%s) >= %s' % (t, cur))})
			try_to_compile(kw)
		except:
			#print ('cur(%d) is too high, set it as high' %  cur)
			hi = cur
			cur = (lo + hi)//2
		else:
			#print ('cur(%d) is too low, set it as lo' %  cur)
			lo = cur
	else:
		if lo > hi:
			self.undefine(define_name)
			self.end_msg('Unknown', 'YELLOW')
			self.fatal("Unexpected: lo (%d) > hi (%d)" % (lo, hi)) 
	#sizeof(t) should be 'lo', if it succeeded
	#try one more time to make sure
	try:
		kw.update({'fragment': kw.get('headers', INCLUDES_DEFAULT) + COMPUTE_INT_CODE % ('(long int) sizeof(%s) == %s' % (t, lo))})
		try_to_compile(kw)
	except:
		self.undefine(define_name)
		self.end_msg('Unknown', 'YELLOW')
		if 'mandatory' not in kw or kw['mandatory']:
			self.fatal("can't compute size of " + t) 
	else:
		self.define(define_name, lo)
		self.end_msg(str(lo))
		return lo
