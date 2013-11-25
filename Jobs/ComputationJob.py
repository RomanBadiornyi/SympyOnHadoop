#!/usr/bin/env python3.3

import sys

from sympy.solvers import solve
from sympy import expand

from Jobs.Utils import *


class ComputationJob:
	def map(self):
		previousLeftBlockRegion = -1
		previousRightBlockRegion = -1
		equationCount = 0
		partIndex = 0
		equationInPartIndex = 0
		for equation in sys.stdin:
			equationCount += 1
			number, equation = equation.strip().split('\t')
			variablesCount, indexesBySymbols, symbolsByIndexes = self.processEquationSymbols(equation)
			equationCoefficients = self.getEquationCoefficients(equation, indexesBySymbols, symbolsByIndexes)
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

	def reduce(self):
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
							tempResults[variableWhichReplace] = tempResults(originalEquation, variableToReplace,
																			newValue)
			for variable in resultKeys:
				tempResults[variable] = expand(tempResults[variable], power_exp=False, log=False)

			results = dict((key, tempResults[str(key)]) for key in variables.keys())
			results = dict(list(finalResults.items()) + list(results.items()))
			for result in results.keys():
				print('{0}\t{1}\t{2}'.format(str(index), str(result), str(results[result])))

	# Build and returns equation matrix from symbolic equations
	def getEquationCoefficients(self, equation, indexesBySymbols, symbolsByIndexes):
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
	def processEquationSymbols(self, equation):
		symbols = set(getSymbolsList(equation))
		symbolsList = list(symbols)
		indexesList = list(map(lambda symbol: getSymbolIndex(symbol), symbolsList))
		return len(symbolsList), dict(zip(symbolsList, indexesList)), dict(zip(indexesList, symbolsList))


if __name__ == "__main__":
	Job = ComputationJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()