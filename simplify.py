import copy
import itertools
import numbers

##############################################
# Kifejezésfák
##############################################

#Átírási szabály
#source: a szabály bal oldala
#target: a szabály jobb oldala
#tags: tag-ek
class Rule:
    def __init__(self, source, target, *tags):
        self.source = source
        #A bal oldal összes változatának előállítása és tárolása (kivéve ha le van tiltva egy speciális tag-el)
        self.all_sources = [source] if "disable_ac_matching" in tags else generate_patterns(source)
        self.target = target
        self.tags = tags
    def __repr__(self):
        return str(self.source) + " -> " + str(self.target) + " (tags: {})".format(", ".join(self.tags))

#Egy függvényt reprezentál a kifejezésfában
#name: név
class Function:
    def __init__(self, name, *args, **kwargs):
         self.name = name
         self.args = list(args)
         #A paraméterlista eredeti hossza
         #Ahhoz kell, hogy ha asszociatív függvényeket összevonunk (pl. +(1,+(2,3)) -> +(1,2,3))
         #akkor később vissza tudjuk állítani az összevont alakból az eredetit.
         self.original_arg_count = len(args)
         self.commutative = False
         self.assoc = -1
         for k, v in kwargs.items():
             if k == "commutative" and type(v) == bool:
                self.commutative = v
             elif k == "associative" and type(v) == int:
                self.assoc = v
             else:
                print("Invalid keyword argument: {} = {}".format(k, v))
    #Kiírás (konvertálás string-é)
    def __repr__(self):
        if self.name in "+-*/%":
            if len(self.args) == 1:
                return "("+self.name+str(self.args[0])+")"
            else:
                return "("+self.name.join(map(str, self.args))+")"
        return "{}({})".format(self.name, ", ".join(map(str, self.args)))
    #Egyenlőség
    def __eq__(self, other):
        return type(other) is Function and self.name == other.name and self.args == other.args and self.commutative == other.commutative and self.assoc == other.assoc

#Egy szabályillesztésben használt változó a kifejezésfában
#name: a változó neve
#további argumentumok: tag-ek
class Var:
    def __init__(self, name, *args):
        self.name = name
        self.tags = set(args)
    def __repr__(self):
        return self.name
    def __eq__(self, other):
        return type(other) is Var and self.name == other.name

#Egyedi illesztési szabály a kifejezésfában
#Használható konstansok felbontására
#Pl. a sin(4*a) nem illeszkedik a sin(2*x) szabályra, de a sin([[2k]]*x) szabályra igen
#func: egy Python függvény neve, ami első paraméterként megkapja az illesztendő kifejezést, a további paraméterei pedig a változónevek amikhez
#értéket kell rendelni, lásd alább a separate_2 függvényt
class External:
    def __init__(self, func, *func_args):
        self.func = func
        self.func_args = func_args
    def __repr__(self):
        return "[["+self.func.__name__+"({})]]".format(", ".join(self.func_args))
    def __eq__(self, other):
        return type(other) is External and self.func == other.func and self.func_args == other.func_args

class Fraction:
    def __init__(self, num, denom):
        if not isinstance(num, numbers.Integral) or not isinstance(denom, numbers.Integral):
            self = None
            return

        self.num = num 
        self.denom = denom

    def __repr__(self):
        return "Fraction({}, {})".format(self.num, self.denom)

    def __eq__(self, other):
        return type(other) is Fraction and self.num == other.num and self.denom == other.denom

#Megpróbál 2-t leválasztani egy konstansból.
#Ha nincs illeszkedés, None-t kell visszaadni, egyébként egy dict-et a változónevekkel és hozzájuk tartozó értékekkel
#Használat: External(separate_2, 'k')
def separate_2(expr, varname):
    if type(expr) != int or expr % 2 == 1:
        return None
    return {varname: int(expr/2)}

#Rövidítések
F = lambda name, *args: Function(name, *args)
C = lambda name, *args: Function(name, *args, commutative=True)
AC0 = lambda name, *args: Function(name, *args, commutative=True, associative=0)
AC1 = lambda name, *args: Function(name, *args, commutative=True, associative=1)
AC2 = lambda name, *args: Function(name, *args, commutative=True, associative=2)
AC3 = lambda name, *args: Function(name, *args, commutative=True, associative=3)
AC4 = lambda name, *args: Function(name, *args, commutative=True, associative=4)
AC5 = lambda name, *args: Function(name, *args, commutative=True, associative=5)
A0 = lambda name, *args: Function(name, *args, associative=0)
A1 = lambda name, *args: Function(name, *args, associative=1)
A2 = lambda name, *args: Function(name, *args, associative=2)
A3 = lambda name, *args: Function(name, *args, associative=3)
A4 = lambda name, *args: Function(name, *args, associative=4)
A5 = lambda name, *args: Function(name, *args, associative=5)
E = lambda func, *args: External(func, *args)

##############################################
# Mintaillesztés és átírás
##############################################

#Összevonja az azonos típusú asszociatív függvényeket
#Pl. +(1,+(2,+(3,4))) -> +(1,2,3,4)
def flatten(tree):
    if type(tree) is Function:
        new_args = []
        for arg in tree.args:
            if type(arg) is Function and arg.assoc == tree.assoc and arg.assoc != -1:
                if arg.original_arg_count == tree.original_arg_count:
                    arg = flatten(arg)
                    for a in arg.args:
                        new_args.append(a)
                else:
                    print("Error: the same associative function appears with different number of arguments")
                    new_args.append(flatten(arg))
            else:
                new_args.append(flatten(arg))
        tree.args = new_args
    return tree

#A flatten fordítottja, a "legbaloldalibb" fát állítja elő
#Pl. +(1,2,3,4) -> +(+(+(1,2),3),4)
def unflatten(param_list, orig_function):
    if len(param_list) == orig_function.original_arg_count:
        return param_list
    new_list = copy.deepcopy(param_list)
    func = copy.deepcopy(orig_function)
    func.args = copy.deepcopy(new_list[:orig_function.original_arg_count])
    new_list[:orig_function.original_arg_count] = [func]
    return unflatten(new_list, orig_function)

#Mint az unflatten, de az összes lehetséges fát előállítja
def generate_assoc_trees(param_list, orig_function):
    if len(param_list) == orig_function.original_arg_count:
        return [param_list]
    res = []
    for k in range(len(param_list)-orig_function.original_arg_count+1):
        new_list = copy.deepcopy(param_list)
        func = copy.deepcopy(orig_function)
        func.args = copy.deepcopy(new_list[k:k+orig_function.original_arg_count])
        new_list[k:k+orig_function.original_arg_count] = [func]
        res = res + generate_assoc_trees(new_list, orig_function)
    return res

#Egy mintához az összes lehetséges bal oldal előállítása (a kommutatív és asszociatív tulajdonságok alapján)
#Pl. +(x,y) mintához +(y,x) is, +(1,+(x,y)) mintához +(+(1,x),y), +(+(x,1),y), +(1,+(y,x)), +(x,+(1,y)) stb.
def generate_patterns_internal(pattern):
    if type(pattern) is Function:
        patterns = [pattern]
        for k in range(len(pattern.args)):
            new_patterns = []
            for new_arg_k in generate_patterns_internal(pattern.args[k]):
                for old_pattern in patterns:
                    p = copy.deepcopy(old_pattern)
                    p.args[k] = new_arg_k
                    new_patterns.append(p)
            patterns = new_patterns
        res = []
        for p in patterns:
            for perm in (itertools.permutations(p.args) if p.commutative else [p.args]):
                if p.assoc >= -1 and len(p.args) > p.original_arg_count:
                    assoc_trees = generate_assoc_trees(list(perm), p)
                    for tree in assoc_trees:
                        res.append(copy.deepcopy(p))
                        res[-1].args = tree
                else:
                    res.append(copy.deepcopy(p))
                    res[-1].args = list(perm)
        return res
    else:
        return [pattern]

def generate_patterns(pattern):
    return generate_patterns_internal(flatten(pattern))

#Ellenőrzi, hogy két dict-el megadott változó -> érték hozzárendelés kompatibilis-e (ha mindkettőben szerepel egy változó, akkor ugyanaz-e az érték?)
def is_compatible_match(m1, m2):
    if m1 == None or m2 == None: return False
    for key in m1:
        if key in m2:
            if m1[key] != m2[key]: return False
    return True

#Mintaillesztés rekurzívan
def match(tree, pattern):
    if type(pattern) is External:
        res = pattern.func(tree, *pattern.func_args)
        if res != None:
            return res
    if type(pattern) is Var:
        return {pattern.name: tree}
    if type(pattern) is Function and type(tree) is Function and pattern.name == tree.name:
        current_match = {}
        if len(pattern.args) != len(tree.args):
            return None
        else:
            for k in range(len(pattern.args)):
                match_res = match(tree.args[k], pattern.args[k])
                if is_compatible_match(match_res, current_match):
                    current_match = dict(current_match, **match_res)
                else:
                    return None
            return current_match
    if pattern != tree:
        return None
    return {}

#Az első paraméter egy fa, a második egy dict ami változó -> érték párokat tartalmaz.
#A fában a változókat lecseréli az adott értékekre.
def replace_in_tree(tree, match_res):
    if type(tree) is Function:
        for k in range(len(tree.args)):
            tree.args[k] = replace_in_tree(tree.args[k], match_res)
    if type(tree) is Var:
        if tree.name in match_res:
            return match_res[tree.name]
    return tree

#Egy átírási szabályt alkalmaz egy fára (rekurzívan).
#Megnézi, hogy az adott részfa illeszkedik-e a szabály bal oldalára (match),
#ha igen, akkor átírja a fát a szabály jobb oldalaként adott kifejezésre (replace_in_tree).
def apply_rule_in_tree(rule, tree):
    if type(tree) is Function:
        for k in range(len(tree.args)):
            tree.args[k] = apply_rule_in_tree(rule, tree.args[k])
    for src in rule.all_sources:
        match_res = match(tree, src)
        if match_res != None and match_res != {}:
            return replace_in_tree(copy.deepcopy(rule.target), match_res)
    return tree

##############################################
# Egyszerűsítés
##############################################

#Csak konstansokat tartalmazó kifejezések kiértékelése
#Ez nem az egyszerűsítő algoritmus dolga, de mivel itt most nincs mögötte egy komputeralgebra rendszer ami
#elvégezné a kiértékelést, a legegyszerűbb eseteket célszerű kezelni
def eval_tree(tree):
    if type(tree) is Function:
        if tree.name in "+-*/%" and len(tree.args) == 2 and isinstance(tree.args[0], numbers.Number) and isinstance(tree.args[1], numbers.Number):
            if tree.name == "+":
                return tree.args[0]+tree.args[1]
            elif tree.name == "-":
                return tree.args[0]-tree.args[1]
            elif tree.name == "*":
                return tree.args[0]*tree.args[1]
            elif tree.name == "/" and tree.args[1] != 0:
                return tree.args[0]/tree.args[1]
            elif tree.name == "%" and tree.args[1] != 0:
                return tree.args[0]%tree.args[1]
        for k in range(len(tree.args)):
            tree.args[k] = eval_tree(tree.args[k])
    return tree

#Az egyszerűsítés egy lépése
#Alkalmazza a megadott transzformációkat és átírási szabályokat.
#Az eredményt csak akkor tartja meg ha egyszerűbb a megadott mérték szerint.
def sZoLZoLimplify_step(expr, rules, transformations, simplicity_measure):
    for trf in transformations:
        expr = trf(copy.deepcopy(expr))
    for rule in rules:
        new_expr = apply_rule_in_tree(rule, copy.deepcopy(expr))
        if simplicity_measure(new_expr) < simplicity_measure(expr):
            expr = new_expr
    return expr

#Egyszerűsítés
#expr: az egyszerűsítendő kifejezés
#rules: átírási szabályok
#transformations: transzformációk amik nem fejezhetők ki átírási szabályként
#simplicity_measure: egy függvény amely egy kifejezéshez egy számot rendel, minél "egyszerűbb" egy kifejezés annál kisebbet
def simplify(expr, rules, transformations, simplicity_measure):
    new_expr = simplify_step(expr, rules, transformations, simplicity_measure)
    if simplicity_measure(new_expr) < simplicity_measure(expr):
        expr = simplify(new_expr, rules, transformations, simplicity_measure)
    return expr

#Feladatok
# Irodalom feldolgozása - hogyan működnek ezek az algoritmusok, használható ötleteket kigyűjteni, stb.
#   63. oldaltól: krtamas/03%20__[Joel_S._Cohen]_Computer_algebra_and_symbolic_comp.pdf
#   Maple: https://www.maplesoft.com/support/help/maple/view.aspx?path=simplify%2fdetails
#   https://stackoverflow.com/questions/7540227/strategies-for-simplifying-math-expressions/7542438#7542438
#
#
# A sympy egyszerűsítési algoritmusa (python) - hogyan működik, van-e olyan ötlet ami átvehető?
#   https://github.com/sympy/sympy/tree/master/sympy/simplify
#
#
# Egyszerűsítési szabályok gyűjtése
#   Források, pl.:
#       http://functions.wolfram.com/ElementaryFunctions/
#       https://en.wikipedia.org/wiki/List_of_logarithmic_identities
#       https://en.wikipedia.org/wiki/List_of_trigonometric_identities
#       stb.
#   Nem csak valós/komplex számokra alkalmazandó szabályokban kell gondolkodni: lehet egyszerűsíteni logikai kifejezéseket, mátrixokat tartalmazó kifejezéseket, általános gyűrűkben, stb. stb.
#   A szabályokat tag-ekkel kell ellátni (lásd a Rule osztály konstruktorát), például az alapján, hogy milyen esetekben alkalmazhatók (valós számokra? mátrixokra? logikai kifejezésekre?)
#   A szabályokon belüli változókat is tag-ekkel kell ellátni az alapján, hogy a változó milyen értékei mellett értelmes a szabály (pl. real, real_nonzero, complex, real_matrix, integer, boolean, stb.)
#   Sok szabály mindkét irányba működik, érdemes lehet a Rule osztályt kibővíteni valahogy ennek kezelésére, hogy ne kelljen a két irányhoz két lényegében azonos szabályt felvenni.
#
# Az egyszerűsítő algoritmus megírása
#   Egyszerűségi mértékek: hogyan lehetne jól mérni egy kifejezés egyszerűségét?
#       nincs egy jó megoldás, különböző célokra különböző mértékek.
#       Valahogy el kell kerülni, hogy egy lokális optimumba beragadjon, így nem elég mindig csak azt nézni, hogy csökkent-e az érték (ötlet: (result length)/(input length) > ratio)
#
#   Transzformációk: bizonyos átalakításokat nem lehet átírási szabályként kifejezni, ezeket rendes Python függvényként kell implementálni.
#       Ilyen például a kommutatív/asszociatív tulajdonságokat felhasználva a kifejezésfák kanonikus alakra hozása amit meg kellene írni
#       (a konstansokat előre rendezem kommutatív függvényeknél, az asszociatív függvényeknél a legbaloldalibb kifejezésfa - lásd fentebb flatten/unflatten függvények)
#       kérdés persze, hogy mikor alkalmazhatók ezek az átalakítások, tudjuk-e hogy egy adott esetben a müveletek valóban kommutatívak/asszociatívak?
#
#   Specializált függvények: az egyszerűsítésnek lehetnek speciális esetei, pl. amikor csak trigonometrikus függvényeket akarok átírni más trig. függvényekre
#       vagy exponenciális függvényekre egy kifejezésben. Ez könnyen megoldható, a szabályoknak csak egy megfelelő részhalmazát kell használni (pl. ezeket a szabályokat egy speciális tag-el lehet ellátni).
#       Lásd Maple: convert/sincos és társai.
#           https://www.maplesoft.com/support/help/maple/view.aspx?path=convert/exp
#           https://www.maplesoft.com/support/help/maple/view.aspx?path=expand
#           https://www.maplesoft.com/support/help/maple/view.aspx?path=factor
#           https://www.maplesoft.com/support/help/maple/view.aspx?path=convert%2fexpsincos
#           https://www.maplesoft.com/support/help/maple/view.aspx?path=convert%2fsincos
#           https://www.maplesoft.com/support/help/maple/view.aspx?path=convert%2fln
#
#
#   A kiértékelésről:
#       A bemenetről felthető, hogy nincsenek benne csak konstansokat tartalmazó kifejezések (pl. 1+1), ezeket
#       a komputeralgebra-rendszer kiértékelné még az egyszerűsítés előtt.
#       Mivel itt most nincs az algoritmus mögött egy komputeralgebra-rendszer ami ezt megtenné, ezért a legalapvetőbb
#       kifejezéseket célszerű mégis kiértékelni, lásd fentebb az eval_tree transzformációt.

def simplify_expr(expr):
    if isinstance(expr, numbers.Integral) or type(expr) is Var:
        return expr

    if type(expr) is Fraction:
        return simplify_fraction(expr)

    if type(expr) is Function:
        expr.args = map(simplify_expr, expr.args)
        
        if expr.name == '^':
            return simplify_power(expr)
        if expr.name == '+':
            return simplify_sum(expr)
        if expr.name == '-':
            return simplify_diff(expr)
        if expr.name == '*':
            return simplify_prod(expr)
        if expr.name == '/':
            return simplify_quot(expr)

def simplify_power(expr):
    v = expr.args[0]
    w = expr.args[1]

    if v == None or w == None:
        return None

    if isinstance(v, numbers.Number):
        if v == 0:
            if isinstance(w, numbers.Number) and w > 0:
                return 0
            elif type(w) is Fraction and w.num * w.denom > 0:
                return 0
        elif v == 1:
            return 1

    if isinstance(w, numbers.Integral):
        return simplify_int_power(v, w)

    return expr

def simplify_int_power(v, n):
    if isinstance(expr, numbers.Integral) or type(expr) is Fraction:
        return simplify_rne(Function('^', v, n))

    if n == 0:
        return 1

    if n == 1:
        return v

    if type(v) is Function:
        if v.name == '^':
            r = v.args[0]
            s = v.args[1]
            p = simplify_product(s, n)

            if isinstance(p, numbers.Integral):
                return simplify_int_power(r, p)

            return Function('^', r, p)

        if v.name == '*':
            v.args = map(simplify_int_power, v.args)
            return simplify_product(v)

    return Function('^', [v,n]);

def simplyfy_product(expr):
    # SPRD-1
    if None in expr.args:
        return None

    # SPRD-2
    if 0 in expr.args:
        return 0

    # SPRD-3
    if len(expr.args) == 1:
        return expr.args[0]

    # SPRD-4
    v = simplify_product_rec(expr.args, expr.commutative, expr.associative)
    
    if len(v) == 1: # SPRD-4-1
        return v[0]
    elif len(v) > 1: # SPRD-4-2
        return Function('*', v, commutative = expr.commutative, associative = expr.associative)
    elif len(v) == 0: # SPRD-4-3
        return 1

def simplify_product_rec(L, c, a):
    if len(L) == 2:
        # SPRDREC-1
        if not (type(L[0]) is Function and L[0].name == '*') and not (type(L[1]) is Function and L[1].name == '*'):
            # SPRDREC-1-1
            if isinstance(L[0], numbers.Number) and isinstance(L[1], numbers.Number):
                P = simlify_rne(Function('*', L, commutative = c, associative = a))
                if P == 1:
                    return []
                else:
                    return [P]
            
            # SPRDREC-1-2-a
            if isinstance(L[0], numbers.Number) and L[0] == 1:
                return [L[1]]

            # SPRDREC-1-2-b
            if isinstance(L[1], numbers.Number) and L[1] == 1:
                return [L[0]]

            # SPRDREC-1-3
            if base(L[0]) == base(L[2]):
                S = simplify_sum(Function('+', exponent(L[0]), exponent(L[1])))
                P = simplyfy_power(Function('^', base(L[0]), S))
                if isinstance(P, numbers.Number) and P == 1:
                    return []
                else:
                    return [P]

            # SPRDREC-1-4
            if c and less(L[1], L[0]):
                return [L[1], L[0]]

            # SPRDREC-1-5
            return L

        # SPRDREC-2-1
        elif type(L[0]) is Function and L[0].name == '*' and type(L[1]) is Function and L[1].name == '*':
            return merge_products(L[0].args, L[1].args, c, a)

        # SPRDREC-2-2
        elif type(L[0]) is Function and L[0].name == '*':
            return merge_products(L[0].args, [L[1]], c, a)

        # SPRDREC-2-3
        elif type(L[1]) is Function and L[1].name == '*':
            return merge_products([L[0]], L[1].args, c, a)

    # SPRDREC-3
    elif len(L) > 2:
        w = simplify_product_rec(L[1:], c, a)

        # SPRDREC-3-1
        if type(L[0]) is Function and L[0].name == '*':
            return merge_products(L[0].args, w, c, a)

        # SPRDREC-3-2
        else:
            return merge_products([L[0]], w, c, a)

def merge_product(p, q, c, a):
    # MPRD-1
    if q == []:
        return p

    # MPRD-2
    if p == []:
        return q

    # MPRD-3
    h = simplify_product_rec([p[0]], [p[1]], c, a)
    
    # MPRD-3-1
    if h == []:
        return merge_products(p[1:], q[1:], c, a)
    # MPRD-3-2
    elif len(h) == 1:
        return merge_products(p[1:], q[1:], c, a).insert(0, h[0])
    
    elif len(h) == 2:
        # MPRD-3-3
        if h[0] == p[0]:
            return merge_products(p[1:], q, c, a).insert(0, h[0])
        
        # MPRD-3-3
        elif h[0] == q[0]:
            return merge_products(p, q[1:], c, a).insert(0, h[0])

def simplyfy_sum(expr):
    # SSRD-1
    if None in expr.args:
        return None

    # SSRD-3
    if len(ex, c, gpr.args) == 1:
        return expr.args[0]

    # SSRD-4
    v = simplify_sum_rec(expr.args, expr.commutative, expr.associative)
    
    if len(v) == 1: # SSRD-4-1
        return v[0]
    elif len(v) > 1: # SSRD-4-2
        return Function('+', v, commutative = expr.commutative, associative = expr.associative)
    elif len(v) == 0: # SSRD-4-3
        return 1

def simplify_sum_rec(L, c, a):
    if len(L) == 2:
        # SSRDREC-1
        if not (type(L[0]) is Function and L[0].name == '+') and not (type(L[1]) is Function and L[1].name == '+'):
            # SSRDREC-1-1
            if isinstance(L[0], numbers.Number) and isinstance(L[1], numbers.Number):
                P = simlify_rne(Function('+', L, commutative = c, associative = a))
                if P == 0:
                    return []
                else:
                    return [P]
            
            # SSRDREC-1-2-a
            if isinstance(L[0], numbers.Number) and L[0] == 0:
                return [L[1]]

            # SSRDREC-1-2-b
            if isinstance(L[1], numbers.Number) and L[1] == 0:
                return [L[0]]

            # SSRDREC-1-3
            if term(L[0]) == term(L[2]):
                S = simplify_sum(Function('+', const(L[0]), const(L[1])))
                P = simplyfy_product(Function('*', term(L[0]), S))
                if isinstance(P, numbers.Number) and P == 0:
                    return []
                else:
                    return [P]

            # SSRDREC-1-4
            if c and less(L[1], L[0]):
                return [L[1], L[0]]

            # SSRDREC-1-5
            return L

        # SSRDREC-2-1
        elif type(L[0]) is Function and L[0].name == '+' and type(L[1]) is Function and L[1].name == '+':
            return merge_sums(L[0].args, L[1].args, c, a)

        # SSRDREC-2-2
        elif type(L[0]) is Function and L[0].name == '+':
            return merge_sums(L[0].args, [L[1]], c, a)

        # SSRDREC-2-3
        elif type(L[1]) is Function and L[1].name == '+':
            return merge_sums([L[0]], L[1].args, c, a)

    # SSRDREC-3
    elif len(L) > 2:
        w = simplify_sum_rec(L[1:], c, a)

        # SSRDREC-3-1
        if type(L[0]) is Function and L[0].name == '+':
            return merge_sums(L[0].args, w, c, a)

        # SSRDREC-3-2
        else:
            return merge_sums([L[0]], w, c, a)

def merge_sums(p, q, c, a):
    # MSRD-1
    if q == []:
        return p

    # MSRD-2
    if p == []:
        return q

    # MSRD-3
    h = simplify_sum_rec([p[0]], [p[1]], c, a)
    
    # MSRD-3-1
    if h == []:
        return merge_sums(p[1:], q[1:], c, a)

    # MSRD-3-2
    elif len(h) == 1:
        return merge_sums(p[1:], q[1:], c, a).insert(0, h[0])
    
    elif len(h) == 2:
        # MSRD-3-3
        if h[0] == p[0]:
            return merge_sums(p[1:], q, c, a).insert(0, h[0])
        
        # MSRD-3-3
        elif h[0] == q[0]:
            return merge_sums(p, q[1:], c, a).insert(0, h[0])

def simplify_rne(u):
    v = simplify_rne_rec(u)
    if v == None:
        return None

    return simplify_rational_number(v)

def simplify_rne_rec(u):
    if isinstance(u, numbers.Integral):
        return u

    elif type(u) is Fraction:
        if denom(u) == 0:
            return None

        return u

    elif type(u) is Function:
        if len(u.args) == 2:
            if u.name in "+*-/":
                v = simplify_rne_rec(u.args[0])
                w = simplify_rne_rec(u.args[1])
                if v == None or w == None:
                    return None

                if u.name == '+':
                    return eval_sum(v, w)
                if u.name == '*':
                    return eval_prod(v, w)
                if u.name == '-':
                    return eval_diff(v, w)
                if u.name == '/':
                    return eval_quot(v, w)
            elif u.name == '^':
                v = simplify_rne_rec(u.args[0])
                if v == None:
                    return None

                return eval_power(v, u.args[1])

def eval_quot(v, w):
    if numer(w)*denom(v) == 0:
        return None

    return Fraction(numer(v) * denom(w), numer(w) * denom(v))

def eval_power(v, n):
    if numer(v) != 0:
        if n > 0:
            s = eval_power(v, n-1)
            return eval_prod(s, v)
        elif n == 0:
            return 1
        elif n == -1:
            return Fraction(denom(v), numer(v))
        elif n < -1:
            s = Fraction(denom(v), numer(v))
            return eval_power(s, -n)
    else:
        if n >= 1:
            return 0
        else:
            return None

def eval_sum(v, w):
    if denom(v) * denom(w) == 0:
        return None

    return Fraction(numer(v)*denom(w) + numer(w)*denom(v), denom(v)*denom(w))

def eval_diff(v, w):
    if denom(v) * denom(w) == 0:
        return None

    return Fraction(numer(v)*denom(w) - numer(w)*denom(v), denom(v)*denom(w))

def eval_prod(v, w):
    if denom(v) * denom(w) == 0:
        return None

    return Fraction(numer(v)*numer(w), denom(v)*denom(w))

def simplify_rational_number(u):
    if isinstance(u, numbers.Integral):
        return u

    if type(u) is Fraction:
        n = u.num
        d = u.denom

        if n % d == 0:
            return n//d

        g = gcd(n, d)
        if d > 0:
            return Fraction(n // g, d // g)
        else:
            return Fraction(-n // g, -d // g)

def gcd(a, b):
    if not isinstance(a, numbers.Integral) or not isinstance(b, numbers.Integral):
        return None

    A = a
    B = b
    while B != 0:
        R = A % B
        A = B
        B = R

    return abs(A)

def term(expr):
    if type(expr) is Var or type(expr) is Function and expr.name != '*':
        return Function('*', expr)

    if type(expr) is Function and expr.name == '*':
        if isinstance(expr.args[0], numbers.Number):
            return Function('*', *expr.args[1:], commutative = expr.commutative, associative = expr.assoc)
        else:
            return expr

    if type(expr) is Fraction or isinstance(expr, numbers.Integral):
        return None

def const(expr):
    if type(expr) is Var or type(expr) is Function and expr.name != '*':
        return 1

    if type(expr) is Function and expr.name == '*':
        if isinstance(expr.args[0], numbers.Number):
            return expr.args[0]
        else:
            return 1

    if type(expr) is Fraction or isinstance(expr, numbers.Integral):
        return None

def base(expr):
    if type(expr) is Var or type(expr) is Function and expr.name != '^':
        return expr

    if type(expr) is Function and expr.name == '^':
        return expr.args[0]

    if type(expr) is Fraction or isinstance(expr, numbers.Integral):
        return None

def exponent(expr):
    if type(expr) is Var or type(expr) is Function and expr.name != '^':
        return 1

    if type(expr) is Function and expr.name == '^':
        return expr.args[1]

    if type(expr) is Fraction or isinstance(expr, numbers.Integral):
        return None

def numer(expr):
    if type(expr) is Fraction:
        return expr.num

    if expr == None:
        return None

    return expr

def denom(expr):
    if type(expr) is Fraction:
        return expr.denom

    if expr == None:
        return None

    return 1

def less(u, v):
    # O-1
    if isinstance(u, numbers.Number) and isinstance(v, numbers.Number):
        return u < v

    if isinstance(u, numbers.Number) and type(v) is Fraction:
        return u < v.num / v.denom

    if isinstance(v, numbers.Number) and type(u) is Fraction:
        return u.num / u.denom < v

    if type(v) is Fraction and type(u) is Fraction:
        return u.num / u.denom < v.num / v.denom

    # O-2
    if type(u) is Var and type(v) is Var:
        return u.name < v.name

    if type(u) is Function and type(v) is Function:
        # O-3
        if u.name == '+' and v.name == '+' or u.name == '*' and v.name =='*':
            for i in range(min(len(u.args), len(v.args))):
                if less(u.args[i], v.args[i]):
                    return True

            return len(u.args) < len(v.args)

        # O-4
        if u.name == '^' and v.name == '^':
            if base(u) != base(v):
                return less(base(u), base(v))
            
            return less(exponent(u), exponent(v))

        # O-6-a
        if u.name not in "+^-/*" and v.name not in "+^-*/":
            if u.name != v.name:
                return u.name < v.name

            # O-6-b
            for i in range(min(len(u.args), len(v.args))):
                if less(u.args[i], v.args[i]):
                    return True

            return len(u.args) < len(v.args)

    # O-7
    if (isinstance(u, numbers.Number) or type(u) is Fraction) and not (isinstance(v, numbers.Number) or type(v) is Fraction):
        return True

    # O-8
    if type(u) is Function and u.name == '*':
        if type(v) is Var or type(v) is Function and v.name != '*':
            return less(u, Function('*', v))

    # O-9
    if type(u) is Function and u.name == '^':
        if type(v) is Var or type(v) is Function and v.name not in "^*":
            return less(u, Function('^', v, 1))

    # O-10
    if type(u) is Function and u.name == '+':
        if type(v) is Var or type(v) is Function and v.name not in "+*":
            return less(u, Function('+', v))

    # O-12
    if type(u) is Function and u.name not in "+^/-*" and type(v) is Var:
        if u.name == v.name:
            return False

        return u.name < v.name

    # O-13
    return not less(v, u)

#Példa egyszerűsítési mértékekre: minél hosszabb/rövidebb annál "egyszerűbb"
def m(x):
    return -len(str(x))
def m2(x):
    return len(str(x))

##Példa szabály: sin([[2k]]x) -> 2*sin(k*x)*cos(k*x)
#sin_rule = Rule(F('sin', AC0('*', E(separate_2, 'k'), Var('x', 'complex'))), #bal oldal (source)
#                AC0('*', F('sin', AC0('*', Var('k', 'integer'), Var('x', 'complex'))), F('cos', AC0('*', Var('k', 'integer'), Var('x', 'complex')))), #jobb oldal (target)
#                'trig')
##Példa szabály: 1*x -> x
#one_rule = Rule(AC0('*', 1, Var('x', 'complex')), #bal oldal (source)
#                Var('x', 'complex'), #jobb oldal (target)
#                'trig')
#
##Példa kifejezés: sin(4*a)+sin(2*b)
#expr=AC0('+', F('sin', AC1('*', 'a', 4)), F('sin', AC1('*', 2, 'b')))
#print("expr:", expr)
#print("simplified:", simplify(expr, [sin_rule, one_rule], [eval_tree], m))
#result=simplify(expr, [sin_rule, one_rule], [eval_tree], m)
##Egy másik mértékkel:
#print("simplified:", simplify(result, [sin_rule, one_rule], [eval_tree], m2))
