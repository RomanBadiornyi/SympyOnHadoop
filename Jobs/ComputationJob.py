#!/usr/bin/env python3.3

import sys

from sympy.solvers import solve
from sympy import expand
from sympy import Equality
from sympy.core import numbers

from Jobs.Utils import *
from sympy import Symbol


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
		index = 0
		variablesToFind = []
		equations = []
		expressions = []
		symbols = set()
		for line in sys.stdin:
			index, indexInPart, equation = line.strip().split('\t')
			strEqSymbols = getSymbolsList(equation)
			expressions.append(expand(equation, power_exp=False, power_base=False, log=False))
			[symbols.add(symbol) for symbol in strEqSymbols]

			symbolPairs = [(getSymbolIndex(symbol), symbol) for symbol in symbols]
			symbolsByIndexes = dict((symbol, index) for symbol, index in symbolPairs)
			indexesBySymbols = dict((index, symbol) for symbol, index in symbolPairs)

		indexes = list([indexesBySymbols.get(symbol) for symbol in symbols])
		indexes.sort()
		for i in range(len(indexes)):
			variablesToFind.append(symbolsByIndexes.get(indexes[-1]))
			indexes.pop()
		while len(expressions) > 0:
			equation = Equality(expressions[0], 0, variablesToFind)
			equations.append(equation)
			del expressions[0]

		# compute equations part
		variables = solve(equations, variablesToFind, rational=True, quick=True, minimal=True, simplify=False)
		if len(variables) > 0:
			finalResults = {}
			for variable in variables:
				strValue = str(variables[variable])
				if checkIfResultReady(strValue):
					finalResults[str(variable)] = strValue
			tempResults = {}
			for variableKey in variables.keys():
				if not variables[variableKey].is_Number:
					tempResults[str(variableKey)] = variables[variableKey].as_poly()
				else:
					tempResults[str(variableKey)] = variables[variableKey]

			# simplify equation result
			resultKeys = sortSymbols(list(tempResults.keys()), indexesBySymbols, symbolsByIndexes)
			for variableToReplace in resultKeys:
				for variableWhichReplace in resultKeys:
					if variableToReplace != variableWhichReplace:
						if tempResults[variableWhichReplace].has(Symbol(variableToReplace)):
							simplifiedResult = tempResults[variableWhichReplace].replace(Symbol(variableToReplace), tempResults[variableToReplace])
							if not isinstance(simplifiedResult, numbers.Zero):
								tempResults[variableWhichReplace] = simplifiedResult
			results = {}
			for variableKey in tempResults.keys():
				if tempResults[variableKey].is_Poly:
					results[str(variableKey)] = tempResults[variableKey].args[0]
				else:
					results[str(variableKey)] = tempResults[variableKey]
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