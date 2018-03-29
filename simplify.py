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
def simplify_step(expr, rules, transformations, simplicity_measure):
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
#   63. oldaltól: http://people.inf.elte.hu/krtamas/03%20__[Joel_S._Cohen]_Computer_algebra_and_symbolic_comp.pdf
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

#Példa egyszerűsítési mértékekre: minél hosszabb/rövidebb annál "egyszerűbb"
def m(x):
    return -len(str(x))
def m2(x):
    return len(str(x))

#Példa szabály: sin([[2k]]x) -> 2*sin(k*x)*cos(k*x)
sin_rule = Rule(F('sin', AC0('*', E(separate_2, 'k'), Var('x', 'complex'))), #bal oldal (source)
                AC0('*', F('sin', AC0('*', Var('k', 'integer'), Var('x', 'complex'))), F('cos', AC0('*', Var('k', 'integer'), Var('x', 'complex')))), #jobb oldal (target)
                'trig')
#Példa szabály: 1*x -> x
one_rule = Rule(AC0('*', 1, Var('x', 'complex')), #bal oldal (source)
                Var('x', 'complex'), #jobb oldal (target)
                'trig')

#Példa kifejezés: sin(4*a)+sin(2*b)
expr=AC0('+', F('sin', AC1('*', 'a', 4)), F('sin', AC1('*', 2, 'b')))
print("expr:", expr)
print("simplified:", simplify(expr, [sin_rule, one_rule], [eval_tree], m))
result=simplify(expr, [sin_rule, one_rule], [eval_tree], m)
#Egy másik mértékkel:
print("simplified:", simplify(result, [sin_rule, one_rule], [eval_tree], m2))
