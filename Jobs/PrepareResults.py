#!/usr/bin/env python3.3

import sys
from glob import glob
from Jobs.Utils import getSymbolIndex
from Jobs.Utils import decodeExpression


class PrepareForSimplification:

	def map(self, blocksCount, debug=False, inputFilename=False, outputFilename=False):
		output = None
		if debug:
			inputList = [open(filename, "r") for filename in glob(inputFilename)]
			output = open(outputFilename, 'w')
		else:
			inputList = [sys.stdin]

		for input in inputList:
			for resultLine in input:
				resultBlock, symbol, result = resultLine.strip().split('\t')
				symbol = decodeExpression(symbol)
				index = getSymbolIndex(str(symbol))
				for block in range(int(blocksCount)):
					if output is not None:
						output.write('{0}\t{1}\t{2}\t{3}\n'.format(block, index, symbol, result))
					else:
						print('{0}\t{1}\t{2}\t{3}'.format(block, index, symbol, result))
			if debug:
				input.close()
		if output is not None:
			output.close()

	def reduce(self):
		return

if __name__ == "__main__":
	Job = PrepareForSimplification()
	if sys.argv[1] == "map":
		Job.map(sys.argv[2:])
	elif sys.argv[1] == "reduce":
		Job.reduce()