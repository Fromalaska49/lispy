import sys
import re

pos = 0 # stakeholder requirement
stackCounter = 0
defunNames = []
defunParams = []
defunBodies = []
fVars = {}
fPos = {}
fStackCounter = {}
fStackPointer = 0

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
operators = ["mod", "rem", "+", "-", "*", "/", "**", "pow", "max", "min", "=", "/=", "<", "<=", ">", ">=", "%", "setf", "defun"]
variables = {}

def throwError(errorType, message):
	errorOutput = "undefined error"
	if errorType == "VariableNameError":
		errorOutput = "illegal variable name"
		if len(message) > 0:
			errorOutput += ": " + str(message)
	else:
		print
	printError(errorOutput)

def setVar(name, value):
	if name not in keywords:
		if name not in operators:
			if name not in variables:
				variables[str(name)] = value
			else:
				throwError("VariableNameError", "duplicate: " + str(name))
		else:
			throwError("VariableNameError", "operand: " + str(name))
	else:
		throwError("VariableNameError", "keyword: " + str(name))

def setFunVar(fId, name, value):
	global fVars
	if name not in keywords:
		if name not in operators:
			key = str(fId) + "." + str(name)
			if key not in fVars:
				fVars[key] = value
			else:
				throwError("VariableNameError", "duplicate: " + str(name))
		else:
			throwError("VariableNameError", "operand: " + str(name))
	else:
		throwError("VariableNameError", "keyword: " + str(name))

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

def isFunVariable(name):
	global fVars
	if name not in keywords:
		if name in fVars:
			return True
		else:
			return False
	else:
		printError("invalid variable name is a keyword: " + str(name))
		return False

def getFunVarValue(name):
	global fVars
	if name not in keywords:
		return fVars[str(name)]
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
		operands = [int(operand) for operand in operands]
	elif onlyTypeFloat(operands):
		onlyFloats = True
		operands = [float(operand) for operand in operands]
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
		result = False
		if len(operands) > 1:
			for operand in operands:
				operands.remove(operand)
				if operand not in operands and len(operands) > 0:
					result = True
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
		#print(string)
		if not re.match("^(\w+)\s\((?!setf|defun)(\w+\s)*(\w+)\)\s(\((?!.*defun).+\))+$", string):
			printError("invalid function declaration: " + str(string))
			return False
		else:
			groups = re.search(r"^(\w+)\s\(([a-zA-Z\-_0-9\s]*)\)\s(\((?!.*defun).+\))+$", string)
			if groups != None:
				parameters = []
				# clean this up later
				gs = groups.groups(1)
				#print("gs = "+str(gs))
				fname = groups.group(1)
				#print("name = "+str(fname))
				parameters.append(groups.group(2))
				for parameterId, parameter in enumerate(parameters):
					parameters[parameterId] = parameter.strip()
				parameters = parameters[0]
				body = groups.group(3)
				body = body[:-1] # slice off outer paren.
				return defun(fname, parameters, body)
			else:
				printError("could not parse function declaration: " + str(string))
	else:
		if operator in defunNames:
			#print("l328")
			return evalFun(operator, operands)
		else:
			printError("unrecognized operator: " + operator)
			result = float("nan")
	#print("result = " + str(result))
	return result

def defun(name, params, body):
	global defunNames
	global defunParams
	global defunBodies
	if name in defunNames:
		printError("cannot create function \"" + str(name) + "\" name already in use")
		return False
	else:
		tmpParams = params.split()
		for param in tmpParams:
			tmpParams.remove(param)
			if param in tmpParams:
				printError("duplicate parameter " + str(param) + " in function declaration " + str(name))
				return False
		defunNames.append(name)
		defunParams.append(params)
		defunBodies.append(body)
		return True

def evalFun(name, params):
	global fStackPointer
	global fStackCounter
	global fVars
	global fPos
	global defunNames
	global defunParams
	global defunBodies
	#print("evalFun("+str(name)+", "+str(params)+")")
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
		fId = fStackPointer
		fPos[str(fId)] = 0
		fVars[str(fId)] = []
		fStackCounter[str(fId)] = 0
		fStackPointer += 1
		expectedParams = defunParams[index].split()
		i = 0
		finalParams = []
		while i < len(params):
			parenStack = 0
			if params[i][0] == '(':
				expressions = params[i][1:]
				for char in params[i]:
					if char == '(':
						parenStack += 1
					elif char == ')':
						parenStack -= 1
				i += 1
				while parenStack > 0 and i < len(params):
					expressions += " " + params[i]
					for char in params[i]:
						if char == '(':
							parenStack += 1
						elif char == ')':
							parenStack -= 1
					i += 1
				expressions = str(expressions)
				#print("ex = "+expressions)
				#expressions = expressions[:-1]
				fPos[str(fStackPointer)] = 0
				fVars[str(fStackPointer)] = []
				fStackCounter[str(fStackPointer)] = 0
				fStackPointer += 1
				expressions = str("("+str(expressions))
				expressions = expressions.split()
				v = evalFunExpression(fStackPointer - 1, expressions)
				finalParams.append(v)
			else:
				finalParams.append(params[i].strip(")"))
				i += 1
		#print(str(finalParams))
		if len(expectedParams) == len(finalParams):
			i = 0
			while i < len(finalParams):
				varName = expectedParams[i]
				fVarKey = str(fId) + "." + str(varName)
				fVars[fVarKey] = finalParams[i]
				i += 1
			#print("asdqfew "+str(params))
			return evalFunExpression(fId, defunBodies[index].split())
		else:
			printError("incorrect number of arguments for function " + str(name) + " " + str(len(expectedParams)) + " expected but " + str(len(params)) + " recieved")
			return False

def evalFunOperands(fId, operator, operands):
	global fPos
	#print("fPos[str(fId)] = "+str(fPos[str(fId)]) + "; evalFunOperands(" + str(fId) + ", " + str(operator) + ", " + str(operands) + ")")
	if len(operands) == 0:
		printError("operand expected, but none given")
	for operandId, operand in enumerate(operands):
		if operand == "T" or operand == "True":
			operands[operandId] = True
		elif operand == "NIL" or operand == "False":
			operands[operandId] = False
		elif isFunVariable(str(fId) + "." + str(operand)):
			operands[operandId] = getFunVarValue(str(fId) + "." + str(operand))
		elif isVariable(str(operand)):
			operands[operandId] = getVarValue(str(operand))
	onlyInts = False
	onlyFloats = False
	if onlyTypeInt(operands):
		onlyInts = True
		operands = [int(operand) for operand in operands]
	elif onlyTypeFloat(operands):
		onlyFloats = True
		operands = [float(operand) for operand in operands]
	else:
		specialOperators = ["setf", "defun"]
		if operator not in specialOperators:
			#print("so = "+str(operands))
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
		result = False
		if len(operands) > 1:
			for operand in operands:
				operands.remove(operand)
				if operand not in operands and len(operands) > 0:
					result = True
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
				setFunVar(fId, operands[i], operands[i + 1])
				i += 2
			return True
	elif operator == "defun":
		tmp = operands
		string = " ".join(tmp)
		if not re.match("^(\w+)\s\((?!setf|defun)(\w+\s)*(\w+)\)\s(\((?!.*defun).+\))+$", string):
			printError("invalid function declaration: " + str(string))
			return False
		else:
			groups = re.search(r"^(\w+)\s\(([a-zA-Z\-_0-9\s]*)\)\s(\((?!.*defun).+\))+$", string)
			if groups != None:
				parameters = []
				# clean this up later
				gs = groups.groups(1)
				fname = groups.group(1)
				parameters.append(groups.group(2))
				for parameterId, parameter in enumerate(parameters):
					parameters[parameterId] = parameter.strip()
				parameters = parameters[0]
				body = groups.group(3)
				body = body[:-1] # slice off outer paren.
				return defun(fname, parameters, body)
			else:
				printError("could not parse function declaration: " + str(string))
	else:
		printError("unrecognized operator: " + operator)
		result = float("nan")
	#print("result = " + str(result))
	return result

def evalFunExpression(fId, expressions):
	global fPos
	global fStackCounter
	fStackCounter[str(fId)] += 1
	operands = []
	tmp = expressions[fPos[str(fId)]:]
	operator = getOperator(" ".join(tmp)) # I know this is horrible, I have some remorse, just not enough to change it
	fPos[str(fId)] += 1
	i = fPos[str(fId)]
	specialOperatorStack = 1
	#print(str(expressions))
	for expressionId, expression in enumerate(expressions):
		operand = expression.strip(")").strip("(")
		fVarName = str(str(fId) + "." + str(operand))
		#'''
		if isFunVariable(fVarName):
			expressions[expressionId] = expression.replace(str(operand), str(getFunVarValue(fVarName)))
		elif isVariable(fVarName):
			operands[operandId] = getVarValue(fVarName)
		else:
			#print(str(expression) + " is not a variable")
			expressions[expressionId] = expression
	if operator == "defun" or operator in defunNames:
		while i < len(expressions) and specialOperatorStack > 0:
			expression = expressions[i]
			#print(str(expression))
			operands.append(expression)
			for character in expression:
				if character == '(':
					specialOperatorStack += 1
				elif character == ')':
					specialOperatorStack -= 1
			i += 1
		else:
			if specialOperatorStack > 0:
				printError("parentheses mismatch")
		if operator in defunNames:
			operands = expressions[fPos[str(fId)]:i]
			operands[0] = operands[0][1:]
			#print(str(operands[-1]))
			if i < len(expressions):
				#print(str(i) + " " + str(len(expressions)))
				operands[-1] = operands[-1][:-2]
			#print(str(operands[-1]))
			fPos[str(fId)] = i
			#print("eso "+str(operator)+" "+str(operands))
			val = evalFun(operator, operands)
			#print("puess "+str(operator)+" "+str(operands)+" "+str(expressions)+" i = "+str(i)+" pos = "+str(pos)+" "+str(val))
			return val
		else:
			return evalOperands(operator, operands)
		fPos[str(fId)] = i
	while i < len(expressions):
		expression = expressions[i]
		#print(str(operands) + " -|- " + expression + " " + str(fPos[str(fId)]) + " " + str(i))# + " -|- " + str(expressions))
		if expression[0] == '(':#fPos[str(fId)] += 1
			#print(str(expressions))
				#'''
			#print("tis"+str(expressions))
			operands.append(evalFunExpression(fId, expressions))
			#print("xnc "+str(i) + " " + str(fPos[str(fId)]))
			i = fPos[str(fId)]
			fStackCounter[str(fId)] -= 1
			#print("the exp = "+str(expressions[i])+" "+str(fStackCounter[str(fId)]))
			if i >= len(expressions) - 1:
				if fStackCounter[str(fId)] > 0:
					#print("fStackCounter[str(fId)] > 0")
					#print("fPos[str(fId)] = "+str(fPos[str(fId)]) + "; evalOperands1(" + str(operator) + ", " + str(operands) + "); stackCounter == " + str(stackCounter))
					return evalFunOperands(fId, operator, operands)
				
				elif fPos[str(fId)] >= len(expressions) - 1:
					#print(str(expressions) + "w/operand"+str(operator)+"w/operators"+str(operands))
					#print("fPos[str(fId)] = "+str(fPos[str(fId)]) + "; evalOperands1(" + str(operator) + ", " + str(operands) + "); stackCounter == " + str(stackCounter))
					return evalFunOperands(fId, operator, operands)
					fPos[str(fId)] += 1
			else:
				#print(str(expressions) + "w/operand"+str(operator)+"w/operators"+str(operands))
				fPos[str(fId)] += 1
		elif expression[-1] == ')':
			fStackCounter[str(fId)] = len(expression)
			expression = expression.strip(')')
			fStackCounter[str(fId)] -= (len(expression))
			if len(expression) > 0:
				operands.append(expression)
			#print("fPos[str(fId)] = "+str(fPos[str(fId)]) + "; evalOperands2(" + str(operator) + ", " + str(operands) + ")")
			#print("hi "+str(operator) + " " + str(operands))
			return evalFunOperands(fId, operator, operands)
		else:
			fPos[str(fId)] += 1
			operands.append(expression)
		i += 1
		#print("klmkmlsa i = "+str(i)+"; fPos[str(fId)] = "+str(fPos[str(fId)]) + "; expression = " + str(expression))
	printError("unknown error")
	return False

def evalExpression(expressions):
	global pos
	global stackCounter
	#print("stackCounter = "+str(stackCounter))
	stackCounter += 1
	operands = []
	tmp = expressions[pos:]
	operator = getOperator(" ".join(tmp)) # I know this is horrible, I have some remorse, just not enough to change it
	pos += 1
	i = pos
	specialOperatorStack = 1
	if operator == "defun" or operator in defunNames:
		while i < len(expressions) and specialOperatorStack > 0:
			expression = expressions[i]
			#print(str(expression))
			operands.append(expression)
			for character in expression:
				if character == '(':
					specialOperatorStack += 1
				elif character == ')':
					specialOperatorStack -= 1
			i += 1
		else:
			if specialOperatorStack > 0:
				printError("parentheses mismatch")
		stackCounter -= 1
		if operator in defunNames:
			operands = expressions[pos:i]
			operands[0] = operands[0][1:]
			#print(str(operands[-1]))
			if i < len(expressions):
				#print(str(i) + " " + str(len(expressions)))
				operands[-1] = operands[-1][:-2]
			#print(str(operands[-1]))
			#print("hiya"+str(operands)+" i = "+str(i)+" pos = "+str(pos))
			i -= 1
			pos = i
			#print("this un "+str(operator)+" "+str(operands))
			val = evalFun(operator, operands)
			#print("well... "+str(val))
			return val
		else:
			return evalOperands(operator, operands)
	while i < len(expressions):
		expression = expressions[i]
		#print(str(operands) + " -|- " + expression + " " + str(pos) + " " + str(i))# + " -|- " + str(expressions))
		if expression[0] == '(':#pos += 1
			operands.append(evalExpression(expressions))
			#print("hishe"+str(operands) + " " + str(operands[-1]) + " " + str(expressions) + " " + str(i) + " " + str(pos))
			i = pos
			if i >= len(expressions):
				return evalOperands(operator, operands)
			expression = expressions[i]
			stackCounter -= 1
			if stackCounter > 0:
				#print("pos = "+str(pos) + "; evalOperands1(" + str(operator) + ", " + str(operands) + "); stackCounter == " + str(stackCounter))
				#print("asc"+str(operands)+str(expressions)+str(stackCounter))
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
			#print(str(operands) + " " + str(expressions) + " " + str(pos))
			if len(expression) > 0:
				operands.append(expression)
			#print("pos = "+str(pos) + "; evalOperands2(" + str(operator) + ", " + str(operands) + ")")
			return evalOperands(operator, operands)
		else:
			pos += 1
			operands.append(expression)
		i += 1
		#print("i = "+str(i)+"; pos = "+str(pos) + "; expression = " + str(expression))
	printError("unknown error")
	return float("False")

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
		stackCounter = 0
