from simplify import *
from rules import add_rule

pow_rules = []
"""
# 1^x = 1
add_rule(pow_rules,
	F('^', 1, Var('x', 'complex')),
	1,
	'pow', 'oneway')
# x^1 = x
add_rule(pow_rules,
	F('^', Var('x', 'complex'), 1),
	Var('x', 'complex'),
	'pow', 'oneway')
# x^0 = 1 ### x != 0
add_rule(pow_rules,
	F('^', Var('x', 'complex_nonzero'), 0),
	1,
	'pow', 'oneway')
# x^a * x^b = x^(a+b)
add_rule(pow_rules,
	AC0('*', F('^', Var('x', 'complex'), Var('a', 'complex')), F('^', Var('x', 'complex'), Var('b', 'complex'))),
	F('^', Var('x', 'complex'), AC0('+', Var('a', 'complex'), Var('b', 'complex'))),
	'pow')
"""
# (xy)^a = x^a * y^a
add_rule(pow_rules,
	F('^', AC0('*', Var('x', 'complex'), Var('y', 'complex')), Var('a', 'complex')),
	AC0('*', F('^', Var('x', 'complex'), Var('a', 'complex')), F('^', Var('y', 'complex'), Var('a', 'complex'))),
	'pow')
# (x^a)^b = x^(ab)
add_rule(pow_rules,
	F('^', F('^', Var('x', 'complex'), Var('a', 'complex')), Var('b', 'complex')),
	F('^', Var('x', 'complex'), AC0('*', Var('a', 'complex'), Var('b', 'complex'))),
	'pow')
