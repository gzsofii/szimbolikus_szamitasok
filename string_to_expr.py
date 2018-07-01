from simplify import *
import re
import numbers

def expression_from_string(str):
	tokens = make_tokens(str)
	postfix = infix_to_postfix(tokens)
	return postfix_to_expression(postfix)

def postfix_to_expression(tokens):
	if tokens == None:
		return None
	stack = []
	for token in tokens:
		if token[0] == 'var':
			var = token[1]
			if isinstance(var, numbers.Integral):
				stack.append(var)
			else:
				stack.append(Var(var, 'complex'))
		elif token[0] == 'op':
			op = token[1]
			argnum = token[2]
			args = [stack.pop() for i in range(argnum)]
			args.reverse()
			if op in "/*-+^":
				if op in "+*":
					stack.append(AC0(op, *args))
				elif op == '/':
					stack.append(A0(op, *args))
				else:
					stack.append(F(op, *args))
			else:
				stack.append(F(op, *args))
		else:
			return None
	return stack[0]

def infix_to_postfix(tokens):
	operators = []
	numOfOperands = []
	postfix = []
	
	for i in range(len(tokens)):
		token = tokens[i]
		#print("token:", token)
		
		if token == '(':
			operators.append(token)
		elif token == ')':
			while len(operators) != 0 and operators[-1] != '(':
				postfix.append(("op", operators.pop(), numOfOperands.pop()))
			if len(operators) == 0:
				return None
			else:
				operators.pop()
		elif token == ',':
			while len(operators) != 0 and operators[-1] != '(':
				postfix.append(("op", operators.pop(), numOfOperands.pop()))
			numOfOperands[-1] += 1
			continue
		elif not isinstance(token, numbers.Integral) and (token in "+/*-^" or (i+1 < len(tokens) and tokens[i+1] == '(')):
			#print("  operator")
			while len(operators) != 0 and prec(token) <= prec(operators[-1]):
				postfix.append(("op", operators.pop(), numOfOperands.pop()))
			operators.append(token)
			if token in '/*-+^':
				numOfOperands.append(2)
			else:
				numOfOperands.append(1)
		else:
			#print("  operand")
			postfix.append(("var", token))
		#print("  stack:", operators)
		#print("  out  :", postfix)
	while len(operators) != 0:
		postfix.append(("op", operators.pop(), numOfOperands.pop()))
	return postfix

def prec(op):
	if op == '(':
		return 0
	elif op in '+-':
		return 1
	elif op in '*/':
		return 2
	elif op == '^':
		return 3
	else:
		return 4

def make_tokens(str):
	i = 0
	tokens = []
	while i < len(str):
		if str[i] in '/*-+^,()':
			tokens.append(str[i])
			i += 1
		elif str[i] in '0123456789':
			m = re.search("[0-9]*",str[i:])
			s = m.group(0)
			tokens.append(int(s))
			i += len(s)
		elif str[i] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
			m = re.search("[a-zA-Z_]*",str[i:])
			s = m.group(0)
			tokens.append(s)
			i += len(s)
		else:
			i += 1
	return tokens


if __name__ == '__main__':
	a = make_tokens("10 + c")
	a = make_tokens("10*b + 5*c^3 - 3 + x")
	a = make_tokens("cos(10*x)")
	a = make_tokens("10*(a+b)*cos(c+d+e)-2*e^2")
	a = make_tokens("f(10*x, 6*x+2) - 10 * g (x^2,2)^2")
	b = infix_to_postfix(a)
	c = postfix_to_expression(b)
	print("============================================================")
	print(a)
	print("============================================================")
	print(b)
	print("============================================================")
	print(c)
	print("============================================================")