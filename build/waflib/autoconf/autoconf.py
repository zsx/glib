#!/usr/bin/env python
# encoding: utf-8

import re, sys
from waflib.Context import STDOUT, STDERR
from waflib.Configure import conf, ConfigurationError
from waflib.TaskGen import feature, before
from waflib import Utils
from autoconf.defaults import INCLUDES_DEFAULT

STRUCT_MEMBER_CODE='''
int
main()
{
static struct %s ac_aggr;
if (ac_aggr.%s)
  return 0;
}
'''

@conf
def check_cpp(self, **kw):
	'''
	preprocess code in kw['fragment']
	define kw['define_name'] if no exceptions
	'''
	if sys.platform == 'win32':
		nul = 'NUL'
	else:
		nul = '/dev/null'
	try:
		for x in ('rule', 'features', 'target'):
			if x in kw:
				del kw[x]
		self.check_cc(rule = '"${CC}" -E ${CPPFLAGS} ${SRC} >' + nul, target=[], features=[], **kw)
	except :
		if 'define_name' in kw:
			self.undefine(kw['define_name'])
		raise

@conf
def check_header(self, h, **kw):

	if isinstance(h, str):
		code = '#include <%s>' % h
	else:
		code = '\n'.join(map(lambda x: '#include <%s>' % x, h))

	if 'msg' not in kw:
		kw['msg'] = 'checking for %r' % h
	if 'errmsg' not in kw:
		kw['errmsg'] = 'not found'
	if 'define_name' not in kw:
		kw['define_name'] = 'HAVE_%s' % Utils.quote_define_name(h)
	self.check_cpp(fragment = code, **kw)

@conf
def check_member(self, m, **kw):
	self.start_msg('Checking for struct member ' + m)
	dot = m.find('.')
	kw['fragment'] = kw.get('headers', INCLUDES_DEFAULT) + STRUCT_MEMBER_CODE % (m[:dot], m[dot + 1:])
	kw['define_name'] = 'HAVE_STRUCT_' + m.replace('.', '_').upper()
	self.validate_c(kw)
	ret = None
	try:
		ret = self.run_c_code(**kw)
	except:
		self.undefine(kw['define_name'])
		self.end_msg('None', 'YELLOW')
		if 'mandatory' not in kw or kw['mandatory']:
			self.fatal(m[dot+1:] + " doesn't exist") 
	else:
		kw['success'] = ret
		self.end_msg('yes')
		self.post_check(**kw)

@conf
def check_const(self):
	try:
		self.check_cc(fragment='int main() {const int a=1; return 0;}', msg='Checking whether compiler supports const', errmsg='No', define_name='HAVE_CONST')
	except:
		self.undefine('HAVE_CONST')
