#!/usr/bin/python
import sys

dependency = {'cprogram':[['c']], 
	      'cxxprogram':[['cxx']], 
	      'cxxshlib':[['cxx']], 
	      'cxx':[['c'], ['d']],
	      'cshlib':[['c'], ['vnum']],
	      'vnum':[['cshlib'], ['cxxshlib'], ['cstlib'], ['cxxstlib']]}
class d(object):
	def solve_dependency(self):
		def solved_one(self, f, extra, visited):
			'''check the dependency only for one feature'''
			if f in visited:
				cycle = '->'.join(visited) + '->' + f
				raise Exception('A cyclical dependency detected: ' + cycle)
			visited.add(f)
			dps = dependency.get(f, None)
			if not dps: 
				return (True, set())

			#dps must be a list of list, success if any of them statisfies the dependency
			#if we have only one dependency and it's missing, try to add
			for x in dps:
				extra2 = set() #for each optional dependency, we start a new extra set
				sat = True
				for y in x:
					if y not in self.features and y not in extra :
						print (y + " is missing on %r" % f)
						if len(dps) == 1:
							print ('trying to add %r' % x)
							extra2.add(y)
						else:
							sat = False
							break
				if not sat:
					continue
				r, e = solved_group(self, x, extra2, visited)
				if r:	
					print (e)
					return (True, extra | e)
			return (False, set())
			
		def solved_group(self, group, extra, visited, top=False):
			'''check if all dependencies in the group are resolvable
			use the same extra set for all element in the group
			'''
			ret = True
			for x in group:
				if top:
					visited = set()
				r, e = solved_one(self, x, extra, visited)
				if not r:
					print ("dependency can't be resolved for " + x)
					ret = False
					break
				else:
					extra.update(e)
			return (ret, extra)
		
		return solved_group(self, self.features, extra=set(),  visited=set(), top=True)

if __name__ == '__main__':
	c = d()
	c.features=sys.argv[1:]
	print ('dependency: %r' % dependency)
	print ('ret = %r' % (c.solve_dependency(),))
	print ('features = %r' % c.features)
