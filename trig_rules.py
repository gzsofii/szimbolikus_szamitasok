#import simplify
from simplify import *
#from measure import m

""" sin_rule = Rule(F('sin', AC0('*', E(separate_2, 'k'), Var('x', 'complex'))), #bal oldal (source)
                AC0('*', F('sin', AC0('*', Var('k', 'integer'), Var('x', 'complex'))), F('cos', AC0('*', Var('k', 'integer'), Var('x', 'complex')))), #jobb oldal (target)
                'trig') """
rules = []
inv_rules = []

tan_rule = Rule(F('tan', Var('x','complex')), # bal oldal
          A0('/', F('sin', Var('x','complex')), F('cos', Var('x','complex'))), # jobb oldal
          'trig')
rules.append(tan_rule)

tan_rule_inv = Rule(A0('/', F('sin', Var('x','complex')), F('cos', Var('x','complex'))),
          F('tan', Var('x','complex')),
          'trig')
inv_rules.append(tan_rule_inv)
        

cot_rule = Rule(F('cot', Var('x','complex')), # bal oldal
          A0('/', F('cos', Var('x','complex')), F('sin', Var('x','complex'))), # jobb oldal
          'trig')
rules.append(cot_rule)

cot_rule_inv = Rule(A0('/', F('cos', Var('x','complex')), F('sin', Var('x','complex'))),
           F('cot', Var('x','complex')), 
          'trig')
inv_rules.append(cot_rule_inv)


sin_1 = Rule(F('sin', AC0('+', Var('x','complex'), Var('y', 'complex'))), 
        AC0('+', AC1('*', F('sin', Var('x','complex')), F('cos', Var('y','complex'))), AC1('*', F('cos', Var('x','complex')), F('sin', Var('y','complex')))),
        'trig')    
rules.append(sin_1)        

sin_1_inv = Rule(AC0('+', AC1('*', F('sin', Var('x','complex')), F('cos', Var('y','complex'))), AC1('*', F('cos', Var('x','complex')), F('sin', Var('y','complex')))),
        F('sin', AC0('+', Var('x','complex'), Var('y', 'complex'))), 
        'trig')    
inv_rules.append(sin_1_inv) 


cos_1 = Rule(F('cos', AC0('+', Var('x','complex'), Var('y', 'complex'))), 
 AC0('-', AC1('*', F('cos', Var('x','complex')), F('cos', Var('y','complex'))), AC1('*', F('sin', Var('x','complex')), F('sin', Var('y','complex')))),
 'trig') 
rules.append(cos_1)      

cos_1_inv = Rule(AC0('-', AC1('*', F('cos', Var('x','complex')), F('cos', Var('y','complex'))), AC1('*', F('sin', Var('x','complex')), F('sin', Var('y','complex')))),
        F('cos', AC0('+', Var('x','complex'), Var('y', 'complex'))), 
        'trig') 
inv_rules.append(cos_1_inv)   


pyth_rule = Rule(AC0('+',F('power', F('sin', Var('x','complex')), 2), F('power', F('cos', Var('x','complex')), 2) ),
            1,
            'trig')
rules.append(pyth_rule)

pyth_rule_inv = Rule(1,
            AC0('+',F('power', F('sin', Var('x','complex')), 2), F('power', F('cos', Var('x','complex')), 2) ),
            'trig')
inv_rules.append(pyth_rule_inv)

rules = rules + inv_rules

""" expr = AC0('+',F('power', F('sin', 'x'), 2), F('power', F('cos','x'), 2) )

print("expr:", expr)
print("simplified:", simplify(expr, rules, [eval_tree], m)) """