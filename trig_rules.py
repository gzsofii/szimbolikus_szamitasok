#import simplify
from simplify import *
#from measure import m

""" sin_rule = Rule(F('sin', AC0('*', E(separate_2, 'k'), Var('x', 'complex'))), #bal oldal (source)
                AC0('*', F('sin', AC0('*', Var('k', 'integer'), Var('x', 'complex'))), F('cos', AC0('*', Var('k', 'integer'), Var('x', 'complex')))), #jobb oldal (target)
                'trig') """
trig_rules = []

tan_rule = Rule(F('tan', Var('x','complex')), # bal oldal
          A0('/', F('sin', Var('x','complex')), F('cos', Var('x','complex'))), # jobb oldal
          'trig')
trig_rules.append(tan_rule)
       
cot_rule = Rule(F('cot', Var('x','complex')), # bal oldal
          A0('/', F('cos', Var('x','complex')), F('sin', Var('x','complex'))), # jobb oldal
          'trig')
trig_rules.append(cot_rule)

sin_1 = Rule(F('sin', AC0('+', Var('x','complex'), Var('y', 'complex'))), 
        AC0('+', AC1('*', F('sin', Var('x','complex')), F('cos', Var('y','complex'))), AC1('*', F('cos', Var('x','complex')), F('sin', Var('y','complex')))),
        'trig')    
trig_rules.append(sin_1)        

cos_1 = Rule(F('cos', AC0('+', Var('x','complex'), Var('y', 'complex'))), 
 AC0('-', AC1('*', F('cos', Var('x','complex')), F('cos', Var('y','complex'))), AC1('*', F('sin', Var('x','complex')), F('sin', Var('y','complex')))),
 'trig') 
trig_rules.append(cos_1)      

pyth_rule = Rule(AC0('+',F('^', F('sin', Var('x','complex')), 2), F('^', F('cos', Var('x','complex')), 2) ),
            1,
            'trig')
trig_rules.append(pyth_rule)