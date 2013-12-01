#!/usr/bin/env python3.3

import sys
import base64
import pickle

from Jobs.Utils import *
from sympy import Symbol
from sympy.core import numbers
from sympy.solvers import solve


class ComputationJob:
	def map(self):
		return

	def reduce(self, reducerNumber, debug=False, inputFilename=None, outputFilename=None):
		index = 0
		variablesToFind = []
		equations = []
		symbols = set()
		output = None
		if debug:
			input = open(inputFilename, 'r')
			output = open(outputFilename, 'w')
		else:
			input = sys.stdin

		for line in input:
			index, indexInPart, strEquation = line.strip().split('\t')
			if not debug or index == str(reducerNumber):
				equation = pickle.loads(base64.b64decode(strEquation.encode("latin1")))
				equations.append(equation)
				[symbols.add(symbol) for symbol in list(equation.free_symbols)]

		symbols = list(symbols)
		symbolPairs = [(getSymbolIndex(str(symbol)), symbol) for symbol in symbols]
		symbolsByIndexes = dict((symbol, index) for symbol, index in symbolPairs)
		indexesBySymbols = dict((index, symbol) for symbol, index in symbolPairs)
		indexes = list([indexesBySymbols.get(symbol) for symbol in symbols])
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
			tempResults = {}
			for variableKey in variables.keys():
				if not variables[variableKey].is_Number:
					tempResults[variableKey] = variables[variableKey].as_poly()
				else:
					tempResults[variableKey] = variables[variableKey]

			# simplify equation result
			indexes = [indexesBySymbols.get(symbol) for symbol in list(tempResults.keys())]
			indexes.sort()
			resultKeys = [symbolsByIndexes.get(index) for index in indexes]
			for variableToReplace in resultKeys:
				for variableWhichReplace in resultKeys:
					if variableToReplace != variableWhichReplace:
						if tempResults[variableWhichReplace].has(variableToReplace):
							simplifiedResult = tempResults[variableWhichReplace].replace(variableToReplace, tempResults[variableToReplace])
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
				if output is not None:
					output.write('{0}\t{1}\t{2}\n'.format(str(index), str(result), str(results[result])))
				else:
					print('{0}\t{1}\t{2}'.format(str(index), str(result), str(results[result])))
		if debug:
			input.close()
		if output is not None:
			output.close()


if __name__ == "__main__":
	Job = ComputationJob()
	if sys.argv[1] == "map":
		Job.map(sys.argv[2:])
	elif sys.argv[1] == "reduce":
		Job.reduce(sys.argv[2:])