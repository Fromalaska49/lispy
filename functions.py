import sys
import re

pos = 0 # stakeholder requirement
stackCounter = 0
defunNames = []
defunParams = []
defunBodies = []
fVariables = []

def printError(error):
	print("Error: " + error)

def getExpression(line):
	if len(line) > 0:
		if line[0] == '(' and line[-1] == ')':
			return line[1:-1]
		else:
			printError("invalid expression: parentheses mismatch")
			return ""
	else:
		printError("invalid expression: len == 0")
		return ""

def getOperands(expression):
	tokens = expression.split()
	r = re.compile("[^\s]+")
	tokens = r.findall(expression)
	return tokens[:-1]

def getOperator(expression):
	tokens = expression.split()
	r = re.compile("[^\s]+")
	tokens = r.findall(expression)
	return tokens[0][1:]

def isTypeInt(x):
	try:
		return int(float(x)) == float(x)
	except ValueError:
		return False
	else:
		return True

def isTypeFloat(x):
	try:
		return bool(float(x))
	except ValueError:
		return False
	else:
		return True

def isTypeComplex(x, y = None):
	try:
		if y != None:
			return bool(complex(x, y))
		else:
			return bool(complex(x))
	except ValueError:
		return False
	else:
		return True

def allTypeNumber(items):
	for item in items:
		if not isTypeInt(item) or not isTypeFloat(item) or not isTypeComplex(item):
			return False
	return True

def onlyTypeInt(items):
	for item in items:
		if not isTypeInt(item):
			return False
	return True

def onlyTypeFloat(items):
	for item in items:
		if not isTypeFloat(item):
			return False
	return True

keywords = ["(", ")", "T", "True", "NIL", "False"]
variables = {}
def setVar(name, value):
	if name not in keywords:
		variables[str(name)] = value
	else:
		printError("invalid variable name is a keyword: " + str(name))

def isVariable(name):
	if name not in keywords:
		if name in variables:
			return True
		else:
			return False
	else:
		printError("invalid variable name is a keyword: " + str(name))
		return False

def getVarValue(name):
	if name not in keywords:
		return variables[str(name)]
	else:
		printError("invalid variable name is a keyword: " + str(name))

def evalOperands(operator, operands):
	global pos
	#print("pos = "+str(pos) + "; evalOperands(" + str(operator) + ", " + str(operands) + ")")
	if len(operands) == 0:
		printError("operand expected, but none given")
	for operandId, operand in enumerate(operands):
		if operand == "T" or operand == "True":
			operands[operandId] = True
		elif operand == "NIL" or operand == "False":
			operands[operandId] = False
		elif isVariable(operand):
			operands[operandId] = getVarValue(operand)
	onlyInts = False
	onlyFloats = False
	if onlyTypeInt(operands):
		onlyInts = True
		operands = [ int(operand) for operand in operands ]
	elif onlyTypeFloat(operands):
		onlyFloats = True
		operands = [ float(operand) for operand in operands ]
	else:
		specialOperators = ["setf", "defun"]
		if operator not in specialOperators:
			printError("invalid input: only operands of type int or float are supported")
			return float("nan")
	result = 0
	if onlyFloats:
		result = 0.0
	if operator == "+":
		for operand in operands:
			result += operand
	elif operator == "-":
		if len(operands) > 1:
			result = operands[0]
			operands = operands[1:]
			for operand in operands:
				result -= operand
		elif len(operands) == 1:
			result -= operands[0]
	elif operator == "/":
		if len(operands) > 1:
			result = operands[0]
			operands = operands[1:]
			for operand in operands:
				if operand != 0:
					result /= operand
				else:
					result = float("inf")
					printError("division by zero")
		else:
			result = 1 / operands[0]
	elif operator == "*":
		result = operands[0]
		if len(operands) > 1:
			operands = operands[1:]
			for operand in operands:
				result *= operand
	elif operator == "mod" or operator == "rem" or operator == "%":
		if len(operands) == 2:
			for operand in operands:
				if operand:
					result /= operand
				else:
					result = float("inf")
					printError("division by zero")
		else:
			printError("incorrect number of arguments: " + operator + " expects 2 arguments " + len(operands) + " given")
	elif operator == "**" or operator == "pow":
		if len(operands) == 2:
			result = pow(operands[0], operands[1])
		else:
			printError("incorrect number of arguments: " + operator + " expects 2 arguments " + len(operands) + " given")
	elif operator == "max":
		for operand in operands:
			result = max(result, operand)
	elif operator == "min":
		for operand in operands:
			result = min(result, operand)
	elif operator == ">":
		result = True
		if len(operands) > 1:
			firstOperand = operands[0]
			operands = operands[1:]
			for operand in operands:
				if firstOperand <= operand:
					result = False
		else:
			printError("incorrect number of arguments: " + operator + " expects at least 2 arguments " + len(operands) + " given")
	elif operator == "<":
		result = True
		if len(operands) > 1:
			firstOperand = operands[0]
			operands = operands[1:]
			for operand in operands:
				if firstOperand >= operand:
					result = False
		else:
			printError("incorrect number of arguments: " + operator + " expects at least 2 arguments " + len(operands) + " given")
	elif operator == ">=":
		result = True
		if len(operands) > 1:
			firstOperand = operands[0]
			operands = operands[1:]
			for operand in operands:
				if firstOperand < operand:
					result = False
		else:
			printError("incorrect number of arguments: " + operator + " expects at least 2 arguments " + len(operands) + " given")
	elif operator == "<=":
		result = True
		if len(operands) > 1:
			firstOperand = operands[0]
			operands = operands[1:]
			for operand in operands:
				if firstOperand > operand:
					result = False
		else:
			printError("incorrect number of arguments: " + operator + " expects at least 2 arguments " + len(operands) + " given")
	elif operator == "=":
		result = True
		if len(operands) > 1:
			firstOperand = operands[0]
			operands = operands[1:]
			for operand in operands:
				if firstOperand != operand:
					result = False
		else:
			printError("incorrect number of arguments: " + operator + " expects at least 2 arguments " + len(operands) + " given")
	elif operator == "/=":
		result = True
		if len(operands) > 1:
			for operand in operands:
				operands.remove(operand)
				if operand in operands:
					result = False
		else:
			printError("incorrect number of arguments: " + operator + " expects at least 2 arguments " + len(operands) + " given")
	elif operator == "and":
		result = True
		if len(operands) > 1:
			for operand in operands:
				if not operand:
					result = False
		else:
			printError("incorrect number of arguments: " + operator + " expects at least 2 arguments " + len(operands) + " given")
	elif operator == "or":
		result = False
		if len(operands) > 1:
			for operand in operands:
				if operand:
					result = True
	elif operator == "not":
		result = True
		if len(operands) == 1:
			if operands[0]:
				result = False
		else:
			printError("incorrect number of arguments: " + operator + " expects 1 argument " + len(operands) + " given")
	elif operator == "setf":
		if len(operands) % 2 != 0:
			printError("no value given for variable " + str(operands[-1]))
			return False
		else:
			i = 0
			while i < len(operands):
				setVar(operands[i], operands[i + 1])
				i += 2
			return True
	elif operator == "defun":
		tmp = operands
		string = " ".join(tmp)
		print(string)
		if not re.match("^(\w+)\s\((?!setf|defun)(\w+\s)*(\w+)\)\s(\((?!.*defun).+\))+$", string):
			printError("invalid function declaration: " + str(string))
			return False
		else:
			groups = re.search(r"^(\w+)\s\(([a-zA-Z\-_0-9\s]*)\)\s(\((?!.*defun).+\))+$", string)
			if groups != None:
				parameters = []
				# clean this up later
				gs = groups.groups(1)
				print("gs = "+str(gs))
				fname = groups.group(1)
				print("name = "+str(fname))
				parameters.append(groups.group(2))
				for parameterId, parameter in enumerate(parameters):
					parameters[parameterId] = parameter.strip()
				parameters = parameters[0]
				body = groups.group(3)
				body = body[:-1] # slice off outer paren.
				defunSetExpectedParams(parameters)
				defunSetBody(string)
			else:
				printError("could not parse function declaration: " + str(string))
	else:
		printError("unrecognized operator: " + operator)
		result = float("nan")
	#print("result = " + str(result))
	return result

def defun(name, params, body):
	if name in defunNames:
		printError("cannot create function \"" + str(name) + "\" name already in use")
		return False
	else:
		defunNames.append(name)
		defunParams.append(params)
		defunBody.append(body)
		return True

def evalFun(name, params):
	i = 0
	index = -1
	for defunName in defunNames:
		if defunName == name:
			index = i
		i += 1
	if index < 0:
		printError("undefined function: " + str(name))
		return False
	else:
		
		expectedParams = defunParams[index].split()
		if len(expectedParams) == len(params):
			

def evalExpression(expressions):
	global pos
	global stackCounter
	stackCounter += 1
	operands = []
	tmp = expressions[pos:]
	operator = getOperator(" ".join(tmp)) # I know this is horrible, I have some remorse, just not enough to change it
	pos += 1
	i = pos
	specialOperatorStack = 1
	if operator == "defun":
		while i < len(expressions) and specialOperatorStack > 0:
			expression = expressions[i]
			operands.append(expression)
			for character in expression:
				if character == '(':
					specialOperatorStack += 1
				elif character == ')':
					specialOperatorStack -= 1
			i += 1
		else:
			if specialOperatorStack != 0:
				printError("parentheses mismatch")
		pos = i
		return evalOperands(operator, operands)
	while i < len(expressions):
		expression = expressions[i]
		#print(str(operands) + " -|- " + expression + " " + str(pos) + " " + str(i))# + " -|- " + str(expressions))
		if expression[0] == '(':#pos += 1
			operands.append(evalExpression(expressions))
			i = pos
			expression = expressions[i]
			stackCounter -= 1
			if stackCounter > 0:
				#print("pos = "+str(pos) + "; evalOperands1(" + str(operator) + ", " + str(operands) + "); stackCounter == " + str(stackCounter))
				return evalOperands(operator, operands)
			
			elif pos >= len(expressions) - 1:
				#print(str(expressions) + "w/operand"+str(operator)+"w/operators"+str(operands))
				#print("pos = "+str(pos) + "; evalOperands1(" + str(operator) + ", " + str(operands) + "); stackCounter == " + str(stackCounter))
				return evalOperands(operator, operands)
				pos += 1
			
			else:
				#print(str(expressions) + "w/operand"+str(operator)+"w/operators"+str(operands))
				pos += 1
		elif expression[-1] == ')':
			stackCounter = len(expression)
			expression = expression.strip(')')
			stackCounter -= (len(expression))
			if len(expression) > 0:
				operands.append(expression)
			#print("pos = "+str(pos) + "; evalOperands2(" + str(operator) + ", " + str(operands) + ")")
			return evalOperands(operator, operands)
		else:
			pos += 1
			operands.append(expression)
		i += 1
		#print("i = "+str(i)+"; pos = "+str(pos) + "; expression = " + str(expression))
	printError("et tu Brute")

filename = ""
if len(sys.argv) >= 2:
	filename = sys.argv[1]
else:
	printError("too few arguments, input file expected")
	exit()
# filename = input("Input file: ")
f = open(filename,'r')

for line in f:
	line = line.rstrip()
	line = re.sub(r'\)\(', ') (', line)
	print(line)
	expressions = line.split()
	pos = 0
	if line[0] != '(':
		printError("parentheses mismatch")
	else:
		print(str(evalExpression(expressions)))
