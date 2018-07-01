from simplify import *
from rules import add_rule

""" sin_rule = Rule(F('sin', AC0('*', E(separate_2, 'k'), Var('x', 'complex'))), #bal oldal (source)
                AC0('*', F('sin', AC0('*', Var('k', 'integer'), Var('x', 'complex'))), F('cos', AC0('*', Var('k', 'integer'), Var('x', 'complex')))), #jobb oldal (target)
                'trig') """
trig_rules = []

add_rule(trig_rules,
	F('tan', Var('x','complex')), # bal oldal
	A0('/', F('sin', Var('x','complex')), F('cos', Var('x','complex'))), # jobb oldal
	'trig')
 
add_rule(trig_rules,
	F('cot', Var('x','complex')), # bal oldal
	A0('/', F('cos', Var('x','complex')), F('sin', Var('x','complex'))), # jobb oldal
	'trig')

add_rule(trig_rules,
	F('sin', AC0('+', Var('x','complex'), Var('y', 'complex'))), 
	AC0('+', AC1('*', F('sin', Var('x','complex')), F('cos', Var('y','complex'))), AC1('*', F('cos', Var('x','complex')), F('sin', Var('y','complex')))),
	'trig')    

add_rule(trig_rules,
	F('cos', AC0('+', Var('x','complex'), Var('y', 'complex'))), 
	F('-', AC1('*', F('cos', Var('x','complex')), F('cos', Var('y','complex'))), AC1('*', F('sin', Var('x','complex')), F('sin', Var('y','complex')))),
	'trig') 

add_rule(trig_rules,
	AC0('+',F('^', F('sin', Var('x','complex')), 2), F('^', F('cos', Var('x','complex')), 2) ),
	1,
	'trig', 'oneway')


if __name__ == '__main__':
	print(trig_rules)