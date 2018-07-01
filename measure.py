from simplify import *

def m1(x):
    return -len(str(x))
def m2(x):
    return len(str(x))

def m(tree):
    m = 0
    #súlyok
    w_a = 1
    w_h = 1
    w_l = 0.5
    args = 0
    height = 0
    length = len(str(tree))
    if type(tree) is Function:
        args = arg_count(tree)
        height = height_of_tree(tree)
    m = w_a * args + w_h * height + w_l * length
    return m

def arg_count(tree):
    c = 0
    if type(tree) is Function:
        c = len(tree.args)
        for arg in tree.args:
            c = c + arg_count(arg)
    return c

def height_of_tree(tree):
    h = 1
    if type(tree) is Function:
        max_h = 1
        for arg in tree.args:
            temp = height_of_tree(arg)
            if temp > max_h:
                max_h = temp
        h = h + max_h
    return h
