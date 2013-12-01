import re
import base64
import pickle


# Gets symbol index
def getSymbolIndex(symbol):
	return int(re.search('[0-9]+', symbol).group())


# Gets symbols list from equation
def getSymbolsList(expr):
	return re.findall('_x[0-9]+_', expr)


# Check if expression has some symbols, if not then result is ready
def checkIfResultReady(expr):
	regex = '_x[0-9]+_'
	return len(re.findall(regex, expr)) == 0


# Sort symbols by indexes
def sortSymbols(symbols):
	symbolPairs = [(getSymbolIndex(str(symbol)), symbol) for symbol in symbols]
	symbolsByIndexes = dict((symbol, index) for symbol, index in symbolPairs)
	indexesList = [index for index in symbolsByIndexes.keys()]
	indexesList.sort()
	return [symbolsByIndexes.get(index) for index in indexesList]


def encodeExpression(expression):
	return base64.b64encode(pickle.dumps(expression)).decode("latin1")


def decodeExpression(expression):
	return pickle.loads(base64.b64decode(expression.encode("latin1")))