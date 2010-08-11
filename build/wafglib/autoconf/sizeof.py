#!/usr/bin/env python
# encoding: utf-8
from waflib.Configure import conf
from waflib.Errors import ConfigurationError
from .defaults import INCLUDES_DEFAULT
from .compute_int import compute_int

__all__ = ['check_sizeof']

@conf
def check_sizeof(self, t, lo = 1, hi=17, **kw):
	if 'define_name' not in kw:
		kw['define_name'] = 'SIZEOF_' + t.upper().replace(' ', '_').replace('*', 'P')
	if self.options.cross_compile:
		return self.compute_sizeof(t, lo, hi, **kw)
	else:
		if 'guess' in kw:
			del kw['guess']
		kw.update({'fragment': kw.get('headers', INCLUDES_DEFAULT) + 'int main() {printf("%%d", sizeof(%s));return 0;}' % t, 
			   'execute':True, 
                           'errmsg':'Unknown', 
                           'define_name':kw['define_name'], 
                           'define_ret':True, 
                           'quote':False})
		self.validate_c(kw)
		self.start_msg('Checking for sizeof ' + t)
		ret = None
		try:
			ret = self.run_c_code(**kw)
		except:
			self.undefine(kw['define_name'])
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
	kw['msg'] = 'Checking for sizeof ' + t
        kw['define_ret'] = True
        kw['quote'] = False
	# The cast to long int works around a bug in the HP C Compiler
	# version HP92453-01 B.11.11.23709.GP, which incorrectly rejects
	# declarations like `int a3[[(sizeof (unsigned char)) >= 0]];'.
	# This bug is HP SR number 8606223364.
	return self.compute_int('(long int) sizeof(%s)' % t, lo, hi, **kw)
