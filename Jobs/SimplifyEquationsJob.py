#!/usr/bin/env python3.3

import sys

from sympy.core import numbers
from sympy import expand

from Jobs.Utils import *


class SimplifyEquationsJob:
	def map(self):
		return

	def reduce(self):
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
				replacedEquation = expand(strReplacedEquation, power_exp=False, log=False)
				if not isinstance(replacedEquation, numbers.Zero):
					blockEquations[equationIndex] = str(replacedEquation)
					print("{0}\t{1}\t{2}".format(block, equationIndex, blockEquations[equationIndex]))
				else:
					undeterminedCount += 1
			if undeterminedCount == len(blockEquations):
				for key in blockResults.keys():
					print("{0}\t{1}\t{2}\t{3}".format(block, getSymbolIndex(key), key, blockResults[key]))


if __name__ == "__main__":
	Job = SimplifyEquationsJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		Job.reduce()