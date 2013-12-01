#!/usr/bin/env python3.3

import sys

from glob import glob
from Jobs.Utils import *
from sympy import Symbol


class SerializeSymbolsJob:

	def map(self):
		return

	def reduce(self, debug=False, inputFilename=None, outputFilename=None):
		output = None
		if debug:
			inputList = [open(filename, "r") for filename in glob(inputFilename)]
			output = open(outputFilename, 'w')
		else:
			inputList = [sys.stdin]

		strSymbols = set()
		for input in inputList:
			for equation in input:
				equationIndex, equation = equation.strip().split('\t')
				symbolsList = getSymbolsList(equation)
				[strSymbols.add(symbol) for symbol in symbolsList]
		#sort symbols by indexes
		symbolPairs = [(getSymbolIndex(symbol), symbol) for symbol in strSymbols]
		symbolsByIndexes = dict((symbol, index) for symbol, index in symbolPairs)
		indexesList = [index for index in symbolsByIndexes.keys()]
		indexesList.sort()
		sortedSymbols = [Symbol(symbolsByIndexes.get(index)) for index in indexesList]
		if output is not None:
			output.write("-1\t{0}\n".format(encodeExpression(sortedSymbols)))
		else:
			print("-1\t{0}".format(encodeExpression(sortedSymbols)))

		if debug:
			input.close()
		if output is not None:
			output.close()


if __name__ == "__main__":
	Job = SerializeSymbolsJob()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		if len(sys.argv[2:]) > 0:
			Job.reduce(debug=sys.argv[2], inputFilename=sys.argv[3], outputFilename=sys.argv[4])
		else:
			Job.reduce()