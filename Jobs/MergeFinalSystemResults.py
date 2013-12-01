#!/usr/bin/env python3.3

import sys
from glob import glob
from Jobs.Utils import *


class MergeFinalSystemResults:
	def map(self):
		return

	def reduce(self, debug=False, inputFilename=None, secondInputFilename=None, outputFilename=None):
		output = None
		if debug:
			inputList = [open(filename, "r") for filename in glob(inputFilename)]
			inputList.append(open(secondInputFilename, "r"))
			output = open(outputFilename, 'w')
		else:
			inputList = [sys.stdin]
		finalResults = {}
		for input in inputList:
			for result in input:
				splits = result.strip().split('\t')
				if len(splits) == 3:
					symbol = decodeExpression(splits[1])
					result = decodeExpression(splits[2])
					index = getSymbolIndex(str(symbol))
					if index not in finalResults.keys() or (index in finalResults.keys() and
																checkIfResultReady(str(result))):
						finalResults[index] = (symbol, result)

		indexes = list(finalResults.keys())
		indexes.sort()
		for index in indexes:
			symbol, result = finalResults[index]
			if output is not None:
				output.write('{0}\t{1}'.format(symbol, result))
			else:
				print('{0}\t{1}'.format(symbol, result))

if __name__ == "__main__":
	Job = MergeFinalSystemResults()
	if sys.argv[1] == "map":
		Job.map()
	elif sys.argv[1] == "reduce":
		if len(sys.argv[2:]) > 0:
			Job.reduce(debug=sys.argv[2], inputFilename=sys.argv[3], secondInputFilename=sys.argv[4],
					   outputFilename=sys.argv[5])
		else:
			Job.reduce()