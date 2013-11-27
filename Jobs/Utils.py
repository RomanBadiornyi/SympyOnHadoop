import re


# Gets symbol index
def getSymbolIndex(symbol):
	return int(re.search('[0-9]+', symbol).group())


# Gets symbols list from equation
def getSymbolsList(expr):
	return re.findall('_x[0-9]+_', expr)


# Replaces one symbol by another one
def replaceSymbol(expr, original, replace):
	regex = re.compile(re.escape(original))
	return regex.sub(replace, expr)


# Check if expression has some symbols, if not then result is ready
def checkIfResultReady(expr):
	regex = '_x[0-9]+_'
	return len(re.findall(regex, expr)) == 0


# Build and returns counts of all symbols, dictionaries of symbolsByIndexes and indexesBySymbols,
def processSymbols(systemEquations):
	symbols = list(map(lambda x: getSymbolsList(x), systemEquations))
	flattenSymbolsSet = set([symbol for equations in symbols for symbol in equations])
	symbolsList = list(flattenSymbolsSet)
	indexesList = list(map(lambda symbol: getSymbolIndex(symbol), symbolsList))
	return len(symbolsList), dict(zip(symbolsList, indexesList)), dict(zip(indexesList, symbolsList))


# Sort symbols by indexes
def sortSymbols(symbols, indexesBySymbols, symbolsByIndexes):
	indexes = [indexesBySymbols.get(symbol) for symbol in symbols]
	indexes.sort()
	return [symbolsByIndexes.get(index) for index in indexes]
