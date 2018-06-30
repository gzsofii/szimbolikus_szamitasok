from simplify import *

pow_rules = []

# 1^x = 1
pow_1_a = Rule(F('^', 1, Var('x', 'complex'))),
				1,
				'pow')
pow_rules.append(pow_1_a)
# x^1 = x
pow_z_1 = Rule(F('^', Var('x', 'complex'), 1)),
				Var('x', 'complex'),
				'pow')
pow_rules.append(pow_z_1)
# x^0 = 1 ### x != 0
pow_z_0 = Rule(F('^', Var('x', 'complex_nonzero'), 0)),
				1,
				'pow')
pow_rules.append(pow_z_0)
# x^a * x^b = x^(a+b)
pow_add = Rule(AC0('*', F('^', Var('x', 'complex'), Var('a', 'complex')), F('^', Var('x', 'complex'), Var('b', 'complex'))),
				F('^', Var('x', 'complex'), AC0('+', Var('a', 'complex'), Var('b', 'complex'))),
				'pow')
pow_rules.append(pow_add)
# (xy)^a = x^a * y^a
pow_mul = Rule(F('^', AC0('*', Var('x', 'complex'), Var('y', 'complex')), Var('a', 'complex')),
				AC0('*', F('^', Var('x', 'complex'), Var('a', 'complex')), F('^', Var('y', 'complex'), Var('a', 'complex'))),
				'pow')
pow_rules.append(pow_mul)
# (x^a)^b = x^(ab)
pow_pow = Rule(F('^', Var('x', 'complex'), F('^', Var('a', 'complex'), Var('b', 'complex'))),
				F('^', Var('x', 'complex'), AC0('*', Var('a', 'complex'), Var('b', 'complex'))),
				'pow')
pow_rules.append(pow_pow)
