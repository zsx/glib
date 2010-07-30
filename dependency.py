#!/usr/bin/python
import sys

dependency = {'cprogram':[['c']], 
	      'cxxprogram':[['cxx']], 
	      'cxxshlib':[['cxx']], 
	      'cxx':[['c'], ['d']],
	      'vnum':[['cshlib'], ['cxxshlib'], ['cstlib'], ['cxxstlib']]}
class d(object):
	def solve_dependency(self):
		def solved_one(self, f):
			'''check only for one feature'''
			dps = dependency.get(f, None)
			if not dps: 
				return True

			#dps must be a list of list
			for x in dps:
				sat = True
				for y in x:
					if not y in self.features:
						print (y + " is missing, giving up on %r" % x)
						sat = False
						if len(x) == 1:
							print ('trying to add %r' % x)
							self.features.append(y)
						else:
							break
				if not sat:
					continue
				if solved_group(self, x):
					return True
			return False
			
			
		def solved_group(self, group):
			'''check if all dependencies in the group are solve'''
			ret = True
			for x in group:
				if not solved_one(self, x):
					print ("can't solve for " + x)
					ret = False
					break
			return ret
		
		return solved_group(self, self.features)

if __name__ == '__main__':
	c = d()
	c.features=sys.argv[1:]
	print ('dependency: %r' % dependency)
	print ('ret = %r' % c.solve_dependency())
