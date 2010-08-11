#!/usr/bin/env python
# encoding: utf-8
from waflib.Configure import conf
from waflib.Errors import ConfigurationError
from .defaults import INCLUDES_DEFAULT

__all__ = ['compute_int']

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
def try_to_compile(self, kw):
        #self.check_cc(**kw)
        #print ('kw=\n%s' %  kw)
        self.validate_c(kw)
        #print ('kw=\n%s' %  kw)
        self.run_c_code(**kw)
@conf
def confirm(self, e, val, **kw):
        kw.update({'fragment': kw.get('headers', INCLUDES_DEFAULT) + COMPUTE_INT_CODE % ('%s == %s' % (e, val))})
        self.try_to_compile(kw)
        if 'define_name' in kw:
                if 'define_ret' in kw and kw['define_ret']:
                        if 'quote' in kw and kw['quote']:
                                self.define(kw['define_name'], str(lo))
                        else:
                                self.define(kw['define_name'], lo)
                else:
                        self.define(kw['define_name'], 1)
        self.end_msg(str(val))
        return val

@conf
def compute_int(self, e, lo=-1, hi=1024, guess=None, **kw):
	if 'msg' not in kw:
		kw['msg'] = 'Checking for value of ' + e
	if 'errmsg' not in kw:
		kw['errmsg'] = 'Unknown'
	self.start_msg(kw['msg'])
	
	if guess != None:
		try:
                        return self.confirm(e, guess, **kw)
		except:
			pass
		if guess > 0:
			ghi = 2 * guess
			glo = guess//2
		elif guess < 0:
			ghi = guess//2
			glo = guess * 2
		else:
			ghi = 8 #an arbitrary choice
			glo = -8

		try:
			kw.update({'fragment': kw.get('headers', INCLUDES_DEFAULT) + COMPUTE_INT_CODE % ('%s >= %s' % (e, glo))})
			self.try_to_compile(kw)
		except:
			pass
		else:
			if glo > lo:
				lo = glo
		
		try:
			kw.update({'fragment': kw.get('headers', INCLUDES_DEFAULT) + COMPUTE_INT_CODE % ('%s <= %s' % (e, ghi))})
			self.try_to_compile(kw)
		except:
			pass
		else:
			if ghi < hi:
				hi = ghi

	while lo < hi:
		cur = (lo + hi)//2
		#print ('lo = %d, hi = %d, cur = %d' % (lo, hi, cur))
		if cur == lo:
			break
		try:
			#print ('compiling (%s)' %  cur)
			kw.update({'fragment': kw.get('headers', INCLUDES_DEFAULT) + COMPUTE_INT_CODE % ('%s >= %s' % (e, cur))})
			self.try_to_compile(kw)
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
		return self.confirm(e, lo, **kw)
	except:
		if 'define_name' in kw:
			self.undefine(kw['define_name'])
		self.end_msg(kw['errmsg'], 'YELLOW')
		if 'mandatory' not in kw or kw['mandatory']:
			self.fatal("can't compute '%s'" % e) 
