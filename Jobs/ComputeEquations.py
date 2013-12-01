#!/usr/bin/env python3.3

import sys
from glob import glob
from sympy import Poly
from sympy.core import numbers
from sympy.solvers import solve
from Jobs.Utils import *


class ComputationJob:
	def map(self):
		return

	def reduce(self, reducerNumber, debug=False, inputFilename=None, outputFilename=None):
		variablesToFind = []
		equations = []
		symbolsSet = set()
		output = None
		if debug:
			inputList = [open(filename, "r") for filename in glob(inputFilename)]
			output = open(outputFilename, 'w')
		else:
			inputList = [sys.stdin]

		for input in inputList:
			for line in input:
				blockNumber, indexInPart, strEquation = line.strip().split('\t')
				if not debug or blockNumber == str(reducerNumber):
					equation, symbols = decodeExpression(strEquation)

					[symbolsSet.add(symbol) for symbol in equation.free_symbols]

					equation = Poly(equation, symbols)
					equations.append(equation)

			if debug:
				input.close()
		symbolsList = list(symbolsSet)
		symbolPairs = [(getSymbolIndex(str(symbol)), symbol) for symbol in symbolsList]
		symbolsByIndexes = dict((symbol, index) for symbol, index in symbolPairs)
		indexesBySymbols = dict((index, symbol) for symbol, index in symbolPairs)
		indexes = list([indexesBySymbols.get(symbol) for symbol in symbolsList])
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
					finalResults[variable] = strValue
			tempResults = {}
			for variableKey in variables.keys():
				tempResults[variableKey] = variables[variableKey]

			# simplify equation result
			indexes = [indexesBySymbols.get(symbol) for symbol in list(tempResults.keys())]
			indexes.sort()
			resultKeys = [symbolsByIndexes.get(index) for index in indexes]
			for variableToReplace in resultKeys:
				for variableWhichReplace in resultKeys:
					if variableToReplace != variableWhichReplace:
						if tempResults[variableWhichReplace].has(variableToReplace):
							simplifiedResult = tempResults[variableWhichReplace].subs(variableToReplace, tempResults[variableToReplace])
							if not isinstance(simplifiedResult, numbers.Zero):
								tempResults[variableWhichReplace] = simplifiedResult
			results = {}
			for variableKey in tempResults.keys():
				if tempResults[variableKey].is_Poly:
					results[variableKey] = tempResults[variableKey].args[0]
				else:
					results[variableKey] = tempResults[variableKey]
			results = dict(list(finalResults.items()) + list(results.items()))
			for result in results.keys():
				if result in finalResults:
					if output is not None:
						output.write('{0}\t{1}\t{2}\n'.format(getSymbolIndex(str(result)), encodeExpression(result),
															  encodeExpression(results[result])))
					else:
						print('{0}\t{1}\t{2}\n'.format(getSymbolIndex(str(result)), encodeExpression(result),
													   encodeExpression(results[result])))
				else:
					if output is not None:
						output.write('{0}\t{1}\t{2}\t{3}\n'.format(str(reducerNumber), getSymbolIndex(str(result)),
																   encodeExpression(result), encodeExpression(results[result])))
					else:
						print('{0}\t{1}\t{2}\t{3}'.format(str(reducerNumber), getSymbolIndex(str(result)),
														  encodeExpression(result), encodeExpression(results[result])))
		if output is not None:
			output.close()


if __name__ == "__main__":
	Job = ComputationJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		if len(sys.argv[2:]) > 1:
			Job.reduce(reducerNumber=sys.argv[2], debug=sys.argv[3], inputFilename=sys.argv[4], outputFilename=sys.argv[5])
		else:
			Job.reduce(reducerNumber=sys.argv[2])