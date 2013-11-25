#!/usr/bin/env python3.3
import re
import os
import sys
import subprocess
from datetime import datetime
from sympy.core import numbers
from sympy.solvers import solve
from sympy.simplify import simplify

NODE_COUNT = 4


def HELP_FUNCTION_GET_BLOCKS_COUNT(input):
	input = open(input, 'r')
	partIndex = 0
	lineCount = 0
	for line in input:
		lineCount += 1
		partIndex, equationIndex, equation = line.strip().split('\t')
	if lineCount == 0:
		return 0
	else:
		return int(partIndex) + 1


def hadoopSimulation(args):
	start = datetime.now()

	os.system("rm FinalResults")

	resultsCount = 0
	equationsExists = True

	MapInitDataCommand = 'cat InitInputEquations | sort -k1,1 -n | python3.3 Solver.py mapInitData | sort -k1,1 -n | cat > InputEquations'
	SplitEquationsCommand = "cat InputEquations | python3.3 Solver.py mapEquationsToNodes | sort -k1,1 -k2,2 -n | cat > InputEquationsSplit"
	ComputeEquationBlockCommand = "cat InputEquationsSplit | grep -P '^{0}\t' | python3.3 Solver.py computeEquationPart | sort | cat > OutputResults{0}"
	MergeResultsCommand = "cat OutputResults* | python3.3 Solver.py mergeResults | sort -n | cat > MergedResults"
	MapResultForSimplificationCommand = "cat MergedResults | python3.3 Solver.py mapResultForSimplification {0} | cat > ResultsForSimplification"
	JoinResultsWithEquationsMapCommand = "cat MergedResults InputEquationsSplit | sort -k1,1 -n | python3.3 Solver.py joinResultsWithEquationsMap | sort -k1,2 -n | python3.3 Solver.py joinResultsWithEquationsReduce | cat > EquationsWithResults"
	JoinEquationsWithResultForSimplificationMapCommand = "cat EquationsWithResults ResultsForSimplification | sort -k1,1 -n | python3.3 Solver.py joinEquationsWithResultForSimplificationMap | sort -k1,1 -n | python3.3 Solver.py joinEquationsWithResultForSimplificationReduce | cat > EquationsWithResultsForSimplification"
	SimplifyEquationsCommand = "cat EquationsWithResultsForSimplification | grep -P '^{0}\t' | sort -k1,1 -n -k2,2 -n | python3.3 Solver.py simplifyEquations | cat > SimplificationResult{0}"
	MergeSimplificationResultsCommand = "cat SimplificationResult* | python3.3 Solver.py mergeSimplificationEquations | sort -k1,1 -n | cat > {0}"
	CollectFinalResultsCommand = "cat MergedResults FinalResults | python3.3 Solver.py grabFinalResults | cat > FinalResults"
	ReplaceVariablesWithFinalResultsCommand = "cat FinalResults InitInputEquations | sort -k1,1 -n | python3.3 Solver.py replaceVariablesWithResults | cat > InputEquations"

	p = subprocess.Popen(MapInitDataCommand, shell=True)
	p.wait()

	print("Start computation: {0}\n".format(str(datetime.now())))
	while equationsExists:
		operationStart = datetime.now()
		p = subprocess.Popen(SplitEquationsCommand, shell=True)
		p.wait()
		operationEnd = datetime.now()
		print("Splitting equations to blocks finished, execution time: {0}\n".format(str(operationEnd - operationStart)))
		blocksCount = HELP_FUNCTION_GET_BLOCKS_COUNT('InputEquationsSplit')

		if blocksCount == 0:
			equationsExists = False

		operationStart = datetime.now()
		if not equationsExists:
			break
		for reducerNumber in range(blocksCount):
			p = subprocess.Popen(ComputeEquationBlockCommand.format(reducerNumber), shell=True)
			p.wait()
		operationEnd = datetime.now()
		print("Computing results in blocks finished, execution time: {0}\n".format(str(operationEnd - operationStart)))

		operationStart = datetime.now()
		p = subprocess.Popen(MergeResultsCommand, shell=True)
		p.wait()

		os.system("rm OutputResults*")
		finalResultsCount = getFinalResultsCount("MergedResults")
		resultsCount += finalResultsCount
		operationEnd = datetime.now()
		print("Merging results finished, execution time: {0}\n".format(str(operationEnd - operationStart)))

		if finalResultsCount == 0:
			operationStart = datetime.now()
			blocksCount = getBlocksCount("InputEquationsSplit")
			p = subprocess.Popen(MapResultForSimplificationCommand.format(blocksCount), shell=True)
			p.wait()
			p = subprocess.Popen(JoinResultsWithEquationsMapCommand, shell=True)
			p.wait()
			p = subprocess.Popen(JoinEquationsWithResultForSimplificationMapCommand, shell=True)
			p.wait()

			os.system("rm ResultsForSimplification")
			os.system("rm EquationsWithResults")

			operationEnd = datetime.now()
			print("Joining results with equations finished, execution time: {0}\n".format(str(operationEnd - operationStart)))

			operationStart = datetime.now()
			for blockNumber in range(blocksCount):
				p = subprocess.Popen(SimplifyEquationsCommand.format(blockNumber), shell=True)
				p.wait()
			operationEnd = datetime.now()
			print("Results simplification finished, execution time: {0}\n".format(str(operationEnd - operationStart)))

			os.system("rm EquationsWithResultsForSimplification")
			p = subprocess.Popen(MergeSimplificationResultsCommand.format("InputEquations"), shell=True)
			p.wait()
			p = subprocess.Popen(MergeSimplificationResultsCommand.format("UndeterminedResults"), shell=True)
			p.wait()
			os.system("rm SimplificationResult*")
		else:
			operationStart = datetime.now()
			p = subprocess.Popen(CollectFinalResultsCommand, shell=True)
			p.wait()
			p = subprocess.Popen(ReplaceVariablesWithFinalResultsCommand, shell=True)
			p.wait()
			operationEnd = datetime.now()
			print("Results in equations replaced: {0}\n".format(str(operationEnd - operationStart)))
		os.system("rm MergedResults")
	os.system("rm InputEquations")
	os.system("rm InputEquationsSplit")
	os.system("rm UndeterminedResults")
	end = datetime.now()
	print('Execution time is {0}'.format(str(end - start)))


def getFinalResultsCount(resultsFile):
	resultsFile = open(resultsFile, 'r')
	count = 0
	for resultLine in resultsFile:
		blockIndex, resultIndex, resultSymbol, result = resultLine.strip().split('\t')
		if checkIfResultReady(result):
			count += 1
	return count


def getBlocksCount(splitEquationsFile):
	splitEquationsFile = open(splitEquationsFile, 'r')
	partIndex = 0
	lineCount = 0
	for equationLine in splitEquationsFile:
		lineCount += 1
		partIndex, equationIndex, equation = equationLine.strip().split('\t')
	if lineCount == 0:
		return 0
	else:
		return int(partIndex) + 1


def mapInitData():
	for equation in sys.stdin:
		equationIndex, equation = equation.strip().split('\t')
		print('{0}\t{1}'.format(equationIndex, equation))


def mapEquationsToNodes():
	previousLeftBlockRegion = -1
	previousRightBlockRegion = -1
	equationCount = 0
	partIndex = 0
	equationInPartIndex = 0
	for equation in sys.stdin:
		equationCount += 1
		number, equation = equation.strip().split('\t')
		variablesCount, indexesBySymbols, symbolsByIndexes = processEquationSymbols(equation)
		equationCoefficients = getEquationCoefficients(equation, indexesBySymbols, symbolsByIndexes)
		equationLen = len(equationCoefficients)
		rightColumnIndex = equationLen - 1
		leftColumnIndex = 0

		while equationCoefficients[leftColumnIndex] != 1 and leftColumnIndex < equationLen:
			leftColumnIndex += 1
		while equationCoefficients[rightColumnIndex] != 1 and rightColumnIndex > 0:
			rightColumnIndex -= 1

		if previousLeftBlockRegion != leftColumnIndex or previousRightBlockRegion != rightColumnIndex:
			if equationInPartIndex > 0:
				partIndex += 1
				equationInPartIndex = 0
			previousLeftBlockRegion = leftColumnIndex
			previousRightBlockRegion = rightColumnIndex
		print('{0}\t{1}\t{2}'.format(str(partIndex), equationInPartIndex, equation))
		equationInPartIndex += 1


def computeEquationPart():
	equations = []
	index = 0
	for equationLine in sys.stdin:
		index, indexInPart, equation = equationLine.strip().split('\t')
		equations.append(equation)
	# compute variables to find
	variablesToFind = []
	symbolsSet = set()
	for equation in equations:
		symbols = getSymbolsList(equation)
		for symbol in symbols:
			symbolsSet.add(symbol)
	varCount, indexesBySymbols, symbolsByIndexes = processSymbols(equations)
	indexes = list([indexesBySymbols.get(symbol) for symbol in symbolsSet])
	indexes.sort()
	for i in range(len(indexes)):
		variablesToFind.append(symbolsByIndexes.get(indexes[-1]))
		indexes.pop()
	# compute equations part
	variables = solve(equations, variablesToFind, rational=True, quick=True, minimal=True, simplify=False)
	if len(variables) > 0:
		finalResults = {}
		for variable in variables:
			strValue = str(variables[variable])
			if checkIfResultReady(strValue):
				finalResults[str(variable)] = strValue
		tempResults = dict((str(key), value) for key, value in variables.items())

		# simplify equation result
		resultKeys = sortSymbols(list(tempResults.keys()), indexesBySymbols, symbolsByIndexes)
		for variableToReplace in resultKeys:
			for variableWhichReplace in resultKeys:
				if variableToReplace != variableWhichReplace:
					newValue = '(' + str(tempResults[variableToReplace]) + ')'
					originalEquation = str(tempResults[variableWhichReplace])
					symbols = list(getSymbolsList(originalEquation))
					if symbols.__contains__(variableToReplace):
						simplifiedResult = simplify((tempResults(originalEquation, variableToReplace, newValue)))
						if not isinstance(simplifiedResult, numbers.Zero):
							tempResults[variableWhichReplace] = simplifiedResult

		results = dict((key, tempResults[str(key)]) for key in variables.keys())
		results = dict(list(finalResults.items()) + list(results.items()))
		for result in results.keys():
			print('{0}\t{1}\t{2}'.format(str(index), str(result), str(results[result])))


def mergeResults():
	for result in sys.stdin:
		block, resultKey, resultValue = result.strip().split('\t')
		index = str(getSymbolIndex(resultKey))
		print('{0}\t{1}\t{2}\t{3}'.format(block, index, resultKey, resultValue))


def grabFinalResults():
	for result in sys.stdin:
		block, index, resultKey, resultValue = result.strip().split('\t')
		if checkIfResultReady(resultValue):
			print('{0}\t{1}\t{2}\t{3}'.format("-1", index, resultKey, resultValue))


def replaceVariablesWithResults():
	results = {}
	for line in sys.stdin:
		splits = line.strip().split('\t')
		if len(splits) != 2:
			resultKey = splits[2]
			resultValue = splits[3]
			results[resultKey] = resultValue
		else:
			equationIndex = splits[0]
			equation = splits[1]
			for resultKey in results.keys():
				equation = replaceSymbol(equation, resultKey, results[resultKey])
			simplifiedEquation = simplify(equation)
			if not isinstance(simplifiedEquation, numbers.Zero):
				print('{0}\t{1}'.format(equationIndex, simplifiedEquation))


def mergeSimplificationEquations():
	equationIndex = 0
	for result in sys.stdin:
		splits = result.strip().split('\t')
		#we got equation
		if len(splits) == 3:
			equation = splits[2]
			print('{0}\t{1}'.format(equationIndex, equation))
			equationIndex += 1


def mergeSimplificationUndeterminedResults():
	for result in sys.stdin:
		splits = result.strip().split('\t')
		#we got undetermined result
		if len(splits) == 2:
			symbol = splits[0]
			result = splits[1]
			print('{0}\t{1}'.format(symbol, result))


def mapResultForSimplification(blocksCount):
	for resultLine in sys.stdin:
		resultBlock, index, symbol, result = resultLine.strip().split('\t')
		for block in range(int(blocksCount)):
			print('{0}\t{1}\t{2}\t{3}'.format(block, index, symbol, result))


def joinEquationsWithResultForSimplificationMap():
	for line in sys.stdin:
		line = line.strip()
		splits = line.split('\t')
		block = "-1"
		indexEq = "-1"
		equation = "-1"
		indexR = "-1"
		symbolR = "-1"
		result = "-1"
		_indexR = "-1"
		_symbolR = "-1"
		_result = "-1"
		#we got equations with block results
		if len(splits) == 6:
			block = splits[0]
			indexEq = splits[1]
			equation = splits[2]
			indexR = splits[3]
			symbolR = splits[4]
			result = splits[5]
		#we got item from all results
		elif len(splits) == 4:
			block = splits[0]
			_indexR = splits[1]
			_symbolR = splits[2]
			_result = splits[3]
		print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}'.format(block, indexEq, equation, indexR, symbolR, result,
																   _indexR, _symbolR, _result))


def joinEquationsWithResultForSimplificationReduce():
	currentIndexEq = "-1"
	currentEq = ""
	currentIndexR = ""
	currentSymbolR = ""
	currentResult = ""

	_currentIndexR = "-1"
	_currentSymbolR = ""
	_currentResult = ""
	for line in sys.stdin:
		line = line.strip()
		block, indexEq, equation, indexR, symbolR, result, _indexR, _symbolR, _result = line.split('\t')
		if indexEq != "-1":
			currentIndexEq = indexEq
			currentEq = equation
			currentIndexR = indexR
			currentSymbolR = symbolR
			currentResult = result
		elif _indexR != "-1":
			_currentIndexR = _indexR
			_currentSymbolR = _symbolR
			_currentResult = _result

		if currentIndexEq != "-1" and _currentIndexR != "-1":
			print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}'.format(block, _currentIndexR, currentIndexEq, currentEq,
																	   currentIndexR, currentSymbolR, currentResult,
																	   _currentSymbolR, _currentResult))


def joinResultsWithEquationsMap():
	for line in sys.stdin:
		line = line.strip()
		splits = line.split('\t')
		indexEq = "-1"
		equation = "-1"
		indexR = "-1"
		symbolR = "-1"
		result = "-1"
		#we got equation
		if len(splits) == 3:
			block, indexEq, equation = splits
		#we got result
		else:
			block, indexR, symbolR, result = splits
		print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(block, indexEq, equation, indexR, symbolR, result))


def joinResultsWithEquationsReduce():
	currentIndexEq = "-1"
	currentEq = ""

	currentIndexR = "-1"
	currentSymbolR = ""
	currentResult = ""
	for line in sys.stdin:
		line = line.strip()
		block, indexEq, equation, indexR, symbolR, result = line.split('\t')
		if indexEq != "-1":
			currentIndexEq = indexEq
			currentEq = equation
		elif indexR != "-1":
			currentIndexR = indexR
			currentSymbolR = symbolR
			currentResult = result

		if currentIndexEq != "-1" and currentIndexR != "-1":
			print('{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(block, currentIndexEq, currentEq, currentIndexR, currentSymbolR, currentResult))


def simplifyEquations():
	blockResults = {}
	blockEquations = {}
	indexesBySymbols = {}
	symbolsByIndexes = {}
	simplifiedEquationResults = {}
	for line in sys.stdin:
		splits = line.split('\t')
		block = int(splits[0])
		indexEq = int(splits[2])
		equation = splits[3]
		symbolR = splits[5]
		result = splits[6]

		_indexR = int(splits[1])
		_symbolR = splits[7]
		_result = splits[8]
		blockEquations[indexEq] = equation
		blockResults[symbolR] = result
		simplifiedEquationResults[_symbolR] = _result
		indexesBySymbols[_symbolR] = _indexR
		symbolsByIndexes[_indexR] = _symbolR
	if len(blockEquations) > 0:
		undeterminedCount = 0
		equationIndexes = list(blockEquations.keys())
		equationIndexes.sort()
		resultKeys = sortSymbols(list(simplifiedEquationResults.keys()), indexesBySymbols, symbolsByIndexes)
		for equationIndex in equationIndexes:
			strReplacedEquation = blockEquations[equationIndex]
			for resultKey in resultKeys:
				newValue = '(' + simplifiedEquationResults[resultKey] + ')'
				symbols = list(getSymbolsList(strReplacedEquation))
				if symbols.__contains__(resultKey):
					strReplacedEquation = replaceSymbol(strReplacedEquation, resultKey, newValue)
			replacedEquation = simplify(strReplacedEquation)
			if not isinstance(replacedEquation, numbers.Zero):
				blockEquations[equationIndex] = str(replacedEquation)
				print("{0}\t{1}\t{2}".format(block, equationIndex, blockEquations[equationIndex]))
			else:
				undeterminedCount += 1
		if undeterminedCount == len(blockEquations):
			for key in blockResults.keys():
				print("{0}\t{1}\t{2}\t{3}".format(block, getSymbolIndex(key), key, blockResults[key]))


# Gets symbol index
def getSymbolIndex(symbol):
	return int(re.search('(?<=f\(x_)(.*)(?=\))', symbol).group())


# Gets symbols list from equation
def getSymbolsList(expr):
	return re.findall('f\\(.*?\\)', expr)


# Replaces one symbol by another one
def replaceSymbol(expr, original, replace):
	regex = re.compile(re.escape(original))
	return regex.sub(replace, expr)


# Check if expression has some symbols, if not then result is ready
def checkIfResultReady(expr):
	regex = 'f\\(.*?\\)'
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


# Build and returns equation matrix from symbolic equations
def getEquationCoefficients(equation, indexesBySymbols, symbolsByIndexes):
	indexes = list(symbolsByIndexes.keys())
	maxIndex = max(indexes)
	minIndex = min(indexes)

	rowCoefficients = []
	for j in range(maxIndex - minIndex + 1):
		rowCoefficients.append(0)
	equationSymbols = set(getSymbolsList(equation))
	equationIndexes = [indexesBySymbols.get(symbol) for symbol in equationSymbols]
	for j in range(len(indexes)):
		if equationIndexes.__contains__(indexes[j]):
			rowCoefficients[indexes[j] - minIndex] = 1
		else:
			rowCoefficients[indexes[j] - minIndex] = 0
	return rowCoefficients


# Build and returns counts of all symbols, dictionaries of symbolsByIndexes and indexesBySymbols,
def processEquationSymbols(equation):
	symbols = set(getSymbolsList(equation))
	symbolsList = list(symbols)
	indexesList = list(map(lambda symbol: getSymbolIndex(symbol), symbolsList))
	return len(symbolsList), dict(zip(symbolsList, indexesList)), dict(zip(indexesList, symbolsList))


#Simplifies results from equations
def simplifyEquationResults(results, indexesBySymbols, symbolsByIndexes):
	resultKeys = sortSymbols(list(results.keys()), indexesBySymbols, symbolsByIndexes)
	notSimplifiedResults = []
	for originalKey in resultKeys:
		for keyToReplace in resultKeys:
			if originalKey != keyToReplace:
				newValue = '(' + str(results[originalKey]) + ')'
				originalEquation = str(results[keyToReplace])
				symbols = list(getSymbolsList(originalEquation))
				if symbols.__contains__(originalKey):
					results[keyToReplace] = replaceSymbol(originalEquation, originalKey, newValue)
					notSimplifiedResults.append(keyToReplace)

	for key in resultKeys:
		if notSimplifiedResults.__contains__(key):
			results[key] = simplify(results[key])

	return results


if __name__ == "__main__":
	if sys.argv[1] == "HadoopSimulation":
		hadoopSimulation(sys.argv[2:])
	elif sys.argv[1] == "mapInitData":
		mapInitData()
	elif sys.argv[1] == "mapEquationsToNodes":
		mapEquationsToNodes()
	elif sys.argv[1] == "computeEquationPart":
		computeEquationPart()
	elif sys.argv[1] == "mergeResults":
		mergeResults()
	elif sys.argv[1] == "mapResultForSimplification":
		mapResultForSimplification(sys.argv[2])
	elif sys.argv[1] == "joinResultsWithEquationsMap":
		joinResultsWithEquationsMap()
	elif sys.argv[1] == "joinResultsWithEquationsReduce":
		joinResultsWithEquationsReduce()
	elif sys.argv[1] == "joinEquationsWithResultForSimplificationMap":
		joinEquationsWithResultForSimplificationMap()
	elif sys.argv[1] == "joinEquationsWithResultForSimplificationReduce":
		joinEquationsWithResultForSimplificationReduce()
	elif sys.argv[1] == "simplifyEquations":
		simplifyEquations()
	elif sys.argv[1] == "mergeSimplificationEquations":
		mergeSimplificationEquations()
	elif sys.argv[1] == "mergeSimplificationUndeterminedResults":
		mergeSimplificationUndeterminedResults()
	elif sys.argv[1] == "grabFinalResults":
		grabFinalResults()
	elif sys.argv[1] == "replaceVariablesWithResults":
		replaceVariablesWithResults()

