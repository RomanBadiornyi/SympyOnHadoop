#!/usr/bin/env python3.3

import sys

from glob import glob
from sympy.core import numbers

from Jobs.Utils import *


class SimplifyEquationsJob:

	def map(self, debug=False, inputFilename=None, secondInputFilename=None, thirdInputFilename=None, outputFilename=None):
		output = None
		if debug:
			inputList = [open(inputFilename, 'r')]

			[inputList.append(open(filename, "r")) for filename in glob(secondInputFilename)]

			inputList.append(open(thirdInputFilename, 'r'))
			output = open(outputFilename, 'w')
		else:
			inputList = [sys.stdin]

		for input in inputList:
			for line in input:
				splits = line.strip().split("\t")
				#got equation
				if len(splits) == 3:
					if output is not None:
						output.write("{0}\t{1}\t{2}\t{3}\n".format(splits[0], '1', splits[1], splits[2]))
					else:
						print("{0}\t{1}\t{2}\t{3}".format(splits[0], '1', splits[1], splits[2]))
				#got block result
				elif len(splits) == 4:
					if output is not None:
						output.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(splits[0], '2', splits[1], splits[2],
																		splits[3]))
					else:
						print("{0}\t{1}\t{2}\t{3}\t{4}".format(splits[0], '2', splits[1], splits[2], splits[3]))
				#got prepared for simplification result
				elif len(splits) == 5:
					if output is not None:
						output.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(splits[1], splits[0], splits[2], splits[3],
																		splits[4]))
					else:
						print("{0}\t{1}\t{2}\t{3}\t{4}".format(splits[1], splits[0], splits[2], splits[3],
															   splits[4]))

	def reduce(self, reducerNumber, debug=False, inputFilename=None, outputFilename=None):
		output = None
		if debug:
			inputList = [open(filename, "r") for filename in glob(inputFilename)]
			output = open(outputFilename, 'w')
		else:
			inputList = [sys.stdin]

		blockResults = {}
		blockEquations = {}
		equationIndexes = []
		undeterminedCount = 0
		sorted = False
		equationSymbols = []
		for input in inputList:
			for line in input:
				splits = line.split('\t')
				#got equation
				if splits[1] == '1':
					block, dummy, equationIndex, encodedEquation = splits
					if not debug or block == str(reducerNumber):
						equation, equationSymbols = decodeExpression(encodedEquation)
						blockEquations[int(equationIndex)] = equation
				#got block result
				elif splits[1] == '2':
					block, dummy, resultIndex, encodedSymbol, encodedResult = splits
					if not debug or block == str(reducerNumber):
						blockResults[decodeExpression(encodedSymbol)] = encodedResult
				#got prepared for simplification result
				elif len(splits) == 5:
					block, dummy, resultIndex, encodedSymbol, encodedResult = splits
					if not debug or block == str(reducerNumber):
						symbol = decodeExpression(encodedSymbol)
						result = decodeExpression(encodedResult)
						if len(blockEquations) > 0:
							if not sorted:
								equationIndexes = list(blockEquations.keys())
								equationIndexes.sort()
								sorted = True
							for equationIndex in equationIndexes:
								equation = blockEquations[equationIndex]
								if equation.has(symbol):
									equation = equation.subs(symbol, result)
									if not isinstance(equation, numbers.Zero):
										blockEquations[equationIndex] = equation
									else:
										undeterminedCount += 1
		if undeterminedCount == len(blockEquations):
			for key in blockResults.keys():
				if output is not None:
					output.write("{0}\t{1}\t{2}\t{3}\n".format(block, getSymbolIndex(str(key)),
															   encodeExpression(key), blockResults[key]))
				else:
					print("{0}\t{1}\t{2}\t{3}".format(block, getSymbolIndex(str(key)),
													  encodeExpression(key), blockResults[key]))
		else:
			for equationIndex in equationIndexes:
				if output is not None:
					output.write("{0}\t{1}\t{2}\n".format(block, equationIndex,
														  encodeExpression((blockEquations[equationIndex], equationSymbols))))
				else:
					print("{0}\t{1}\t{2}".format(block, equationIndex,
												 encodeExpression((blockEquations[equationIndex], equationSymbols))))
		if debug:
			input.close()
		if output is not None:
			output.close()


if __name__ == "__main__":
	Job = SimplifyEquationsJob()
	if sys.argv[1] == "map":
		if len(sys.argv[2:]) > 0:
			Job.map(debug=sys.argv[2], inputFilename=sys.argv[3], secondInputFilename=sys.argv[4],
					thirdInputFilename=sys.argv[4], outputFilename=sys.argv[5])
		else:
			Job.map()
	elif sys.argv[1] == "reduce":
		if len(sys.argv[2:]) > 1:
			Job.reduce(reducerNumber=sys.argv[2], debug=sys.argv[3], inputFilename=sys.argv[4],
					   outputFilename=sys.argv[5])
		else:
			Job.reduce(reducerNumber=sys.argv[2])