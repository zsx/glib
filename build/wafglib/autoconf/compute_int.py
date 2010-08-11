#!/usr/bin/env python
# encoding: utf-8
from waflib.Configure import conf
from waflib.Errors import ConfigurationError
from .defaults import INCLUDES_DEFAULT

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
def compute_int(self, e, lo=-1, hi=1024, **kw):
	def try_to_compile(kw):
		#self.check_cc(**kw)
		#print ('kw=\n%s' %  kw)
		self.validate_c(kw)
		#print ('kw=\n%s' %  kw)
		self.run_c_code(**kw)

	if 'msg' not in kw:
		kw['msg'] = 'Checking for value of ' + e
	if 'errmsg' not in kw:
		kw['errmsg'] = 'Unknown'
	self.start_msg(kw['msg'])
	while lo < hi:
		cur = (lo + hi)//2
		#print ('lo = %d, hi = %d, cur = %d' % (lo, hi, cur))
		if cur == lo:
			break
		try:
			#print ('compiling (%s)' %  cur)
			kw.update({'fragment': kw.get('headers', INCLUDES_DEFAULT) + COMPUTE_INT_CODE % ('%s >= %s' % (e, cur))})
			try_to_compile(kw)
		except:
			#print ('cur(%d) is too high, set it as high' %  cur)
			hi = cur
			cur = (lo + hi)//2
		else:
			#print ('cur(%d) is too low, set it as lo' %  cur)
			lo = cur
	#e should be 'lo', if it succeeded
	#try one more time to make sure
	try:
		kw.update({'fragment': kw.get('headers', INCLUDES_DEFAULT) + COMPUTE_INT_CODE % ('%s == %s' % (e, lo))})
		try_to_compile(kw)
	except:
		if 'define_name' in kw:
			self.undefine(kw['define_name'])
		self.end_msg(kw['errmsg'], 'YELLOW')
		if 'mandatory' not in kw or kw['mandatory']:
			self.fatal("can't compute '%s'" % e) 
	else:
		if 'define_name' in kw:
			if 'define_ret' in kw and kw['define_ret']:
				if 'quote' in kw and kw['quote']:
					self.define(kw['define_name'], '"%d"' % lo)
				else:
					self.define(kw['define_name'], lo)
			else:
				self.define(kw['define_name'], 1)
		self.end_msg(str(lo))
		return lo
